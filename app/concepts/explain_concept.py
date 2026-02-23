"""EXPLAIN visualization concept."""

from typing import Any

from app.concepts.base import BaseConcept, Step
from app.engine.explain import generate_explain, ExplainRow, predict_access_for_index, _calculate_index_cost
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

        explain_row_dicts = [
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
        ]

        # Generate beginner-friendly diagnosis
        diagnosis = self._generate_diagnosis(explain_rows, parsed)

        # Generate index comparison scenarios
        index_scenarios = self._generate_index_scenarios(parsed, dataset, explain_rows)

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
            'explain_rows': explain_row_dicts,
            'annotations': annotations_by_field,
            'field_descriptions': self._get_field_descriptions(),
            'diagnosis': diagnosis,
            'index_scenarios': index_scenarios
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

    def _generate_diagnosis(self, explain_rows: list, parsed: Any) -> dict:
        """Generate beginner-friendly diagnosis of query performance."""
        checklist = []
        worst_rating = 'good'

        for row in explain_rows:
            table_name = row.table
            access_type = row.type
            type_rating = row.get_type_rating()
            key_used = row.key
            rows_examined = row.rows
            has_where = bool(parsed.where_conditions)

            # Track worst rating across all tables
            if type_rating == 'bad':
                worst_rating = 'bad'
            elif type_rating == 'caution' and worst_rating != 'bad':
                worst_rating = 'caution'

            # Priority 1: Access Type (most impactful)
            type_labels = {
                'const': ('good', 'Access Type: const (Single Row Lookup)',
                         'MySQL finds exactly one row using the primary key'),
                'eq_ref': ('good', 'Access Type: eq_ref (Unique Key Join)',
                          'MySQL finds one row per join using a unique index'),
                'ref': ('good', 'Access Type: ref (Index Lookup)',
                       'MySQL uses an index to find matching rows'),
                'range': ('good', 'Access Type: range (Index Range Scan)',
                         'MySQL scans a portion of the index'),
                'index': ('caution', 'Access Type: index (Full Index Scan)',
                         'MySQL reads the entire index (better than table scan, but still slow)'),
                'ALL': ('bad', 'Access Type: ALL (Full Table Scan)',
                       'MySQL is reading every single row in the table')
            }

            status, what, why = type_labels.get(
                access_type,
                ('caution', f'Access Type: {access_type}', 'Unknown access type')
            )

            # Generate fix suggestion for bad access types
            fix = None
            if access_type == 'ALL' and has_where:
                # Find the column being filtered
                filter_cols = [c.get('column', '') for c in parsed.where_conditions if c.get('column')]
                if filter_cols:
                    fix = f"CREATE INDEX idx_{filter_cols[0]} ON {table_name}({filter_cols[0]})"

            checklist.append({
                'priority': 1,
                'field': 'type',
                'status': status,
                'what': what,
                'why': why,
                'fix': fix
            })

            # Priority 2: Rows Examined
            rows_status = 'good'
            rows_why = f'MySQL will examine {rows_examined} row{"s" if rows_examined != 1 else ""}'
            rows_fix = None

            if rows_examined > 100:
                rows_status = 'caution'
                rows_why = f'MySQL will scan {rows_examined} rows to find matches'
                if access_type == 'ALL':
                    rows_fix = 'An index would dramatically reduce the rows scanned'
            elif rows_examined > 1000:
                rows_status = 'bad'
                rows_why = f'MySQL must examine {rows_examined} rows - this will be slow!'

            if rows_examined == 1:
                rows_why = 'MySQL finds exactly 1 row - perfect!'

            checklist.append({
                'priority': 2,
                'field': 'rows',
                'status': rows_status,
                'what': f'Rows Examined: {rows_examined}',
                'why': rows_why,
                'fix': rows_fix
            })

            # Priority 3: Index Usage
            if key_used:
                checklist.append({
                    'priority': 3,
                    'field': 'key',
                    'status': 'good',
                    'what': f'Index Used: {key_used}',
                    'why': f'The "{key_used}" index helps MySQL find rows efficiently',
                    'fix': None
                })
            else:
                key_status = 'bad' if has_where else 'caution'
                key_why = 'No index is being used to speed up the query'
                key_fix = None

                if has_where:
                    filter_cols = [c.get('column', '') for c in parsed.where_conditions if c.get('column')]
                    if filter_cols:
                        key_fix = f"CREATE INDEX idx_{filter_cols[0]} ON {table_name}({filter_cols[0]})"
                        key_why = f'No index on the filtered column "{filter_cols[0]}"'

                checklist.append({
                    'priority': 3,
                    'field': 'key',
                    'status': key_status,
                    'what': 'Index Used: None',
                    'why': key_why,
                    'fix': key_fix
                })

            # Check for filesort/temporary (only if present)
            if row.extra:
                if 'Using filesort' in row.extra:
                    checklist.append({
                        'priority': 4,
                        'field': 'extra',
                        'status': 'caution',
                        'what': 'Extra: Using filesort',
                        'why': 'MySQL needs an extra sorting pass after reading rows',
                        'fix': 'Consider an index that matches your ORDER BY clause'
                    })
                if 'Using temporary' in row.extra:
                    checklist.append({
                        'priority': 4,
                        'field': 'extra',
                        'status': 'caution',
                        'what': 'Extra: Using temporary',
                        'why': 'MySQL creates a temporary table to process this query',
                        'fix': None
                    })

        # Generate overall verdict and summary
        verdict_labels = {
            'good': 'Good',
            'caution': 'Needs Attention',
            'bad': 'Problematic'
        }

        # Generate smart summary that connects the pieces
        summary = self._generate_summary(explain_rows, parsed, worst_rating)

        return {
            'verdict': worst_rating,
            'verdict_label': verdict_labels[worst_rating],
            'summary': summary,
            'checklist': sorted(checklist, key=lambda x: x['priority'])
        }

    def _generate_summary(self, explain_rows: list, parsed: Any, verdict: str) -> str:
        """Generate a one-line summary connecting type, rows, and indexes."""
        if not explain_rows:
            return "Unable to analyze query"

        row = explain_rows[0]  # Focus on primary table
        access_type = row.type
        rows = row.rows
        key = row.key
        table = row.table

        if verdict == 'good':
            if access_type == 'const':
                return f"Excellent! MySQL finds exactly 1 row instantly using the primary key."
            elif access_type in ('eq_ref', 'ref'):
                return f"Using index '{key}' to efficiently locate {rows} row{'s' if rows != 1 else ''}."
            elif access_type == 'range':
                return f"Index range scan on '{key}' - reads only the rows needed."
            else:
                return f"Query is reasonably efficient."

        elif verdict == 'caution':
            if access_type == 'index':
                return f"Full index scan - reads entire index ({rows} rows). Consider more specific WHERE conditions."
            elif rows > 100:
                return f"Scanning {rows} rows. Performance is acceptable but could be improved with better indexing."
            else:
                return f"Query works but has room for optimization."

        else:  # bad
            filter_cols = [c.get('column', '') for c in parsed.where_conditions if c.get('column')]
            if access_type == 'ALL' and filter_cols:
                col = filter_cols[0]
                return f"Full table scan: reading all {rows} rows because there's no index on '{col}'. Adding an index would change type from ALL to range."
            elif access_type == 'ALL':
                return f"Full table scan: MySQL must read all {rows} rows in '{table}'. Consider adding indexes for frequently filtered columns."
            else:
                return f"Query performance is poor. Review the checklist below for specific issues."

    def _generate_index_scenarios(self, parsed: Any, dataset: Any, explain_rows: list) -> dict:
        """Generate index comparison scenarios for interactive exploration."""
        if not parsed.tables:
            return {'available': False}

        table_name = parsed.tables[0]
        table_indexes = dataset.indexes.get(table_name, {})

        if not table_indexes:
            return {'available': False, 'reason': 'No indexes defined for this table'}

        # Get current choice from explain
        current_key = explain_rows[0].key if explain_rows else None
        current_access = explain_rows[0].type if explain_rows else 'ALL'
        current_rows = explain_rows[0].rows if explain_rows else len(dataset.get_table(table_name))

        # Generate scenario for each possible index
        scenarios = []
        best_cost = float('inf')
        best_index = None

        for idx_name in list(table_indexes.keys()) + [None]:
            prediction = predict_access_for_index(parsed, table_name, idx_name, table_indexes, dataset)

            # Get the column this index is on
            idx_col = table_indexes[idx_name][0] if idx_name and idx_name in table_indexes else None

            scenario = {
                'index_name': idx_name if idx_name else 'No Index',
                'index_column': idx_col,
                'access_type': prediction['access_type'],
                'rows': prediction['rows'],
                'cost': prediction['cost'],
                'reason': prediction['reason'],
                'is_current': idx_name == current_key,
                'is_worse': prediction['cost'] > _calculate_index_cost(current_access, current_rows) if current_key else False,
            }

            scenarios.append(scenario)

            if prediction['cost'] < best_cost:
                best_cost = prediction['cost']
                best_index = idx_name

        # Mark the best option
        for s in scenarios:
            s['is_best'] = s['index_name'] == best_index or (s['index_name'] == 'No Index' and best_index is None)

        # Sort: current first, then best, then by cost
        def sort_key(s):
            if s['is_current']:
                return (0, s['cost'])
            if s['is_best']:
                return (1, s['cost'])
            return (2, s['cost'])

        scenarios.sort(key=sort_key)

        return {
            'available': True,
            'table': table_name,
            'current_index': current_key,
            'current_access': current_access,
            'current_rows': current_rows,
            'scenarios': scenarios,
            'where_columns': [c.get('column') for c in parsed.where_conditions if c.get('column')]
        }

    def get_index_comparison(self, query: str, dataset: Any, selected_index: str) -> dict:
        """Generate comparison data for a selected index vs MySQL's choice."""
        parsed = parse_query(query)

        if not parsed.tables:
            return {'error': 'No table in query'}

        table_name = parsed.tables[0]
        table_indexes = dataset.indexes.get(table_name, {})

        # Get MySQL's choice
        explain_rows, _ = generate_explain(parsed, dataset)
        mysql_choice = {
            'index': explain_rows[0].key if explain_rows else None,
            'access_type': explain_rows[0].type if explain_rows else 'ALL',
            'rows': explain_rows[0].rows if explain_rows else len(dataset.get_table(table_name)),
        }
        mysql_choice['cost'] = _calculate_index_cost(mysql_choice['access_type'], mysql_choice['rows'])

        # Get prediction for selected index
        idx_name = None if selected_index == 'none' else selected_index
        prediction = predict_access_for_index(parsed, table_name, idx_name, table_indexes, dataset)

        # Calculate row difference
        row_diff = prediction['rows'] - mysql_choice['rows']
        row_diff_pct = (row_diff / mysql_choice['rows'] * 100) if mysql_choice['rows'] > 0 else 0

        # Determine comparison verdict
        if prediction['cost'] == mysql_choice['cost']:
            verdict = 'equivalent'
            verdict_label = 'Same Performance'
            verdict_color = 'blue'
        elif prediction['cost'] < mysql_choice['cost']:
            verdict = 'better'
            verdict_label = 'Better Choice!'
            verdict_color = 'green'
        else:
            verdict = 'worse'
            verdict_label = 'Worse Choice'
            verdict_color = 'red'

        return {
            'mysql_choice': mysql_choice,
            'your_choice': {
                'index': idx_name if idx_name else 'No Index',
                'access_type': prediction['access_type'],
                'rows': prediction['rows'],
                'cost': prediction['cost'],
                'reason': prediction['reason'],
            },
            'comparison': {
                'row_diff': row_diff,
                'row_diff_pct': round(row_diff_pct, 1),
                'verdict': verdict,
                'verdict_label': verdict_label,
                'verdict_color': verdict_color,
            }
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
