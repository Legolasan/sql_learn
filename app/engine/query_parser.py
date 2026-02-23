"""
Simple SQL query parser for visualization purposes.
Not a full SQL parser - just extracts key components.
Supports CTEs (WITH ... AS ...) including recursive CTEs.
"""

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CTEDefinition:
    """A single CTE definition."""
    name: str
    query: str
    is_recursive: bool = False
    columns: list[str] = field(default_factory=list)


@dataclass
class ParsedQuery:
    """Parsed SQL query components."""
    query_type: str  # SELECT, INSERT, UPDATE, DELETE, CTE
    tables: list[str]
    columns: list[str]
    where_conditions: list[dict]  # [{'column': x, 'op': '>', 'value': y}]
    group_by: list[str]
    having_conditions: list[dict]
    order_by: list[tuple[str, str]]  # [(column, 'ASC'/'DESC')]
    limit: int | None
    joins: list[dict]
    raw_query: str
    # CTE specific fields
    ctes: list[CTEDefinition] = field(default_factory=list)
    main_query: str = ""
    is_recursive: bool = False
    # Table aliases: alias -> table_name
    table_aliases: dict[str, str] = field(default_factory=dict)


def parse_query(sql: str) -> ParsedQuery:
    """
    Parse a SQL query into components.
    This is a simplified parser for educational purposes.
    """
    sql = sql.strip()
    sql_upper = sql.upper()

    # Check for CTE (WITH clause)
    ctes = []
    main_query = sql
    is_recursive = False

    if sql_upper.startswith('WITH'):
        is_recursive = 'WITH RECURSIVE' in sql_upper
        ctes, main_query = _extract_ctes(sql)

    # Determine query type from main query
    main_upper = main_query.strip().upper()
    if main_upper.startswith('SELECT'):
        query_type = 'SELECT'
    elif main_upper.startswith('INSERT'):
        query_type = 'INSERT'
    elif main_upper.startswith('UPDATE'):
        query_type = 'UPDATE'
    elif main_upper.startswith('DELETE'):
        query_type = 'DELETE'
    elif sql_upper.startswith('WITH'):
        query_type = 'SELECT'  # CTE followed by SELECT
    else:
        query_type = 'UNKNOWN'

    # Parse the main query (or the whole query if no CTEs)
    tables = _extract_tables(main_query)
    columns = _extract_columns(main_query)
    where_conditions = _extract_where(main_query)
    group_by = _extract_group_by(main_query)
    having_conditions = _extract_having(main_query)
    order_by = _extract_order_by(main_query)
    limit = _extract_limit(main_query)
    joins = _extract_joins(main_query)
    table_aliases = _extract_table_aliases(main_query)

    return ParsedQuery(
        query_type=query_type,
        tables=tables,
        columns=columns,
        where_conditions=where_conditions,
        group_by=group_by,
        having_conditions=having_conditions,
        order_by=order_by,
        limit=limit,
        joins=joins,
        raw_query=sql,
        ctes=ctes,
        main_query=main_query,
        is_recursive=is_recursive,
        table_aliases=table_aliases
    )


def _extract_ctes(sql: str) -> tuple[list[CTEDefinition], str]:
    """Extract CTE definitions and the main query."""
    ctes = []
    sql_upper = sql.upper()

    # Check if recursive
    is_recursive = 'WITH RECURSIVE' in sql_upper

    # Remove WITH [RECURSIVE] keyword
    if is_recursive:
        remaining = sql[sql_upper.find('WITH RECURSIVE') + len('WITH RECURSIVE'):].strip()
    else:
        remaining = sql[sql_upper.find('WITH') + len('WITH'):].strip()

    # Find where CTEs end and main query begins
    # CTEs are: name AS (...), name2 AS (...)
    # Main query starts with SELECT/INSERT/UPDATE/DELETE outside of parentheses

    depth = 0
    cte_section = ""
    main_start = 0

    for i, char in enumerate(remaining):
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        elif depth == 0:
            # Check if we've hit the main query
            rest = remaining[i:].strip().upper()
            if rest.startswith('SELECT') or rest.startswith('INSERT') or \
               rest.startswith('UPDATE') or rest.startswith('DELETE'):
                cte_section = remaining[:i]
                main_start = i
                break

    if main_start == 0:
        # No main query found, entire thing is CTEs (error in real SQL)
        return ctes, remaining

    main_query = remaining[main_start:].strip()

    # Parse individual CTEs from cte_section
    # Format: name [(col1, col2)] AS (query), name2 AS (query2)
    cte_pattern = r'(\w+)\s*(?:\(([^)]+)\))?\s*AS\s*\('

    current_pos = 0
    for match in re.finditer(cte_pattern, cte_section, re.IGNORECASE):
        cte_name = match.group(1)
        cte_columns = []
        if match.group(2):
            cte_columns = [c.strip() for c in match.group(2).split(',')]

        # Find the matching closing parenthesis for AS (
        start = match.end()
        depth = 1
        end = start

        for i in range(start, len(cte_section)):
            if cte_section[i] == '(':
                depth += 1
            elif cte_section[i] == ')':
                depth -= 1
                if depth == 0:
                    end = i
                    break

        cte_query = cte_section[start:end].strip()

        # Check if this specific CTE is recursive (references itself)
        cte_is_recursive = is_recursive and cte_name.lower() in cte_query.lower()

        ctes.append(CTEDefinition(
            name=cte_name.lower(),
            query=cte_query,
            is_recursive=cte_is_recursive,
            columns=cte_columns
        ))

    return ctes, main_query


