"""WHERE vs HAVING comparison concept."""

from typing import Any

from app.concepts.base import BaseConcept, Step
from app.engine.query_parser import parse_query


class WhereVsHavingConcept(BaseConcept):
    name = "where-having"
    display_name = "WHERE vs HAVING"
    description = "Understand the critical difference: WHERE filters rows BEFORE grouping, HAVING filters AFTER. See it in action!"
    difficulty = "intermediate"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        parsed = parse_query(query)

        if not parsed.tables:
            return {'error': 'No table specified in query'}

        table_name = parsed.tables[0]
        table_data = self._table_to_dicts(dataset.get_table(table_name))

        if not table_data:
            return {'error': f'Table "{table_name}" not found'}

        # Process through each stage
        stages = []

        # Stage 1: Original data
        stages.append({
            'name': 'Original Data',
            'clause': f'FROM {table_name}',
            'data': table_data[:10],
            'row_count': len(table_data),
            'description': f'All {len(table_data)} rows from {table_name}'
        })

        # Stage 2: After WHERE (if present)
        current_data = table_data
        if parsed.where_conditions:
            filtered_data = self._apply_where(current_data, parsed.where_conditions)
            where_str = ' AND '.join([f"{c['column']} {c['op']} {c['value']}" for c in parsed.where_conditions])
            stages.append({
                'name': 'After WHERE',
                'clause': f'WHERE {where_str}',
                'data': filtered_data[:10],
                'row_count': len(filtered_data),
                'removed': len(current_data) - len(filtered_data),
                'description': f'WHERE filters individual rows BEFORE any grouping',
                'highlight': 'where'
            })
            current_data = filtered_data
        else:
            stages.append({
                'name': 'WHERE (not used)',
                'clause': 'No WHERE clause',
                'data': [],
                'row_count': len(current_data),
                'description': 'No row filtering applied',
                'inactive': True
            })

        # Stage 3: After GROUP BY (if present)
        if parsed.group_by:
            grouped_data = self._apply_group_by(current_data, parsed.group_by)
            group_str = ', '.join(parsed.group_by)
            stages.append({
                'name': 'After GROUP BY',
                'clause': f'GROUP BY {group_str}',
                'data': grouped_data[:10],
                'row_count': len(grouped_data),
                'description': f'Rows grouped into {len(grouped_data)} groups',
                'highlight': 'groupby'
            })
            current_data = grouped_data
        else:
            stages.append({
                'name': 'GROUP BY (not used)',
                'clause': 'No GROUP BY clause',
                'data': [],
                'row_count': len(current_data),
                'description': 'No grouping applied',
                'inactive': True
            })

        # Stage 4: After HAVING (if present)
        if parsed.having_conditions:
            before_having = len(current_data)
            filtered_data = self._apply_having(current_data, parsed.having_conditions)
            having_str = str(parsed.having_conditions)
            stages.append({
                'name': 'After HAVING',
                'clause': f'HAVING {having_str}',
                'data': filtered_data[:10],
                'row_count': len(filtered_data),
                'removed': before_having - len(filtered_data),
                'description': f'HAVING filters groups AFTER aggregation',
                'highlight': 'having'
            })
            current_data = filtered_data
        else:
            stages.append({
                'name': 'HAVING (not used)',
                'clause': 'No HAVING clause',
                'data': [],
                'row_count': len(current_data),
                'description': 'No group filtering applied',
                'inactive': True
            })

        # Key differences
        key_differences = [
            {
                'aspect': 'When it runs',
                'where': 'BEFORE GROUP BY',
                'having': 'AFTER GROUP BY'
            },
            {
                'aspect': 'What it filters',
                'where': 'Individual rows',
                'having': 'Grouped results'
            },
            {
                'aspect': 'Can use aggregates?',
                'where': 'NO (SUM, COUNT, etc.)',
                'having': 'YES (required for aggregates)'
            },
            {
                'aspect': 'Performance',
                'where': 'Faster (reduces data early)',
                'having': 'Slower (processes more data)'
            },
        ]

        # Common mistakes
        common_mistakes = [
            {
                'wrong': "SELECT dept, AVG(salary) FROM employees WHERE AVG(salary) > 50000",
                'right': "SELECT dept, AVG(salary) FROM employees GROUP BY dept HAVING AVG(salary) > 50000",
                'explanation': "Can't use AVG() in WHERE - aggregates require HAVING"
            },
            {
                'wrong': "SELECT dept, COUNT(*) FROM employees HAVING salary > 50000",
                'right': "SELECT dept, COUNT(*) FROM employees WHERE salary > 50000 GROUP BY dept",
                'explanation': "Filter individual rows with WHERE, not HAVING"
            }
        ]

        return {
            'query': query,
            'stages': stages,
            'final_count': len(current_data),
            'key_differences': key_differences,
            'common_mistakes': common_mistakes,
            'has_where': bool(parsed.where_conditions),
            'has_having': bool(parsed.having_conditions),
            'has_group_by': bool(parsed.group_by)
        }

    def _table_to_dicts(self, rows: list) -> list[dict]:
        if not rows:
            return []
        return [vars(row) if hasattr(row, '__dict__') else row.__dict__ for row in rows]

    def _apply_where(self, data: list[dict], conditions: list[dict]) -> list[dict]:
        result = []
        for row in data:
            matches = True
            for cond in conditions:
                col = cond['column']
                op = cond['op']
                val = cond['value']
                if col not in row:
                    continue
                row_val = row[col]
                if op == '=' and row_val != val:
                    matches = False
                elif op == '>' and not (row_val > val):
                    matches = False
                elif op == '<' and not (row_val < val):
                    matches = False
                elif op == '>=' and not (row_val >= val):
                    matches = False
                elif op == '<=' and not (row_val <= val):
                    matches = False
            if matches:
                result.append(row)
        return result

    def _apply_group_by(self, data: list[dict], group_cols: list[str]) -> list[dict]:
        groups = {}
        for row in data:
            key = tuple(row.get(col) for col in group_cols)
            if key not in groups:
                groups[key] = []
            groups[key].append(row)

        result = []
        for key, rows in groups.items():
            group_row = {col: key[i] for i, col in enumerate(group_cols)}
            group_row['COUNT(*)'] = len(rows)
            group_row['SUM(salary)'] = sum(r.get('salary', 0) for r in rows)
            group_row['AVG(salary)'] = group_row['SUM(salary)'] / len(rows) if rows else 0
            group_row['_rows'] = rows
            result.append(group_row)
        return result

    def _apply_having(self, data: list[dict], conditions: list[dict]) -> list[dict]:
        result = []
        for row in data:
            matches = True
            for cond in conditions:
                expr = cond.get('expression', '')
                op = cond.get('op', '>')
                val = cond.get('value', 0)

                # Get the value to compare
                if 'COUNT' in expr.upper():
                    row_val = row.get('COUNT(*)', 0)
                elif 'SUM' in expr.upper():
                    row_val = row.get('SUM(salary)', 0)
                elif 'AVG' in expr.upper():
                    row_val = row.get('AVG(salary)', 0)
                else:
                    row_val = row.get(expr, 0)

                if op == '>' and not (row_val > val):
                    matches = False
                elif op == '>=' and not (row_val >= val):
                    matches = False
                elif op == '<' and not (row_val < val):
                    matches = False
                elif op == '<=' and not (row_val <= val):
                    matches = False
                elif op == '=' and row_val != val:
                    matches = False

            if matches:
                result.append(row)
        return result

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        viz_data = self.get_visualization_data(query, dataset)

        if 'error' in viz_data:
            return [Step(title="Error", description=viz_data['error'], highlight={})]

        steps = []
        for stage in viz_data['stages']:
            if not stage.get('inactive'):
                steps.append(Step(
                    title=stage['name'],
                    description=stage['description'],
                    highlight={'stage': stage['name']}
                ))

        # Add key insight
        if viz_data['has_where'] and viz_data['has_having']:
            steps.append(Step(
                title="Key Insight",
                description="WHERE reduced rows BEFORE grouping, HAVING filtered groups AFTER. Both work together!",
                highlight={'insight': True}
            ))
        elif viz_data['has_where']:
            steps.append(Step(
                title="Using WHERE",
                description="WHERE is perfect here - you're filtering individual rows, not aggregates.",
                highlight={'insight': True}
            ))
        elif viz_data['has_having']:
            steps.append(Step(
                title="Using HAVING",
                description="HAVING is needed here to filter based on aggregate values.",
                highlight={'insight': True}
            ))

        return steps

    def get_sample_queries(self) -> list[str]:
        return [
            "SELECT department_id, COUNT(*) FROM employees WHERE salary > 60000 GROUP BY department_id",
            "SELECT department_id, AVG(salary) FROM employees GROUP BY department_id HAVING AVG(salary) > 70000",
            "SELECT department_id, COUNT(*) FROM employees WHERE salary > 50000 GROUP BY department_id HAVING COUNT(*) > 2",
            "SELECT department_id, SUM(salary) FROM employees GROUP BY department_id HAVING SUM(salary) > 200000",
        ]
