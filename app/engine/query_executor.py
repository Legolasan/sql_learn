"""
Query executor that runs SQL queries against the static dataset.
Supports CTEs (WITH ... AS ...) including recursive CTEs.
"""

import re
import time
from dataclasses import dataclass, field
from typing import Any

from app.engine.query_parser import parse_query, ParsedQuery, CTEDefinition
from app.engine.errors import (
    QueryError, SyntaxError, UnknownTableError, UnknownColumnError,
    UnsupportedFeatureError, EmptyQueryError, NoTablesError
)


@dataclass
class QueryResult:
    """Result of a query execution."""
    rows: list[dict]
    columns: list[str]
    row_count: int
    execution_time_ms: float
    query: str
    warnings: list[str] = field(default_factory=list)
    cte_info: dict = field(default_factory=dict)  # Info about CTEs executed


class QueryExecutor:
    """Executes SQL queries against the static dataset."""

    AVAILABLE_TABLES = ['employees', 'departments', 'customers', 'products', 'orders', 'order_items']

    TABLE_COLUMNS = {
        'employees': ['id', 'name', 'department_id', 'manager_id', 'salary', 'hire_date', 'email', 'phone'],
        'departments': ['id', 'name', 'budget', 'location'],
        'customers': ['id', 'name', 'email', 'city', 'country', 'credit_limit', 'created_at'],
        'products': ['id', 'name', 'category', 'price', 'stock_quantity', 'weight', 'is_active'],
        'orders': ['id', 'customer_id', 'employee_id', 'order_date', 'shipped_date', 'status', 'notes'],
        'order_items': ['id', 'order_id', 'product_id', 'quantity', 'unit_price', 'discount'],
    }

    # Maximum recursion depth for recursive CTEs
    MAX_RECURSION_DEPTH = 100

    def __init__(self, dataset):
        self.dataset = dataset
        # Virtual tables created by CTEs
        self._cte_tables: dict[str, list[dict]] = {}
        self._cte_columns: dict[str, list[str]] = {}

    def execute(self, query: str) -> QueryResult:
        """
        Execute a query and return results.

        Raises:
            QueryError: On any query error
        """
        start_time = time.time()

        # Reset CTE tables
        self._cte_tables = {}
        self._cte_columns = {}

        # Check for empty query
        if not query or not query.strip():
            raise EmptyQueryError()

        # Parse the query
        try:
            parsed = parse_query(query)
        except Exception as e:
            raise SyntaxError(f"Failed to parse query: {str(e)}")

        # Execute CTEs first
        cte_info = {}
        if parsed.ctes:
            cte_info = self._execute_ctes(parsed.ctes, parsed.is_recursive)

        # Validate main query
        self._validate(parsed)

        # Execute main query
        rows, columns = self._execute(parsed)

        execution_time = (time.time() - start_time) * 1000

        return QueryResult(
            rows=rows,
            columns=columns,
            row_count=len(rows),
            execution_time_ms=round(execution_time, 2),
            query=query,
            cte_info=cte_info
        )

    def _execute_ctes(self, ctes: list[CTEDefinition], is_recursive: bool) -> dict:
        """Execute all CTEs and store results."""
        cte_info = {
            'count': len(ctes),
            'names': [c.name for c in ctes],
            'recursive': is_recursive,
            'details': []
        }

        for cte in ctes:
            if cte.is_recursive:
                rows, columns = self._execute_recursive_cte(cte)
            else:
                rows, columns = self._execute_simple_cte(cte)

            # Store CTE results as virtual table
            self._cte_tables[cte.name] = rows
            self._cte_columns[cte.name] = columns

            cte_info['details'].append({
                'name': cte.name,
                'row_count': len(rows),
                'columns': columns,
                'is_recursive': cte.is_recursive
            })

        return cte_info

    def _execute_simple_cte(self, cte: CTEDefinition) -> tuple[list[dict], list[str]]:
        """Execute a non-recursive CTE."""
        # Parse and execute the CTE query
        cte_parsed = parse_query(f"SELECT * FROM dummy")  # Placeholder

        # Actually parse the CTE's inner query
        try:
            cte_parsed = parse_query(cte.query if cte.query.upper().strip().startswith('SELECT')
                                     else f"SELECT {cte.query}")
        except:
            cte_parsed = parse_query(f"SELECT * FROM ({cte.query}) t")

        # Execute the CTE query
        rows, columns = self._execute(cte_parsed)

        # If CTE has explicit column names, rename
        if cte.columns:
            renamed_rows = []
            for row in rows:
                new_row = {}
                for i, col in enumerate(cte.columns):
                    if i < len(columns):
                        new_row[col] = row.get(columns[i])
                renamed_rows.append(new_row)
            rows = renamed_rows
            columns = cte.columns

        return rows, columns

    def _execute_recursive_cte(self, cte: CTEDefinition) -> tuple[list[dict], list[str]]:
        """Execute a recursive CTE."""
        # Split the CTE query into anchor and recursive parts
        # Format: anchor_query UNION ALL recursive_query

        query = cte.query
        query_upper = query.upper()

        # Find UNION ALL
        union_pos = query_upper.find('UNION ALL')
        if union_pos == -1:
            # Not actually recursive, just execute as simple
            return self._execute_simple_cte(cte)

        anchor_query = query[:union_pos].strip()
        recursive_query = query[union_pos + len('UNION ALL'):].strip()

        # Execute anchor
        anchor_parsed = parse_query(anchor_query if anchor_query.upper().startswith('SELECT')
                                    else f"SELECT * FROM ({anchor_query}) t")
        anchor_rows, columns = self._execute(anchor_parsed)

        if not anchor_rows:
            return [], columns

        # Use explicit columns if provided
        if cte.columns:
            columns = cte.columns

        all_rows = list(anchor_rows)
        current_rows = anchor_rows
        iteration = 0

        # Iteratively execute recursive part
        while current_rows and iteration < self.MAX_RECURSION_DEPTH:
            iteration += 1

            # Make current CTE results available
            self._cte_tables[cte.name] = current_rows
            self._cte_columns[cte.name] = columns

            # Execute recursive query
            try:
                rec_parsed = parse_query(recursive_query if recursive_query.upper().startswith('SELECT')
                                         else f"SELECT * FROM ({recursive_query}) t")
                new_rows, new_cols = self._execute(rec_parsed)
            except Exception as e:
                break

            if not new_rows:
                break

            # Map new row columns to anchor columns (recursive CTE must match anchor structure)
            mapped_rows = []
            for row in new_rows:
                mapped_row = {}
                for i, anchor_col in enumerate(columns):
                    if i < len(new_cols):
                        # Get value from new row using new column name
                        new_col = new_cols[i]
                        mapped_row[anchor_col] = row.get(new_col, row.get(anchor_col))
                    else:
                        mapped_row[anchor_col] = None
                mapped_rows.append(mapped_row)

            # Add new rows to all rows
            all_rows.extend(mapped_rows)
            current_rows = mapped_rows

        # Final CTE contains all rows
        self._cte_tables[cte.name] = all_rows
        self._cte_columns[cte.name] = columns

        return all_rows, columns

    def _validate(self, parsed: ParsedQuery):
        """Validate the parsed query."""

        # Check for SELECT
        if parsed.query_type != 'SELECT':
            raise UnsupportedFeatureError(
                f"{parsed.query_type} queries",
                "Only SELECT queries are supported in this demo"
            )

        # Check tables exist (including CTEs) - skip if no tables (literal SELECT)
        if not parsed.tables:
            return  # Literal SELECT like "SELECT 1 as n" is valid

        available = self.AVAILABLE_TABLES + list(self._cte_tables.keys())

        for table in parsed.tables:
            if table.lower() not in [t.lower() for t in available]:
                raise UnknownTableError(table, available)

        # Check columns exist (if not using *)
        if parsed.columns != ['*']:
            available_cols = self._get_available_columns(parsed.tables)

            for col in parsed.columns:
                # Handle aliases and functions
                col_name = self._extract_column_name(col)
                if col_name and col_name.lower() not in [c.lower() for c in available_cols]:
                    # Check if it's an aggregate function
                    if not self._is_aggregate(col):
                        raise UnknownColumnError(col_name, parsed.tables[0], available_cols)

        # Check WHERE columns
        for cond in parsed.where_conditions:
            col = cond.get('column', '')
            if col:
                available_cols = self._get_available_columns(parsed.tables)
                if col.lower() not in [c.lower() for c in available_cols]:
                    raise UnknownColumnError(col, parsed.tables[0], available_cols)

    def _get_available_columns(self, tables: list[str]) -> list[str]:
        """Get all columns available from the specified tables (including CTEs)."""
        columns = []
        for table in tables:
            table_lower = table.lower()
            # Check CTEs first
            if table_lower in self._cte_columns:
                columns.extend(self._cte_columns[table_lower])
            elif table_lower in self.TABLE_COLUMNS:
                columns.extend(self.TABLE_COLUMNS[table_lower])
        return columns

    def _extract_column_name(self, col_expr: str) -> str | None:
        """Extract the column name from an expression."""
        # Handle table.column
        if '.' in col_expr:
            return col_expr.split('.')[-1].strip()

        # Handle aliases (col AS alias)
        if ' AS ' in col_expr.upper():
            return col_expr.split()[0].strip()

        # Handle functions
        match = re.match(r'\w+\(([^)]+)\)', col_expr)
        if match:
            inner = match.group(1).strip()
            if inner == '*':
                return None
            return inner

        return col_expr.strip()

    def _is_aggregate(self, col_expr: str) -> bool:
        """Check if expression is an aggregate function."""
        aggregates = ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN']
        col_upper = col_expr.upper()
        return any(f"{agg}(" in col_upper for agg in aggregates)

    def _has_aggregates(self, columns: list[str]) -> bool:
        """Check if any column expression contains an aggregate function."""
        return any(self._is_aggregate(col) for col in columns)

    def _apply_aggregate_no_group(self, data: list[dict], select_cols: list[str]) -> list[dict]:
        """Apply aggregations when there's no GROUP BY (entire dataset is one group)."""
        result_row = {}

        for col_expr in select_cols:
            col_upper = col_expr.upper()

            # Extract alias if present
            alias = col_expr
            source_expr = col_expr
            if ' AS ' in col_upper:
                parts = re.split(r'\s+AS\s+', col_expr, flags=re.IGNORECASE)
                source_expr = parts[0].strip()
                alias = parts[1].strip()

            source_upper = source_expr.upper()
            value = None

            if 'COUNT(*)' in source_upper:
                value = len(data)
            elif 'COUNT(' in source_upper:
                match = re.search(r'COUNT\((\w+)\)', source_expr, re.IGNORECASE)
                if match:
                    col = match.group(1)
                    value = sum(1 for r in data if r.get(col) is not None)
            elif 'SUM(' in source_upper:
                match = re.search(r'SUM\((\w+)\)', source_expr, re.IGNORECASE)
                if match:
                    col = match.group(1)
                    vals = [r.get(col) for r in data if r.get(col) is not None]
                    value = sum(vals) if vals else 0
            elif 'AVG(' in source_upper:
                match = re.search(r'AVG\((\w+)\)', source_expr, re.IGNORECASE)
                if match:
                    col = match.group(1)
                    vals = [r.get(col) for r in data if r.get(col) is not None]
                    value = sum(vals) / len(vals) if vals else 0
            elif 'MAX(' in source_upper:
                match = re.search(r'MAX\((\w+)\)', source_expr, re.IGNORECASE)
                if match:
                    col = match.group(1)
                    vals = [r.get(col) for r in data if r.get(col) is not None]
                    value = max(vals) if vals else None
            elif 'MIN(' in source_upper:
                match = re.search(r'MIN\((\w+)\)', source_expr, re.IGNORECASE)
                if match:
                    col = match.group(1)
                    vals = [r.get(col) for r in data if r.get(col) is not None]
                    value = min(vals) if vals else None

            if value is not None:
                result_row[alias] = value

        return [result_row] if result_row else []

    def _execute(self, parsed: ParsedQuery) -> tuple[list[dict], list[str]]:
        """Execute the parsed query."""

        # Handle SELECT without FROM (literal values like SELECT 1 as n)
        if not parsed.tables:
            return self._execute_literal_select(parsed)

        # Get base data (could be from CTE or real table)
        primary_table = parsed.tables[0]
        data = self._get_table_data(primary_table)

        # Apply JOINs
        for join in parsed.joins:
            join_table = join['table']
            join_data = self._get_table_data(join_table)
            data = self._apply_join(data, join_data, join, primary_table, join_table)

        # Apply WHERE
        if parsed.where_conditions:
            data = self._apply_where(data, parsed.where_conditions)

        # Apply GROUP BY (or aggregate without GROUP BY)
        if parsed.group_by:
            data = self._apply_group_by(data, parsed.group_by, parsed.columns)
        elif self._has_aggregates(parsed.columns):
            # Aggregate query without GROUP BY - treat all rows as one group
            data = self._apply_aggregate_no_group(data, parsed.columns)

        # Apply HAVING
        if parsed.having_conditions:
            data = self._apply_having(data, parsed.having_conditions)

        # Apply ORDER BY
        if parsed.order_by:
            data = self._apply_order_by(data, parsed.order_by)

        # Apply LIMIT
        if parsed.limit:
            data = data[:parsed.limit]

        # Select columns
        columns, data = self._select_columns(data, parsed.columns, primary_table)

        return data, columns

    def _execute_literal_select(self, parsed: ParsedQuery) -> tuple[list[dict], list[str]]:
        """Execute a SELECT without FROM clause (literal values)."""
        # Handle SELECT 1 as n, SELECT 'hello' as greeting, etc.
        row = {}
        columns = []

        for col_expr in parsed.columns:
            col_expr = col_expr.strip()

            # Parse "value AS name" or just "value"
            if ' AS ' in col_expr.upper():
                parts = re.split(r'\s+AS\s+', col_expr, flags=re.IGNORECASE)
                value_str = parts[0].strip()
                col_name = parts[1].strip()
            else:
                # Just a value, use the expression as the column name
                value_str = col_expr
                col_name = col_expr

            # Parse the value
            value = self._parse_literal_value(value_str)

            row[col_name] = value
            columns.append(col_name)

        return [row], columns

    def _parse_literal_value(self, value_str: str):
        """Parse a literal value string to appropriate type."""
        value_str = value_str.strip().strip('\'"')
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            return value_str

    def _evaluate_expression(self, expr: str, row: dict):
        """Evaluate a simple expression with row data."""
        expr = expr.strip()

        # Handle "column AS alias"
        if ' AS ' in expr.upper():
            parts = re.split(r'\s+AS\s+', expr, flags=re.IGNORECASE)
            expr = parts[0].strip()

        # Handle simple arithmetic: col + num, col - num, col * num, col / num
        arith_match = re.match(r'(\w+)\s*([+\-*/])\s*(\d+(?:\.\d+)?)', expr)
        if arith_match:
            col, op, num = arith_match.groups()
            col_val = row.get(col, 0)
            num_val = float(num) if '.' in num else int(num)
            if op == '+':
                return col_val + num_val
            elif op == '-':
                return col_val - num_val
            elif op == '*':
                return col_val * num_val
            elif op == '/':
                return col_val / num_val if num_val != 0 else 0

        # Handle level + 1 style expressions with column reference
        arith_match2 = re.match(r'(\w+)\.(\w+)\s*([+\-*/])\s*(\d+(?:\.\d+)?)', expr)
        if arith_match2:
            table, col, op, num = arith_match2.groups()
            col_val = row.get(col, row.get(f"{table}.{col}", 0))
            num_val = float(num) if '.' in num else int(num)
            if op == '+':
                return col_val + num_val
            elif op == '-':
                return col_val - num_val
            elif op == '*':
                return col_val * num_val
            elif op == '/':
                return col_val / num_val if num_val != 0 else 0

        # Just a column name
        if expr in row:
            return row[expr]

        # Try lowercase
        if expr.lower() in row:
            return row[expr.lower()]

        # Try to parse as literal
        return self._parse_literal_value(expr)

    def _get_table_data(self, table_name: str) -> list[dict]:
        """Get table data as list of dicts (from real table or CTE)."""
        table_lower = table_name.lower()

        # Check CTEs first
        if table_lower in self._cte_tables:
            return list(self._cte_tables[table_lower])  # Return a copy

        # Real table
        table = self.dataset.get_table(table_name)
        if not table:
            return []

        return [self._row_to_dict(row) for row in table]

    def _row_to_dict(self, row) -> dict:
        """Convert a dataclass row to dict."""
        if hasattr(row, '__dict__'):
            return dict(row.__dict__)
        return dict(row)

    def _apply_join(self, left_data: list[dict], right_data: list[dict],
                    join_info: dict, left_table: str, right_table: str) -> list[dict]:
        """Apply a JOIN operation."""
        join_type = join_info.get('type', 'INNER')
        on_clause = join_info.get('on', '')

        # Parse ON clause to get join columns
        left_col, right_col = self._parse_join_on(on_clause, left_table, right_table)

        result = []
        right_matched = set()

        for l_row in left_data:
            l_val = l_row.get(left_col)
            matched = False

            for i, r_row in enumerate(right_data):
                r_val = r_row.get(right_col)

                if l_val == r_val:
                    matched = True
                    right_matched.add(i)
                    # Combine rows with prefixes
                    combined = {f"{left_table}.{k}": v for k, v in l_row.items()}
                    combined.update({f"{right_table}.{k}": v for k, v in r_row.items()})
                    # Also add without prefix for convenience
                    combined.update(l_row)
                    combined.update({k: v for k, v in r_row.items() if k not in combined})
                    result.append(combined)

            if not matched and join_type in ('LEFT', 'LEFT OUTER'):
                combined = {f"{left_table}.{k}": v for k, v in l_row.items()}
                combined.update({f"{right_table}.{k}": None for k in right_data[0].keys()} if right_data else {})
                combined.update(l_row)
                result.append(combined)

        # Handle RIGHT JOIN unmatched
        if join_type in ('RIGHT', 'RIGHT OUTER'):
            for i, r_row in enumerate(right_data):
                if i not in right_matched:
                    combined = {f"{left_table}.{k}": None for k in left_data[0].keys()} if left_data else {}
                    combined.update({f"{right_table}.{k}": v for k, v in r_row.items()})
                    combined.update(r_row)
                    result.append(combined)

        return result

    def _parse_join_on(self, on_clause: str, left_table: str, right_table: str) -> tuple[str, str]:
        """Parse JOIN ON clause to extract column names."""
        if not on_clause:
            # Default join columns
            if left_table == 'employees' and right_table == 'departments':
                return 'department_id', 'id'
            elif left_table == 'orders' and right_table == 'employees':
                return 'employee_id', 'id'
            return 'id', 'id'

        # Parse "table1.col = table2.col"
        match = re.search(r'(\w+)\.(\w+)\s*=\s*(\w+)\.(\w+)', on_clause, re.IGNORECASE)
        if match:
            t1, c1, t2, c2 = match.groups()
            if t1.lower() == left_table.lower():
                return c1.lower(), c2.lower()
            else:
                return c2.lower(), c1.lower()

        return 'id', 'id'

    def _apply_where(self, data: list[dict], conditions: list[dict]) -> list[dict]:
        """Apply WHERE conditions."""
        result = []

        for row in data:
            if self._row_matches_conditions(row, conditions):
                result.append(row)

        return result

    def _row_matches_conditions(self, row: dict, conditions: list[dict]) -> bool:
        """Check if a row matches all conditions."""
        for cond in conditions:
            col = cond.get('column', '')
            op = cond.get('op', '=')
            val = cond.get('value')

            row_val = row.get(col)

            # Handle IS NULL / IS NOT NULL
            if op == 'IS NULL':
                if row_val is not None:
                    return False
                continue
            elif op == 'IS NOT NULL':
                if row_val is None:
                    return False
                continue

            if row_val is None:
                return False

            if not self._compare(row_val, op, val):
                return False

        return True

    def _compare(self, row_val: Any, op: str, cond_val: Any) -> bool:
        """Compare values with operator."""
        try:
            if op == '=':
                return row_val == cond_val
            elif op in ('!=', '<>'):
                return row_val != cond_val
            elif op == '>':
                return row_val > cond_val
            elif op == '<':
                return row_val < cond_val
            elif op == '>=':
                return row_val >= cond_val
            elif op == '<=':
                return row_val <= cond_val
            elif op == 'IN':
                return row_val in cond_val
            elif op == 'LIKE':
                # Simple LIKE matching
                pattern = cond_val.replace('%', '.*').replace('_', '.')
                return bool(re.match(f'^{pattern}$', str(row_val), re.IGNORECASE))
            return False
        except TypeError:
            return False

    def _apply_group_by(self, data: list[dict], group_cols: list[str],
                        select_cols: list[str]) -> list[dict]:
        """Apply GROUP BY with aggregations."""
        groups = {}

        for row in data:
            key = tuple(row.get(col) for col in group_cols)
            if key not in groups:
                groups[key] = []
            groups[key].append(row)

        result = []
        for key, rows in groups.items():
            group_row = {}

            # Add group columns
            for i, col in enumerate(group_cols):
                group_row[col] = key[i]

            # Calculate aggregates
            for col_expr in select_cols:
                if col_expr in group_cols:
                    continue

                col_upper = col_expr.upper()

                # Extract alias if present (e.g., "SUM(salary) AS total" -> alias is "total")
                alias = col_expr
                source_expr = col_expr
                if ' AS ' in col_upper:
                    parts = re.split(r'\s+AS\s+', col_expr, flags=re.IGNORECASE)
                    source_expr = parts[0].strip()
                    alias = parts[1].strip()

                source_upper = source_expr.upper()
                value = None

                if 'COUNT(*)' in source_upper:
                    value = len(rows)
                elif 'COUNT(' in source_upper:
                    match = re.search(r'COUNT\((\w+)\)', source_expr, re.IGNORECASE)
                    if match:
                        col = match.group(1)
                        value = sum(1 for r in rows if r.get(col) is not None)
                elif 'SUM(' in source_upper:
                    match = re.search(r'SUM\((\w+)\)', source_expr, re.IGNORECASE)
                    if match:
                        col = match.group(1)
                        value = sum(r.get(col, 0) for r in rows)
                elif 'AVG(' in source_upper:
                    match = re.search(r'AVG\((\w+)\)', source_expr, re.IGNORECASE)
                    if match:
                        col = match.group(1)
                        vals = [r.get(col) for r in rows if r.get(col) is not None]
                        value = sum(vals) / len(vals) if vals else 0
                elif 'MAX(' in source_upper:
                    match = re.search(r'MAX\((\w+)\)', source_expr, re.IGNORECASE)
                    if match:
                        col = match.group(1)
                        vals = [r.get(col) for r in rows if r.get(col) is not None]
                        value = max(vals) if vals else None
                elif 'MIN(' in source_upper:
                    match = re.search(r'MIN\((\w+)\)', source_expr, re.IGNORECASE)
                    if match:
                        col = match.group(1)
                        vals = [r.get(col) for r in rows if r.get(col) is not None]
                        value = min(vals) if vals else None

                if value is not None:
                    group_row[alias] = value

            result.append(group_row)

        return result

    def _apply_having(self, data: list[dict], conditions: list[dict]) -> list[dict]:
        """Apply HAVING conditions on grouped data."""
        result = []

        for row in data:
            matches = True
            for cond in conditions:
                expr = cond.get('expression', '')
                op = cond.get('op', '>')
                val = cond.get('value', 0)

                # Get the aggregate value
                row_val = row.get(expr, 0)

                if not self._compare(row_val, op, val):
                    matches = False
                    break

            if matches:
                result.append(row)

        return result

    def _apply_order_by(self, data: list[dict], order_by: list[tuple[str, str]]) -> list[dict]:
        """Apply ORDER BY sorting."""
        if not order_by:
            return data

        def sort_key(row):
            keys = []
            for col, direction in order_by:
                val = row.get(col, 0)
                if val is None:
                    val = 0
                if direction == 'DESC' and isinstance(val, (int, float)):
                    val = -val
                keys.append(val)
            return tuple(keys)

        return sorted(data, key=sort_key)

    def _select_columns(self, data: list[dict], columns: list[str],
                        primary_table: str) -> tuple[list[str], list[dict]]:
        """Select only the requested columns."""
        if columns == ['*']:
            # Return all columns from primary table (or CTE)
            if primary_table.lower() in self._cte_columns:
                all_cols = self._cte_columns[primary_table.lower()]
            else:
                all_cols = self.TABLE_COLUMNS.get(primary_table, [])
            return all_cols, data

        # Parse column expressions
        result_cols = []
        result_data = []

        for col_expr in columns:
            # Handle aliases
            if ' AS ' in col_expr.upper():
                parts = re.split(r'\s+AS\s+', col_expr, flags=re.IGNORECASE)
                result_cols.append(parts[1].strip())
            else:
                result_cols.append(col_expr)

        for row in data:
            new_row = {}
            for i, col_expr in enumerate(columns):
                col_name = result_cols[i]

                # Handle aliases
                alias = None
                if ' AS ' in col_expr.upper():
                    parts = re.split(r'\s+AS\s+', col_expr, flags=re.IGNORECASE)
                    source_col = parts[0].strip()
                    alias = parts[1].strip()
                else:
                    source_col = col_expr

                # First, check if the alias exists in the row (from GROUP BY)
                if alias and alias in row:
                    new_row[col_name] = row[alias]
                # Check if it's an arithmetic expression
                elif any(op in source_col for op in ['+', '-', '*', '/']):
                    new_row[col_name] = self._evaluate_expression(source_col, row)
                # Get value from row by source column
                elif source_col in row:
                    new_row[col_name] = row[source_col]
                elif source_col.lower() in row:
                    new_row[col_name] = row[source_col.lower()]
                # Try the result column name itself
                elif col_name in row:
                    new_row[col_name] = row[col_name]
                else:
                    # Try without table prefix
                    simple_col = source_col.split('.')[-1] if '.' in source_col else source_col
                    new_row[col_name] = row.get(simple_col, row.get(source_col))

            result_data.append(new_row)

        return result_cols, result_data
