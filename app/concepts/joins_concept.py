"""JOIN visualization concept."""

from typing import Any

from app.concepts.base import BaseConcept, Step
from app.engine.query_parser import parse_query


class JoinsConcept(BaseConcept):
    name = "joins"
    display_name = "JOIN Types"
    description = "Visualize how INNER, LEFT, RIGHT, and CROSS JOINs combine tables. See which rows match and which get NULL."
    difficulty = "beginner"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        parsed = parse_query(query)

        # Get tables involved
        left_table = parsed.tables[0] if parsed.tables else 'employees'
        right_table = parsed.joins[0]['table'] if parsed.joins else 'departments'

        left_data = self._table_to_dicts(dataset.get_table(left_table))
        right_data = self._table_to_dicts(dataset.get_table(right_table))

        # Determine join type
        join_type = 'INNER'
        join_condition = None
        if parsed.joins:
            join_type = parsed.joins[0].get('type', 'INNER')
            join_condition = parsed.joins[0].get('on', '')

        # Parse join condition to find matching columns
        left_col, right_col = self._parse_join_condition(join_condition, left_table, right_table)

        # Perform the join and track matches
        result, match_info = self._perform_join(
            left_data, right_data, left_col, right_col, join_type, left_table, right_table
        )

        return {
            'query': query,
            'join_type': join_type,
            'left_table': {
                'name': left_table,
                'data': left_data[:10],
                'total': len(left_data),
                'columns': list(left_data[0].keys()) if left_data else []
            },
            'right_table': {
                'name': right_table,
                'data': right_data[:10],
                'total': len(right_data),
                'columns': list(right_data[0].keys()) if right_data else []
            },
            'join_condition': {
                'left_col': left_col,
                'right_col': right_col,
                'raw': join_condition
            },
            'result': result[:15],
            'result_total': len(result),
            'match_info': match_info,
            'join_explanations': self._get_join_explanations()
        }

    def _table_to_dicts(self, rows: list) -> list[dict]:
        if not rows:
            return []
        return [vars(row) if hasattr(row, '__dict__') else row.__dict__ for row in rows]

    def _parse_join_condition(self, condition: str, left_table: str, right_table: str) -> tuple[str, str]:
        """Extract column names from join condition."""
        if not condition:
            # Default join on id/foreign key
            if left_table == 'employees' and right_table == 'departments':
                return 'department_id', 'id'
            elif left_table == 'orders' and right_table == 'employees':
                return 'employee_id', 'id'
            return 'id', 'id'

        # Parse "table1.col = table2.col" or "col1 = col2"
        import re
        match = re.search(r'(\w+)\.?(\w+)?\s*=\s*(\w+)\.?(\w+)?', condition, re.IGNORECASE)
        if match:
            left_col = match.group(2) or match.group(1)
            right_col = match.group(4) or match.group(3)
            return left_col.lower(), right_col.lower()

        return 'id', 'id'

    def _perform_join(self, left: list, right: list, left_col: str, right_col: str,
                      join_type: str, left_name: str, right_name: str) -> tuple[list, dict]:
        """Perform join and return results with match tracking."""
        result = []
        left_matched = set()
        right_matched = set()
        match_pairs = []

        # Build right index for faster lookup
        right_index = {}
        for i, r_row in enumerate(right):
            key = r_row.get(right_col)
            if key not in right_index:
                right_index[key] = []
            right_index[key].append((i, r_row))

        # Perform join
        for l_idx, l_row in enumerate(left):
            l_key = l_row.get(left_col)
            matches = right_index.get(l_key, [])

            if matches:
                for r_idx, r_row in matches:
                    left_matched.add(l_idx)
                    right_matched.add(r_idx)
                    match_pairs.append((l_idx, r_idx))

                    combined = {f'{left_name}.{k}': v for k, v in l_row.items()}
                    combined.update({f'{right_name}.{k}': v for k, v in r_row.items()})
                    result.append(combined)
            elif join_type in ('LEFT', 'LEFT OUTER'):
                # Left row with NULL right
                combined = {f'{left_name}.{k}': v for k, v in l_row.items()}
                combined.update({f'{right_name}.{k}': None for k in (right[0].keys() if right else [])})
                result.append(combined)

        # Handle RIGHT JOIN - add unmatched right rows
        if join_type in ('RIGHT', 'RIGHT OUTER'):
            for r_idx, r_row in enumerate(right):
                if r_idx not in right_matched:
                    combined = {f'{left_name}.{k}': None for k in (left[0].keys() if left else [])}
                    combined.update({f'{right_name}.{k}': v for k, v in r_row.items()})
                    result.append(combined)

        # Handle FULL OUTER JOIN
        if join_type in ('FULL', 'FULL OUTER'):
            for r_idx, r_row in enumerate(right):
                if r_idx not in right_matched:
                    combined = {f'{left_name}.{k}': None for k in (left[0].keys() if left else [])}
                    combined.update({f'{right_name}.{k}': v for k, v in r_row.items()})
                    result.append(combined)

        # Handle CROSS JOIN
        if join_type == 'CROSS':
            result = []
            for l_row in left[:5]:  # Limit for visualization
                for r_row in right[:5]:
                    combined = {f'{left_name}.{k}': v for k, v in l_row.items()}
                    combined.update({f'{right_name}.{k}': v for k, v in r_row.items()})
                    result.append(combined)

        match_info = {
            'left_matched': len(left_matched),
            'left_unmatched': len(left) - len(left_matched),
            'right_matched': len(right_matched),
            'right_unmatched': len(right) - len(right_matched),
            'match_pairs': match_pairs[:20],
            'total_result_rows': len(result)
        }

        return result, match_info

    def _get_join_explanations(self) -> dict:
        return {
            'INNER': {
                'title': 'INNER JOIN',
                'description': 'Returns only rows that have matching values in BOTH tables.',
                'use_when': 'You only want records that exist in both tables.',
                'venn': 'intersection'
            },
            'LEFT': {
                'title': 'LEFT JOIN',
                'description': 'Returns ALL rows from left table, and matched rows from right. Unmatched right = NULL.',
                'use_when': 'You want all records from the left table, even if no match exists.',
                'venn': 'left_with_intersection'
            },
            'RIGHT': {
                'title': 'RIGHT JOIN',
                'description': 'Returns ALL rows from right table, and matched rows from left. Unmatched left = NULL.',
                'use_when': 'You want all records from the right table, even if no match exists.',
                'venn': 'right_with_intersection'
            },
            'CROSS': {
                'title': 'CROSS JOIN',
                'description': 'Returns Cartesian product - every row from left paired with every row from right.',
                'use_when': 'You need all possible combinations (rare in practice).',
                'venn': 'cartesian'
            }
        }

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        viz_data = self.get_visualization_data(query, dataset)

        steps = [
            Step(
                title="Load Left Table",
                description=f"Load {viz_data['left_table']['total']} rows from {viz_data['left_table']['name']}",
                highlight={'table': 'left'}
            ),
            Step(
                title="Load Right Table",
                description=f"Load {viz_data['right_table']['total']} rows from {viz_data['right_table']['name']}",
                highlight={'table': 'right'}
            ),
            Step(
                title=f"Apply {viz_data['join_type']} JOIN",
                description=f"Match on {viz_data['join_condition']['left_col']} = {viz_data['join_condition']['right_col']}",
                highlight={'join': True}
            ),
            Step(
                title="Match Results",
                description=f"Found {viz_data['match_info']['left_matched']} left rows matching {viz_data['match_info']['right_matched']} right rows",
                highlight={'matches': True}
            ),
        ]

        join_exp = viz_data['join_explanations'].get(viz_data['join_type'], {})
        if join_exp:
            steps.append(Step(
                title=f"Understanding {viz_data['join_type']} JOIN",
                description=join_exp['description'],
                highlight={'explanation': True}
            ))

        steps.append(Step(
            title="Final Result",
            description=f"Result: {viz_data['result_total']} rows",
            highlight={'result': True}
        ))

        return steps

    def get_sample_queries(self) -> list[str]:
        return [
            "SELECT * FROM employees INNER JOIN departments ON employees.department_id = departments.id",
            "SELECT * FROM employees LEFT JOIN departments ON employees.department_id = departments.id",
            "SELECT * FROM departments RIGHT JOIN employees ON departments.id = employees.department_id",
            "SELECT * FROM employees CROSS JOIN departments",
        ]
