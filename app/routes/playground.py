"""
SQL Playground routes - Interactive query analysis tool.
"""

from flask import Blueprint, render_template, request

from app.engine.dataset import get_dataset
from app.engine.query_analyzer import analyze_query

playground_bp = Blueprint('playground', __name__)


SAMPLE_QUERIES = [
    {
        'name': 'Basic SELECT',
        'query': 'SELECT * FROM employees',
        'category': 'basic'
    },
    {
        'name': 'Filtered Query',
        'query': 'SELECT name, salary FROM employees WHERE department_id = 1',
        'category': 'basic'
    },
    {
        'name': 'JOIN Query',
        'query': 'SELECT e.name, d.name AS department FROM employees e JOIN departments d ON e.department_id = d.id',
        'category': 'join'
    },
    {
        'name': 'Aggregation',
        'query': 'SELECT department_id, AVG(salary) AS avg_salary FROM employees GROUP BY department_id',
        'category': 'aggregate'
    },
    {
        'name': 'Subquery',
        'query': 'SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees)',
        'category': 'subquery'
    },
    {
        'name': 'Anti-pattern: Function on Column',
        'query': "SELECT * FROM orders WHERE YEAR(order_date) = 2023",
        'category': 'antipattern'
    },
    {
        'name': 'Anti-pattern: Leading Wildcard',
        'query': "SELECT * FROM products WHERE name LIKE '%phone%'",
        'category': 'antipattern'
    },
    {
        'name': 'Anti-pattern: SELECT *',
        'query': 'SELECT * FROM employees WHERE salary > 70000 ORDER BY salary DESC',
        'category': 'antipattern'
    },
]


@playground_bp.route('/')
def playground():
    """Render the SQL playground page."""
    dataset = get_dataset()
    schema = dataset.get_schema_info()

    return render_template(
        'playground.html',
        schema=schema,
        sample_queries=SAMPLE_QUERIES
    )


@playground_bp.route('/analyze', methods=['POST'])
def analyze():
    """Analyze a query and return results as HTMX partial."""
    query = request.form.get('query', '').strip()
    dataset = get_dataset()

    analysis = analyze_query(query, dataset)

    return render_template(
        'components/playground_results.html',
        query=query,
        analysis=analysis
    )