def _extract_tables(sql: str) -> list[str]:
    """Extract table names from FROM clause."""
    # Match FROM table_name [AS] [alias]
    pattern = r'\bFROM\s+(\w+)'
    match = re.search(pattern, sql, re.IGNORECASE)
    tables = []
    if match:
        tables.append(match.group(1).lower())

    # Also get JOIN tables
    join_pattern = r'\bJOIN\s+(\w+)'
    for match in re.finditer(join_pattern, sql, re.IGNORECASE):
        tables.append(match.group(1).lower())

    return tables


def _extract_table_aliases(sql: str) -> dict[str, str]:
    """Extract table aliases mapping alias -> table_name."""
    aliases = {}

    # Match FROM table_name [AS] alias (before JOIN or WHERE)
    from_pattern = r'\bFROM\s+(\w+)\s+(?:AS\s+)?(\w+)(?=\s+(?:INNER|LEFT|RIGHT|CROSS|JOIN|WHERE|GROUP|ORDER|LIMIT|$))'
    match = re.search(from_pattern, sql, re.IGNORECASE)
    if match:
        table_name, alias = match.groups()
        if alias.upper() not in ('INNER', 'LEFT', 'RIGHT', 'CROSS', 'JOIN', 'WHERE', 'GROUP', 'ORDER', 'LIMIT'):
            aliases[alias.lower()] = table_name.lower()

    # Also get JOIN table aliases
    join_pattern = r'\bJOIN\s+(\w+)\s+(?:AS\s+)?(\w+)\s+ON'
    for match in re.finditer(join_pattern, sql, re.IGNORECASE):
        table_name, alias = match.groups()
        aliases[alias.lower()] = table_name.lower()

    return aliases


def _extract_columns(sql: str) -> list[str]:
    """Extract selected columns."""
    # Try to match SELECT ... FROM first
    pattern = r'\bSELECT\s+(.*?)\s+FROM'
    match = re.search(pattern, sql, re.IGNORECASE | re.DOTALL)

    if not match:
        # No FROM clause - try SELECT ... (end of query or WHERE/ORDER/etc)
        pattern_no_from = r'\bSELECT\s+(.*?)(?:\s+WHERE|\s+ORDER|\s+LIMIT|\s+GROUP|\s*$)'
        match = re.search(pattern_no_from, sql, re.IGNORECASE | re.DOTALL)
        if not match:
            return ['*']

    cols_str = match.group(1).strip()
    if cols_str == '*':
        return ['*']

    # Split by comma, handling functions
    columns = []
    depth = 0
    current = ''
    for char in cols_str:
        if char == '(':
            depth += 1
        elif char == ')':
            depth -= 1
        elif char == ',' and depth == 0:
            columns.append(current.strip())
            current = ''
            continue
        current += char
    if current.strip():
        columns.append(current.strip())

    return columns


