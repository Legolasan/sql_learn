"""EXPLAIN visualization concept."""

from typing import Any

from app.concepts.base import BaseConcept, Step
from app.engine.explain import generate_explain, ExplainRow
from app.engine.query_parser import parse_query


class ExplainConcept(BaseConcept):
    name = "explain"
    display_name = "EXPLAIN Analysis"
    description = "Decode MySQL EXPLAIN output. Understand access types, key usage, and performance implications."
    difficulty = "intermediate"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        parsed = parse_query(query)

        if not parsed.tables:
            return {'error': 'No table specified in query'}

        explain_rows, annotations = generate_explain(parsed, dataset)

        # Group annotations by field
        annotations_by_field = {}
        for ann in annotations:
            if ann.field not in annotations_by_field:
                annotations_by_field[ann.field] = []
            annotations_by_field[ann.field].append({
                'value': ann.value,
                'explanation': ann.explanation,
                'recommendation': ann.recommendation,
                'severity': ann.severity
            })

        return {
            'query': query,
            'parsed': {
                'type': parsed.query_type,
                'tables': parsed.tables,
                'columns': parsed.columns,
                'where': parsed.where_conditions,
                'group_by': parsed.group_by,
                'order_by': parsed.order_by,
                'limit': parsed.limit
            },
            'explain_rows': [
                {
                    'id': row.id,
                    'select_type': row.select_type,
                    'table': row.table,
                    'type': row.type,
                    'type_rating': row.get_type_rating(),
                    'possible_keys': ', '.join(row.possible_keys) if row.possible_keys else 'NULL',
                    'key': row.key or 'NULL',
                    'key_len': row.key_len,
                    'ref': row.ref or 'NULL',
                    'rows': row.rows,
                    'filtered': row.filtered,
                    'extra': ', '.join(row.extra) if row.extra else ''
                }
                for row in explain_rows
            ],
            'annotations': annotations_by_field,
            'field_descriptions': self._get_field_descriptions()
        }

    def _get_field_descriptions(self) -> dict:
        """Get descriptions for each EXPLAIN field."""
        return {
            'id': 'Sequential identifier for each SELECT in the query',
            'select_type': 'Type of SELECT (SIMPLE, PRIMARY, SUBQUERY, etc.)',
            'table': 'Table being accessed',
            'type': 'Join type - how MySQL accesses the table (const, ref, range, ALL, etc.)',
            'possible_keys': 'Indexes that could potentially be used',
            'key': 'Index actually chosen by the optimizer',
            'key_len': 'Length of the key used (longer = more columns used from index)',
            'ref': 'Columns or constants compared to the index',
            'rows': 'Estimated number of rows MySQL will examine',
            'filtered': 'Percentage of rows that match the WHERE condition',
            'Extra': 'Additional information about query execution'
        }

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        viz_data = self.get_visualization_data(query, dataset)

        if 'error' in viz_data:
            return [Step(
                title="Error",
                description=viz_data['error'],
                highlight={}
            )]

        steps = []

        # Overview step
        steps.append(Step(
            title="Query Overview",
            description=f"Analyzing: {query[:50]}{'...' if len(query) > 50 else ''}",
            highlight={'field': None}
        ))

        # Walk through each explain row
        for row in viz_data['explain_rows']:
            # Access type analysis
            type_desc = {
                'const': 'Best: Single row lookup via unique key',
                'eq_ref': 'Great: One row per join via unique key',
                'ref': 'Good: Multiple rows via non-unique key',
                'range': 'OK: Index range scan',
                'index': 'Caution: Full index scan',
                'ALL': 'Warning: Full table scan!'
            }

            steps.append(Step(
                title=f"Table: {row['table']}",
                description=f"Access type: {row['type']} - {type_desc.get(row['type'], 'Unknown')}",
                highlight={'field': 'type', 'row_id': row['id']}
            ))

            # Key usage
            if row['key'] != 'NULL':
                steps.append(Step(
                    title="Index Used",
                    description=f"Using index '{row['key']}' to find rows",
                    highlight={'field': 'key', 'row_id': row['id']}
                ))
            elif row['possible_keys'] != 'NULL':
                steps.append(Step(
                    title="Index Not Used",
                    description=f"Available indexes: {row['possible_keys']}, but none selected",
                    highlight={'field': 'possible_keys', 'row_id': row['id']}
                ))

            # Row estimation
            steps.append(Step(
                title="Row Estimate",
                description=f"MySQL estimates scanning {row['rows']} rows ({row['filtered']:.0f}% will match filters)",
                highlight={'field': 'rows', 'row_id': row['id']}
            ))

            # Extra info
            if row['extra']:
                for extra in row['extra'].split(', '):
                    extra_desc = {
                        'Using filesort': 'Extra sorting pass needed (can be slow)',
                        'Using temporary': 'Temporary table created (memory/disk usage)',
                        'Using where': 'WHERE filtering after reading rows',
                        'Using index': 'Query satisfied entirely from index (covering index)',
                        'Using index condition': 'Index conditions pushed down to storage engine'
                    }
                    steps.append(Step(
                        title=f"Extra: {extra}",
                        description=extra_desc.get(extra, extra),
                        highlight={'field': 'Extra', 'row_id': row['id']}
                    ))

        return steps

    def get_sample_queries(self) -> list[str]:
        return [
            "SELECT * FROM employees WHERE salary > 80000",
            "SELECT * FROM employees WHERE id = 5",
            "SELECT name, salary FROM employees ORDER BY salary DESC",
            "SELECT department_id, COUNT(*) FROM employees GROUP BY department_id",
        ]
