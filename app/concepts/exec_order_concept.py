"""Query execution order visualization concept."""

from typing import Any

from app.concepts.base import BaseConcept, Step
from app.engine.execution_order import simulate_execution
from app.engine.query_parser import parse_query


class ExecOrderConcept(BaseConcept):
    name = "exec-order"
    display_name = "Execution Order"
    description = "See the logical order MySQL processes query clauses. FROM first, SELECT near the end!"
    difficulty = "beginner"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        parsed = parse_query(query)

        if not parsed.tables:
            return {'error': 'No table specified in query'}

        stages = simulate_execution(parsed, dataset)

        # Build the written order vs execution order comparison
        written_order = self._get_written_order(parsed)
        execution_order = [s.name for s in stages if s.is_active]

        return {
            'query': query,
            'parsed': {
                'type': parsed.query_type,
                'tables': parsed.tables,
                'columns': parsed.columns,
                'where': parsed.where_conditions,
                'group_by': parsed.group_by,
                'having': parsed.having_conditions,
                'order_by': parsed.order_by,
                'limit': parsed.limit
            },
            'stages': [
                {
                    'name': s.name,
                    'sql_clause': s.sql_clause,
                    'description': s.description,
                    'input_rows': s.input_rows,
                    'output_rows': s.output_rows,
                    'sample_data': s.sample_data,
                    'is_active': s.is_active
                }
                for s in stages
            ],
            'written_order': written_order,
            'execution_order': execution_order,
            'misconception': self._get_common_misconception(parsed)
        }

    def _get_written_order(self, parsed) -> list[str]:
        """Get the order clauses appear in written SQL."""
        order = ['SELECT']
        if parsed.tables:
            order.append('FROM')
        if parsed.joins:
            order.append('JOIN')
        if parsed.where_conditions:
            order.append('WHERE')
        if parsed.group_by:
            order.append('GROUP BY')
        if parsed.having_conditions:
            order.append('HAVING')
        if parsed.order_by:
            order.append('ORDER BY')
        if parsed.limit:
            order.append('LIMIT')
        return order

    def _get_common_misconception(self, parsed) -> dict | None:
        """Identify common misconceptions in the query."""
        misconceptions = []

        # WHERE vs HAVING
        if parsed.where_conditions and parsed.group_by:
            misconceptions.append({
                'title': 'WHERE vs HAVING',
                'explanation': 'WHERE filters rows BEFORE grouping. HAVING filters AFTER grouping. Use WHERE for row-level filters, HAVING for aggregate filters.',
                'example': "WHERE salary > 50000 filters individual rows. HAVING COUNT(*) > 5 filters groups."
            })

        # SELECT aliases in WHERE
        if parsed.where_conditions:
            for col in parsed.columns:
                if ' AS ' in col.upper():
                    misconceptions.append({
                        'title': 'Column Aliases',
                        'explanation': "You can't use SELECT aliases in WHERE because WHERE runs BEFORE SELECT!",
                        'example': "SELECT salary * 12 AS annual... WHERE annual > 100000 WON'T WORK"
                    })
                    break

        return misconceptions[0] if misconceptions else None

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        viz_data = self.get_visualization_data(query, dataset)

        if 'error' in viz_data:
            return [Step(
                title="Error",
                description=viz_data['error'],
                highlight={}
            )]

        steps = []

        # Introduction
        steps.append(Step(
            title="Query Written Order",
            description=f"You wrote: {' → '.join(viz_data['written_order'])}",
            highlight={'stage': None}
        ))

        steps.append(Step(
            title="But MySQL Executes...",
            description="In a completely different order! Let's see...",
            highlight={'stage': None}
        ))

        # Walk through each stage
        for stage in viz_data['stages']:
            if stage['is_active']:
                steps.append(Step(
                    title=f"Stage: {stage['name']}",
                    description=f"{stage['sql_clause']} - {stage['description']}",
                    highlight={'stage': stage['name']},
                    data_snapshot={
                        'input': stage['input_rows'],
                        'output': stage['output_rows'],
                        'sample': stage['sample_data']
                    }
                ))

        # Misconception callout
        if viz_data['misconception']:
            steps.append(Step(
                title=f"💡 {viz_data['misconception']['title']}",
                description=viz_data['misconception']['explanation'],
                highlight={'misconception': True}
            ))

        # Summary
        steps.append(Step(
            title="Execution Complete",
            description=f"Actual order: {' → '.join(viz_data['execution_order'])}",
            highlight={'complete': True}
        ))

        return steps

    def get_sample_queries(self) -> list[str]:
        return [
            "SELECT * FROM employees WHERE salary > 50000 ORDER BY name LIMIT 5",
            "SELECT department_id, COUNT(*) FROM employees GROUP BY department_id HAVING COUNT(*) > 2",
            "SELECT name, salary FROM employees WHERE department_id = 1 ORDER BY salary DESC",
            "SELECT * FROM employees ORDER BY hire_date LIMIT 10",
        ]
