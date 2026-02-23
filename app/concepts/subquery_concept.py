"""Subquery execution visualization concept."""

from typing import Any

from app.concepts.base import BaseConcept, Step
from app.engine.query_parser import parse_query


class SubqueryConcept(BaseConcept):
    name = "subqueries"
    display_name = "Subqueries"
    description = "See how nested queries execute. Compare correlated vs non-correlated subqueries and their performance."
    difficulty = "advanced"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        # Detect subquery type
        query_upper = query.upper()
        has_subquery = 'SELECT' in query_upper[query_upper.find('FROM'):]  if 'FROM' in query_upper else False

        subquery_types = self._get_subquery_types()

        # Determine which type based on query
        detected_type = None
        if 'IN (' in query_upper and 'SELECT' in query_upper:
            detected_type = 'in_subquery'
        elif 'EXISTS' in query_upper:
            detected_type = 'exists'
        elif '= (' in query_upper or '> (' in query_upper or '< (' in query_upper:
            detected_type = 'scalar'
        elif 'FROM (' in query_upper:
            detected_type = 'derived'

        # Example execution trace
        execution_examples = {
            'in_subquery': {
                'outer_query': "SELECT * FROM employees WHERE department_id IN (...)",
                'inner_query': "SELECT id FROM departments WHERE budget > 200000",
                'steps': [
                    {'step': 1, 'action': 'Execute inner query first', 'result': 'Returns: [1, 5]'},
                    {'step': 2, 'action': 'Replace subquery with result', 'result': 'WHERE department_id IN (1, 5)'},
                    {'step': 3, 'action': 'Execute outer query', 'result': 'Returns matching employees'},
                ],
                'is_correlated': False
            },
            'exists': {
                'outer_query': "SELECT * FROM employees e WHERE EXISTS (...)",
                'inner_query': "SELECT 1 FROM orders o WHERE o.employee_id = e.id",
                'steps': [
                    {'step': 1, 'action': 'For each employee row...', 'result': 'Start with employee id=1'},
                    {'step': 2, 'action': 'Execute inner query with e.id=1', 'result': 'Check if any orders exist'},
                    {'step': 3, 'action': 'If EXISTS returns true, include row', 'result': 'Employee 1 has orders'},
                    {'step': 4, 'action': 'Repeat for next employee...', 'result': 'Process all employees'},
                ],
                'is_correlated': True
            },
            'scalar': {
                'outer_query': "SELECT name, salary, (...) as avg_sal FROM employees",
                'inner_query': "SELECT AVG(salary) FROM employees",
                'steps': [
                    {'step': 1, 'action': 'Execute scalar subquery once', 'result': 'Returns: 72500'},
                    {'step': 2, 'action': 'Use result in each row', 'result': 'avg_sal = 72500 for all rows'},
                ],
                'is_correlated': False
            },
            'derived': {
                'outer_query': "SELECT * FROM (...) AS dept_stats WHERE avg_salary > 70000",
                'inner_query': "SELECT department_id, AVG(salary) as avg_salary FROM employees GROUP BY department_id",
                'steps': [
                    {'step': 1, 'action': 'Execute derived table query', 'result': 'Creates temporary result set'},
                    {'step': 2, 'action': 'Materialize as "dept_stats"', 'result': 'Temporary table created'},
                    {'step': 3, 'action': 'Execute outer query on derived table', 'result': 'Filter where avg > 70000'},
                ],
                'is_correlated': False
            }
        }

        # Performance comparison
        performance_tips = [
            {
                'pattern': 'Correlated Subquery',
                'issue': 'Executes once PER ROW of outer query - can be very slow!',
                'alternative': 'Consider rewriting as JOIN',
                'example_before': "SELECT * FROM employees e WHERE EXISTS (SELECT 1 FROM orders WHERE employee_id = e.id)",
                'example_after': "SELECT DISTINCT e.* FROM employees e INNER JOIN orders o ON e.id = o.employee_id"
            },
            {
                'pattern': 'IN with large subquery',
                'issue': 'Subquery results loaded into memory',
                'alternative': 'Consider EXISTS or JOIN for large datasets',
                'example_before': "SELECT * FROM orders WHERE customer_id IN (SELECT id FROM customers WHERE country = 'US')",
                'example_after': "SELECT o.* FROM orders o JOIN customers c ON o.customer_id = c.id WHERE c.country = 'US'"
            },
            {
                'pattern': 'Scalar subquery in SELECT',
                'issue': 'May execute once per row if correlated',
                'alternative': 'Use JOIN with aggregation',
                'example_before': "SELECT name, (SELECT AVG(salary) FROM employees e2 WHERE e2.dept_id = e1.dept_id) FROM employees e1",
                'example_after': "SELECT e.name, d.avg_sal FROM employees e JOIN (SELECT dept_id, AVG(salary) avg_sal FROM employees GROUP BY dept_id) d ON e.dept_id = d.dept_id"
            }
        ]

        return {
            'query': query,
            'has_subquery': has_subquery,
            'detected_type': detected_type,
            'subquery_types': subquery_types,
            'execution_example': execution_examples.get(detected_type, execution_examples['in_subquery']),
            'performance_tips': performance_tips
        }

    def _get_subquery_types(self) -> list[dict]:
        return [
            {
                'name': 'Scalar Subquery',
                'description': 'Returns a single value. Used in SELECT or WHERE.',
                'syntax': "SELECT name, (SELECT AVG(salary) FROM employees) as company_avg FROM employees",
                'key_point': 'Must return exactly ONE row and ONE column',
                'icon': '1'
            },
            {
                'name': 'Row Subquery',
                'description': 'Returns a single row with multiple columns.',
                'syntax': "SELECT * FROM t1 WHERE (col1, col2) = (SELECT col1, col2 FROM t2 WHERE id = 1)",
                'key_point': 'Useful for comparing multiple columns at once',
                'icon': '→'
            },
            {
                'name': 'Column Subquery',
                'description': 'Returns multiple rows, single column. Used with IN, ANY, ALL.',
                'syntax': "SELECT * FROM employees WHERE department_id IN (SELECT id FROM departments WHERE budget > 100000)",
                'key_point': 'Common with IN operator',
                'icon': '↓'
            },
            {
                'name': 'Table Subquery (Derived)',
                'description': 'Returns a full result set. Used in FROM clause.',
                'syntax': "SELECT * FROM (SELECT dept, AVG(salary) avg FROM emp GROUP BY dept) AS dept_avgs WHERE avg > 50000",
                'key_point': 'Creates a temporary table that can be queried',
                'icon': '▦'
            },
            {
                'name': 'Correlated Subquery',
                'description': 'References outer query. Executes once per outer row!',
                'syntax': "SELECT * FROM employees e WHERE salary > (SELECT AVG(salary) FROM employees WHERE dept_id = e.dept_id)",
                'key_point': 'Can be slow - consider rewriting as JOIN',
                'icon': '↻'
            },
            {
                'name': 'EXISTS Subquery',
                'description': 'Checks if any rows exist. Returns TRUE/FALSE.',
                'syntax': "SELECT * FROM customers c WHERE EXISTS (SELECT 1 FROM orders WHERE customer_id = c.id)",
                'key_point': 'Stops as soon as one match is found - can be efficient',
                'icon': '?'
            }
        ]

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        viz_data = self.get_visualization_data(query, dataset)

        steps = [
            Step(
                title="Identify Subquery Type",
                description=f"Detected: {viz_data['detected_type'] or 'No subquery found'} subquery",
                highlight={'type': viz_data['detected_type']}
            )
        ]

        if viz_data['detected_type']:
            example = viz_data['execution_example']
            steps.append(Step(
                title="Inner Query" if not example['is_correlated'] else "Outer Query First",
                description=example['inner_query'] if not example['is_correlated'] else example['outer_query'],
                highlight={'query': 'inner'}
            ))

            for exec_step in example['steps']:
                steps.append(Step(
                    title=f"Step {exec_step['step']}",
                    description=f"{exec_step['action']} → {exec_step['result']}",
                    highlight={'step': exec_step['step']}
                ))

            if example['is_correlated']:
                steps.append(Step(
                    title="⚠️ Performance Warning",
                    description="Correlated subquery executes once per row. Consider JOIN alternative!",
                    highlight={'warning': True}
                ))

        return steps

    def get_sample_queries(self) -> list[str]:
        return [
            "SELECT * FROM employees WHERE department_id IN (SELECT id FROM departments WHERE budget > 200000)",
            "SELECT * FROM employees e WHERE EXISTS (SELECT 1 FROM orders WHERE employee_id = e.id)",
            "SELECT name, salary, (SELECT AVG(salary) FROM employees) as avg FROM employees",
            "SELECT * FROM (SELECT department_id, AVG(salary) as avg_sal FROM employees GROUP BY department_id) AS t WHERE avg_sal > 70000",
        ]
