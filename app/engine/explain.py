"""
EXPLAIN output simulator.
Generates MySQL-like EXPLAIN results with educational annotations.
"""

from dataclasses import dataclass
from typing import Any

from app.engine.query_parser import ParsedQuery


@dataclass
class ExplainRow:
    """A single row in EXPLAIN output."""
    id: int
    select_type: str
    table: str
    type: str  # system, const, eq_ref, ref, range, index, ALL
    possible_keys: list[str]
    key: str | None
    key_len: int | None
    ref: str | None
    rows: int
    filtered: float
    extra: list[str]

    def get_type_rating(self) -> str:
        """Get quality rating for access type."""
        ratings = {
            'system': 'good',
            'const': 'good',
            'eq_ref': 'good',
            'ref': 'good',
            'range': 'good',
            'index': 'caution',
            'ALL': 'bad'
        }
        return ratings.get(self.type, 'caution')


@dataclass
class ExplainAnnotation:
    """Annotation explaining an EXPLAIN field."""
    field: str
    value: Any
    explanation: str
    recommendation: str | None = None
    severity: str = 'info'  # info, caution, warning


def generate_explain(query: ParsedQuery, dataset: Any) -> tuple[list[ExplainRow], list[ExplainAnnotation]]:
    """
    Generate EXPLAIN output for a query.

    Returns:
        Tuple of (EXPLAIN rows, annotations)
    """
    rows = []
    annotations = []

    for i, table_name in enumerate(query.tables):
        table_data = dataset.get_table(table_name)
        table_indexes = dataset.indexes.get(table_name, {})

        # Determine access type and key
        access_type, key_used, possible_keys = _determine_access(
            query, table_name, table_indexes, dataset
        )

        # Estimate rows
        total_rows = len(table_data)
        rows_examined = _estimate_rows(query, table_name, total_rows, access_type)

        # Determine extra info
        extra = _determine_extra(query, table_name, access_type)

        row = ExplainRow(
            id=i + 1,
            select_type='SIMPLE',
            table=table_name,
            type=access_type,
            possible_keys=possible_keys,
            key=key_used,
            key_len=len(key_used) * 4 if key_used else None,
            ref='const' if key_used and access_type in ('const', 'ref') else None,
            rows=rows_examined,
            filtered=_estimate_filtered(query, table_name, total_rows, rows_examined),
            extra=extra
        )
        rows.append(row)

        # Generate annotations
        annotations.extend(_generate_annotations(row, query, table_name))

    return rows, annotations


def _determine_access(query: ParsedQuery, table: str, indexes: dict, dataset: Any) -> tuple[str, str | None, list[str]]:
    """Determine access type and key used."""
    possible_keys = list(indexes.keys())

    # Check if we're querying by primary key
    for cond in query.where_conditions:
        col = cond.get('column', '')
        op = cond.get('op', '')

        # Check if condition uses an indexed column
        for idx_name, (idx_col, _) in indexes.items():
            if col == idx_col:
                if op == '=' and idx_name == 'PRIMARY':
                    return 'const', 'PRIMARY', possible_keys
                elif op == '=':
                    return 'ref', idx_name, possible_keys
                elif op in ('>', '<', '>=', '<=', 'BETWEEN'):
                    return 'range', idx_name, possible_keys

    # Check for index-only access
    if query.columns != ['*'] and all(c in [idx[0] for idx in indexes.values()] for c in query.columns):
        return 'index', list(indexes.keys())[0] if indexes else None, possible_keys

    # Full table scan
    return 'ALL', None, possible_keys


def _estimate_rows(query: ParsedQuery, table: str, total: int, access_type: str) -> int:
    """Estimate number of rows examined."""
    if access_type == 'const':
        return 1
    elif access_type in ('eq_ref', 'ref'):
        return max(1, total // 10)
    elif access_type == 'range':
        # Estimate ~30% of table for range queries
        return max(1, int(total * 0.3))
    elif access_type == 'index':
        return total
    else:  # ALL
        return total


def _estimate_filtered(query: ParsedQuery, table: str, total: int, examined: int) -> float:
    """Estimate filter percentage."""
    if not query.where_conditions:
        return 100.0

    # More conditions = more filtering
    filter_factor = 100.0 / (len(query.where_conditions) + 1)
    return min(100.0, max(10.0, filter_factor))


def _determine_extra(query: ParsedQuery, table: str, access_type: str) -> list[str]:
    """Determine Extra column content."""
    extra = []

    # Check for WHERE
    if query.where_conditions:
        if access_type == 'ALL':
            extra.append('Using where')

    # Check for filesort
    if query.order_by:
        order_cols = [col for col, _ in query.order_by]
        # Would need index to avoid filesort
        extra.append('Using filesort')

    # Check for temporary
    if query.group_by and query.order_by:
        extra.append('Using temporary')

    # Check for index condition pushdown
    if access_type == 'range':
        extra.append('Using index condition')

    return extra


def _generate_annotations(row: ExplainRow, query: ParsedQuery, table: str) -> list[ExplainAnnotation]:
    """Generate educational annotations for EXPLAIN row."""
    annotations = []

    # Access type annotation
    type_explanations = {
        'system': 'Table has only one row. This is the best possible case.',
        'const': 'One row match using PRIMARY KEY or UNIQUE index. Very efficient.',
        'eq_ref': 'One row per join using unique index. Used in JOINs.',
        'ref': 'All rows with matching index value are read. Good for non-unique indexes.',
        'range': 'Index range scan. Retrieves rows in a given range.',
        'index': 'Full index scan. Reads entire index, better than ALL.',
        'ALL': 'Full table scan. Reads every row in the table. Usually bad for large tables.'
    }

    annotations.append(ExplainAnnotation(
        field='type',
        value=row.type,
        explanation=type_explanations.get(row.type, 'Unknown access type'),
        severity='warning' if row.type == 'ALL' else 'info',
        recommendation='Consider adding an index on filtered columns' if row.type == 'ALL' else None
    ))

    # Key annotation
    if row.key:
        annotations.append(ExplainAnnotation(
            field='key',
            value=row.key,
            explanation=f'Using index "{row.key}" to find rows',
            severity='info'
        ))
    elif row.possible_keys:
        annotations.append(ExplainAnnotation(
            field='key',
            value='NULL',
            explanation='No index used despite available indexes',
            severity='caution',
            recommendation='Query conditions may not match index columns'
        ))

    # Rows annotation
    annotations.append(ExplainAnnotation(
        field='rows',
        value=row.rows,
        explanation=f'MySQL estimates examining {row.rows} rows',
        severity='caution' if row.rows > 100 else 'info'
    ))

    # Extra annotations
    for extra_item in row.extra:
        if extra_item == 'Using filesort':
            annotations.append(ExplainAnnotation(
                field='Extra',
                value='Using filesort',
                explanation='MySQL must do an extra sorting pass',
                severity='caution',
                recommendation='Consider adding index that matches ORDER BY'
            ))
        elif extra_item == 'Using temporary':
            annotations.append(ExplainAnnotation(
                field='Extra',
                value='Using temporary',
                explanation='MySQL creates a temporary table for this query',
                severity='caution',
                recommendation='Usually caused by GROUP BY + ORDER BY on different columns'
            ))
        elif extra_item == 'Using where':
            annotations.append(ExplainAnnotation(
                field='Extra',
                value='Using where',
                explanation='Rows are filtered after being read from table',
                severity='info'
            ))

    return annotations
