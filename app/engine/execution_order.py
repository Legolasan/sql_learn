"""
Query execution order simulator.
Shows how MySQL logically processes a query step by step.
"""

from dataclasses import dataclass
from typing import Any

from app.engine.query_parser import ParsedQuery


@dataclass
class ExecutionStage:
    """A stage in query execution."""
    name: str
    sql_clause: str
    description: str
    input_rows: int
    output_rows: int
    sample_data: list[dict]
    is_active: bool  # True if this stage is used in the query


# Logical execution order (not the written order!)
EXECUTION_ORDER = [
    ('FROM', 'FROM/JOINs', 'Load data from tables and perform joins'),
    ('WHERE', 'WHERE', 'Filter rows based on conditions'),
    ('GROUP BY', 'GROUP BY', 'Group rows with same values'),
    ('HAVING', 'HAVING', 'Filter groups based on aggregate conditions'),
    ('SELECT', 'SELECT', 'Choose which columns to return'),
    ('DISTINCT', 'DISTINCT', 'Remove duplicate rows'),
    ('ORDER BY', 'ORDER BY', 'Sort the result set'),
    ('LIMIT', 'LIMIT/OFFSET', 'Limit number of returned rows'),
]


def simulate_execution(query: ParsedQuery, dataset: Any) -> list[ExecutionStage]:
    """
    Simulate query execution and return stages with data snapshots.
    """
    stages = []

    # Get initial data
    if not query.tables:
        return stages

    primary_table = query.tables[0]
    current_data = _table_to_dicts(dataset.get_table(primary_table))
    columns = dataset.get_table_columns(primary_table)

    # Stage 1: FROM
    stages.append(ExecutionStage(
        name='FROM',
        sql_clause=f'FROM {primary_table}',
        description=f'Load all {len(current_data)} rows from {primary_table}',
        input_rows=0,
        output_rows=len(current_data),
        sample_data=current_data[:5],
        is_active=True
    ))

    # Handle JOINs
    for join in query.joins:
        join_table = join['table']
        join_data = _table_to_dicts(dataset.get_table(join_table))
        # Simplified join simulation
        before_count = len(current_data)
        current_data = _simulate_join(current_data, join_data, join)

        stages.append(ExecutionStage(
            name='JOIN',
            sql_clause=f"{join['type']} JOIN {join_table}",
            description=f"Join with {join_table} ({len(join_data)} rows)",
            input_rows=before_count,
            output_rows=len(current_data),
            sample_data=current_data[:5],
            is_active=True
        ))

    # Stage 2: WHERE
    if query.where_conditions:
        before_count = len(current_data)
        current_data = _apply_where(current_data, query.where_conditions)

        conditions_str = ' AND '.join([
            f"{c['column']} {c['op']} {c['value']}"
            for c in query.where_conditions
        ])

        stages.append(ExecutionStage(
            name='WHERE',
            sql_clause=f'WHERE {conditions_str}',
            description=f'Filter: {before_count} rows -> {len(current_data)} rows',
            input_rows=before_count,
            output_rows=len(current_data),
            sample_data=current_data[:5],
            is_active=True
        ))
    else:
        stages.append(ExecutionStage(
            name='WHERE',
            sql_clause='WHERE (none)',
            description='No WHERE clause - all rows pass through',
            input_rows=len(current_data),
            output_rows=len(current_data),
            sample_data=[],
            is_active=False
        ))

    # Stage 3: GROUP BY
    if query.group_by:
        before_count = len(current_data)
        grouped_data, group_count = _apply_group_by(current_data, query.group_by)

        stages.append(ExecutionStage(
            name='GROUP BY',
            sql_clause=f"GROUP BY {', '.join(query.group_by)}",
            description=f'Group {before_count} rows into {group_count} groups',
            input_rows=before_count,
            output_rows=group_count,
            sample_data=grouped_data[:5],
            is_active=True
        ))
        current_data = grouped_data
    else:
        stages.append(ExecutionStage(
            name='GROUP BY',
            sql_clause='GROUP BY (none)',
            description='No grouping - rows remain individual',
            input_rows=len(current_data),
            output_rows=len(current_data),
            sample_data=[],
            is_active=False
        ))

    # Stage 4: HAVING
    if query.having_conditions:
        before_count = len(current_data)
        current_data = _apply_having(current_data, query.having_conditions)

        stages.append(ExecutionStage(
            name='HAVING',
            sql_clause=f"HAVING {query.having_conditions}",
            description=f'Filter groups: {before_count} -> {len(current_data)}',
            input_rows=before_count,
            output_rows=len(current_data),
            sample_data=current_data[:5],
            is_active=True
        ))
    else:
        stages.append(ExecutionStage(
            name='HAVING',
            sql_clause='HAVING (none)',
            description='No HAVING - all groups pass through',
            input_rows=len(current_data),
            output_rows=len(current_data),
            sample_data=[],
            is_active=False
        ))

    # Stage 5: SELECT
    before_data = current_data
    if query.columns != ['*']:
        current_data = _apply_select(current_data, query.columns)

    stages.append(ExecutionStage(
        name='SELECT',
        sql_clause=f"SELECT {', '.join(query.columns)}",
        description=f"Project {len(query.columns)} column(s)" if query.columns != ['*'] else "Select all columns",
        input_rows=len(before_data),
        output_rows=len(current_data),
        sample_data=current_data[:5],
        is_active=True
    ))

    # Stage 6: ORDER BY
    if query.order_by:
        current_data = _apply_order_by(current_data, query.order_by)

        order_str = ', '.join([f"{col} {dir}" for col, dir in query.order_by])
        stages.append(ExecutionStage(
            name='ORDER BY',
            sql_clause=f'ORDER BY {order_str}',
            description=f'Sort {len(current_data)} rows',
            input_rows=len(current_data),
            output_rows=len(current_data),
            sample_data=current_data[:5],
            is_active=True
        ))
    else:
        stages.append(ExecutionStage(
            name='ORDER BY',
            sql_clause='ORDER BY (none)',
            description='No sorting applied',
            input_rows=len(current_data),
            output_rows=len(current_data),
            sample_data=[],
            is_active=False
        ))

    # Stage 7: LIMIT
    if query.limit:
        before_count = len(current_data)
        current_data = current_data[:query.limit]

        stages.append(ExecutionStage(
            name='LIMIT',
            sql_clause=f'LIMIT {query.limit}',
            description=f'Take first {query.limit} of {before_count} rows',
            input_rows=before_count,
            output_rows=len(current_data),
            sample_data=current_data[:5],
            is_active=True
        ))
    else:
        stages.append(ExecutionStage(
            name='LIMIT',
            sql_clause='LIMIT (none)',
            description='Return all rows',
            input_rows=len(current_data),
            output_rows=len(current_data),
            sample_data=[],
            is_active=False
        ))

    return stages