def _extract_where(sql: str) -> list[dict]:
    """Extract WHERE conditions."""
    conditions = []

    # Find WHERE clause
    where_match = re.search(r'\bWHERE\s+(.*?)(?:\bGROUP BY|\bORDER BY|\bLIMIT|\bHAVING|$)', sql, re.IGNORECASE | re.DOTALL)
    if not where_match:
        return conditions

    where_clause = where_match.group(1).strip()

    # Parse simple conditions (column op value)
    # Supports: =, !=, <>, <, >, <=, >=, LIKE, IN, BETWEEN
    patterns = [
        (r'(\w+)\s*(>=|<=|<>|!=|>|<|=)\s*([\'"]?)(\d+(?:\.\d+)?|[\w\s]+)\3', ['column', 'op', None, 'value']),
        (r'(\w+)\s+LIKE\s+[\'"]([^"\']+)[\'"]', ['column', 'value']),
        (r'(\w+)\s+IN\s*\(([^)]+)\)', ['column', 'values']),
        (r'(\w+)\s+IS\s+NULL', ['column', 'null']),
        (r'(\w+)\s+IS\s+NOT\s+NULL', ['column', 'not_null']),
    ]

    for pattern, fields in patterns:
        for match in re.finditer(pattern, where_clause, re.IGNORECASE):
            if len(fields) == 4:  # Standard comparison
                conditions.append({
                    'column': match.group(1).lower(),
                    'op': match.group(2),
                    'value': _parse_value(match.group(4))
                })
            elif 'values' in fields:  # IN clause
                values = [_parse_value(v.strip().strip('\'"')) for v in match.group(2).split(',')]
                conditions.append({
                    'column': match.group(1).lower(),
                    'op': 'IN',
                    'value': values
                })
            elif 'null' in fields:  # IS NULL
                conditions.append({
                    'column': match.group(1).lower(),
                    'op': 'IS NULL',
                    'value': None
                })
            elif 'not_null' in fields:  # IS NOT NULL
                conditions.append({
                    'column': match.group(1).lower(),
                    'op': 'IS NOT NULL',
                    'value': None
                })
            else:  # LIKE
                conditions.append({
                    'column': match.group(1).lower(),
                    'op': 'LIKE',
                    'value': match.group(2)
                })

    return conditions


def _extract_group_by(sql: str) -> list[str]:
    """Extract GROUP BY columns."""
    pattern = r'\bGROUP BY\s+(.*?)(?:\bHAVING|\bORDER BY|\bLIMIT|$)'
    match = re.search(pattern, sql, re.IGNORECASE)
    if not match:
        return []

    cols = match.group(1).strip()
    return [c.strip().lower() for c in cols.split(',')]


def _extract_having(sql: str) -> list[dict]:
    """Extract HAVING conditions."""
    conditions = []

    having_match = re.search(r'\bHAVING\s+(.*?)(?:\bORDER BY|\bLIMIT|$)', sql, re.IGNORECASE)
    if not having_match:
        return conditions

    having_clause = having_match.group(1).strip()

    # Parse aggregate conditions like COUNT(*) > 5
    pattern = r'(\w+\([^)]*\)|\w+)\s*(>=|<=|<>|!=|>|<|=)\s*(\d+(?:\.\d+)?)'
    for match in re.finditer(pattern, having_clause, re.IGNORECASE):
        conditions.append({
            'expression': match.group(1),
            'op': match.group(2),
            'value': _parse_value(match.group(3))
        })

    return conditions


def _extract_order_by(sql: str) -> list[tuple[str, str]]:
    """Extract ORDER BY columns and direction."""
    pattern = r'\bORDER BY\s+(.*?)(?:\bLIMIT|$)'
    match = re.search(pattern, sql, re.IGNORECASE)
    if not match:
        return []

    order_clause = match.group(1).strip()
    result = []

    for part in order_clause.split(','):
        part = part.strip()
        if ' DESC' in part.upper():
            col = re.sub(r'\s+DESC\s*$', '', part, flags=re.IGNORECASE).strip()
            result.append((col.lower(), 'DESC'))
        else:
            col = re.sub(r'\s+ASC\s*$', '', part, flags=re.IGNORECASE).strip()
            result.append((col.lower(), 'ASC'))

    return result


def _extract_limit(sql: str) -> int | None:
    """Extract LIMIT value."""
    pattern = r'\bLIMIT\s+(\d+)'
    match = re.search(pattern, sql, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def _extract_joins(sql: str) -> list[dict]:
    """Extract JOIN clauses."""
    joins = []

    pattern = r'\b(LEFT|RIGHT|INNER|OUTER|CROSS)?\s*JOIN\s+(\w+)\s+(?:AS\s+)?(\w+)?\s*(?:ON\s+(.+?))?(?=\bJOIN|\bWHERE|\bGROUP|\bORDER|\bLIMIT|$)'
    for match in re.finditer(pattern, sql, re.IGNORECASE):
        joins.append({
            'type': (match.group(1) or 'INNER').upper(),
            'table': match.group(2).lower(),
            'alias': match.group(3).lower() if match.group(3) else None,
            'on': match.group(4).strip() if match.group(4) else None
        })

    return joins


def _parse_value(val: str) -> Any:
    """Parse a string value to appropriate type."""
    val = val.strip()
    try:
        if '.' in val:
            return float(val)
        return int(val)
    except ValueError:
        return val
