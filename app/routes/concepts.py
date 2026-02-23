from flask import Blueprint, render_template, request

from app.concepts import get_concept
from app.engine.dataset import get_dataset
from app.engine.query_executor import QueryExecutor
from app.engine.errors import QueryError

concepts_bp = Blueprint('concepts', __name__)


@concepts_bp.route('/<concept_name>')
def show_concept(concept_name):
    concept = get_concept(concept_name)
    if not concept:
        return "Concept not found", 404

    return render_template(
        'concept_view.html',
        concept=concept,
        dataset=get_dataset()
    )


@concepts_bp.route('/<concept_name>/query', methods=['POST'])
def run_query(concept_name):
    concept = get_concept(concept_name)
    if not concept:
        return "Concept not found", 404

    query = request.form.get('query', '')
    dataset = get_dataset()

    # Execute the query
    query_result = None
    error = None

    if query.strip():
        executor = QueryExecutor(dataset)
        try:
            query_result = executor.execute(query)
        except QueryError as e:
            error = {
                'message': e.message,
                'suggestion': e.suggestion,
                'error_type': e.error_type,
                'context': e.context
            }

    # Get visualization data and steps (even if query failed)
    try:
        viz_data = concept.get_visualization_data(query, dataset)
        steps = concept.get_steps(query, dataset)
    except Exception as e:
        viz_data = {'error': str(e)}
        steps = []

    return render_template(
        f'concepts/{concept_name}.html',
        concept=concept,
        query=query,
        viz_data=viz_data,
        steps=steps,
        current_step=0,
        dataset=dataset,
        query_result=query_result,
        error=error
    )


@concepts_bp.route('/<concept_name>/step/<int:step_num>', methods=['GET'])
def get_step(concept_name, step_num):
    concept = get_concept(concept_name)
    if not concept:
        return "Concept not found", 404

    query = request.args.get('query', '')
    dataset = get_dataset()

    # Re-execute query for results
    query_result = None
    error = None

    if query.strip():
        executor = QueryExecutor(dataset)
        try:
            query_result = executor.execute(query)
        except QueryError as e:
            error = {
                'message': e.message,
                'suggestion': e.suggestion,
                'error_type': e.error_type,
                'context': e.context
            }

    viz_data = concept.get_visualization_data(query, dataset)
    steps = concept.get_steps(query, dataset)

    # Clamp step number
    step_num = max(0, min(step_num, len(steps) - 1)) if steps else 0

    return render_template(
        f'concepts/{concept_name}.html',
        concept=concept,
        query=query,
        viz_data=viz_data,
        steps=steps,
        current_step=step_num,
        dataset=dataset,
        query_result=query_result,
        error=error
    )