def _table_to_dicts(rows: list) -> list[dict]:
    """Convert dataclass rows to dicts."""
    if not rows:
        return []
    return [vars(row) if hasattr(row, '__dict__') else row.__dict__ for row in rows]


def _simulate_join(left: list[dict], right: list[dict], join_info: dict) -> list[dict]:
    """Simplified join simulation."""
    # For demo purposes, just combine first few rows
    result = []
    for l_row in left[:10]:
        for r_row in right[:3]:
            combined = {**l_row, **{f"_{k}": v for k, v in r_row.items()}}
            result.append(combined)
    return result


def _apply_where(data: list[dict], conditions: list[dict]) -> list[dict]:
    """Apply WHERE conditions."""
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
            elif op == '!=' and row_val == val:
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


def _apply_group_by(data: list[dict], group_cols: list[str]) -> tuple[list[dict], int]:
    """Apply GROUP BY."""
    groups = {}
    for row in data:
        key = tuple(row.get(col) for col in group_cols)
        if key not in groups:
            groups[key] = []
        groups[key].append(row)

    # Return first row of each group with count
    result = []
    for key, rows in groups.items():
        group_row = {**rows[0], '_count': len(rows)}
        result.append(group_row)

    return result, len(groups)


def _apply_having(data: list[dict], conditions: list[dict]) -> list[dict]:
    """Apply HAVING conditions (simplified)."""
    return data  # Simplified - would need aggregate evaluation


def _apply_select(data: list[dict], columns: list[str]) -> list[dict]:
    """Project specific columns."""
    result = []
    for row in data:
        new_row = {}
        for col in columns:
            # Handle simple column names
            col_name = col.split('.')[-1].strip()
            if col_name in row:
                new_row[col_name] = row[col_name]
            else:
                new_row[col] = row.get(col, None)
        result.append(new_row)
    return result


def _apply_order_by(data: list[dict], order_by: list[tuple[str, str]]) -> list[dict]:
    """Sort data by ORDER BY columns."""
    if not order_by:
        return data

    def sort_key(row):
        keys = []
        for col, direction in order_by:
            val = row.get(col, 0)
            if direction == 'DESC':
                # For descending, negate if numeric, otherwise will handle differently
                if isinstance(val, (int, float)):
                    val = -val
            keys.append(val)
        return tuple(keys)

    return sorted(data, key=sort_key)
