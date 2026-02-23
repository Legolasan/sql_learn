"""
Unified query analyzer that combines query execution, insights detection,
EXPLAIN analysis, and optimization suggestions.
"""

import re
from dataclasses import dataclass, field
from typing import Any

from app.engine.query_parser import parse_query, ParsedQuery
from app.engine.query_executor import QueryExecutor, QueryResult
from app.engine.explain import generate_explain, ExplainRow, ExplainAnnotation
from app.engine.errors import QueryError


@dataclass
class QueryIssue:
    """A detected anti-pattern or issue in the query."""
    severity: str  # 'info', 'warning', 'error'
    title: str
    description: str
    fix: str | None = None


@dataclass
class IndexRecommendation:
    """A recommended index to improve query performance."""
    type: str  # 'WHERE filter', 'Composite', 'Covering', 'ORDER BY'
    columns: list[str]
    table: str
    sql: str
    reason: str


@dataclass
class QueryRewrite:
    """A suggested query rewrite for better performance."""
    original_pattern: str
    rewritten: str
    reason: str
    improvement: str


@dataclass
class QueryAnalysis:
    """Complete analysis of a query."""
    # Execution results
    result: QueryResult | None = None
    error: dict | None = None

    # Parsed query info
    parsed: ParsedQuery | None = None

    # Detected issues (from pattern detection)
    issues: list[QueryIssue] = field(default_factory=list)
    overall_severity: str = 'good'  # 'good', 'warning', 'critical'

    # EXPLAIN analysis
    explain_rows: list[ExplainRow] = field(default_factory=list)
    explain_annotations: list[ExplainAnnotation] = field(default_factory=list)
    access_rating: str = 'good'  # 'good', 'caution', 'bad'

    # Optimization suggestions
    index_recommendations: list[IndexRecommendation] = field(default_factory=list)
    rewrites: list[QueryRewrite] = field(default_factory=list)
    optimized_query: str | None = None
    tips: list[str] = field(default_factory=list)


def analyze_query(query: str, dataset: Any) -> QueryAnalysis:
    """
    Run full analysis on a query.

    Args:
        query: SQL query string
        dataset: Dataset instance

    Returns:
        QueryAnalysis with all insights
    """
    analysis = QueryAnalysis()

    if not query or not query.strip():
        analysis.error = {
            'message': 'Please enter a query',
            'suggestion': 'Try: SELECT * FROM employees'
        }
        return analysis

    # Parse the query
    try:
        parsed = parse_query(query)
        analysis.parsed = parsed
    except Exception as e:
        analysis.error = {
            'message': f'Syntax error: {str(e)}',
            'suggestion': 'Check your SQL syntax'
        }
        return analysis

    # Execute the query
    executor = QueryExecutor(dataset)
    try:
        analysis.result = executor.execute(query)
    except QueryError as e:
        analysis.error = {
            'message': e.message,
            'suggestion': e.suggestion,
            'error_type': e.error_type,
            'context': e.context
        }
        # Continue with analysis even if execution fails

    # Detect issues/anti-patterns
    analysis.issues = _detect_issues(query, parsed)
    analysis.overall_severity = _calculate_overall_severity(analysis.issues)

    # Generate EXPLAIN analysis
    if parsed.tables:
        try:
            explain_rows, annotations = generate_explain(parsed, dataset)
            analysis.explain_rows = explain_rows
            analysis.explain_annotations = annotations
            analysis.access_rating = _calculate_access_rating(explain_rows)
        except Exception:
            pass  # Skip EXPLAIN if it fails

    # Generate optimization suggestions
    analysis.index_recommendations = _generate_index_recommendations(parsed, dataset)
    analysis.rewrites = _generate_rewrites(query, parsed)
    analysis.optimized_query = _generate_optimized_query(query, parsed, analysis.issues)
    analysis.tips = _generate_tips(analysis)

    return analysis


def _detect_issues(query: str, parsed: ParsedQuery) -> list[QueryIssue]:
    """Detect anti-patterns and issues in the query."""
    issues = []
    query_upper = query.upper()

    # SELECT * anti-pattern
    if '*' in parsed.columns:
        issues.append(QueryIssue(
            severity='warning',
            title='SELECT * Usage',
            description='Fetching all columns when you might only need specific ones.',
            fix='List only the columns you need: SELECT id, name, salary FROM ...'
        ))

    # Function on indexed column
    function_patterns = ['YEAR(', 'MONTH(', 'DATE(', 'UPPER(', 'LOWER(', 'CONCAT(']
    for func in function_patterns:
        if func in query_upper:
            issues.append(QueryIssue(
                severity='error',
                title=f'Function on Column: {func})',
                description='Using functions on columns prevents index usage. MySQL must scan all rows.',
                fix=f'Rewrite to compare against a range instead of using {func})'
            ))
            break

    # Leading wildcard LIKE
    if "LIKE '%" in query or 'LIKE "%' in query:
        issues.append(QueryIssue(
            severity='error',
            title='Leading Wildcard LIKE',
            description="LIKE '%value' or LIKE '%value%' cannot use B-tree indexes.",
            fix="Use trailing wildcard LIKE 'value%' or consider FULLTEXT index"
        ))

    # OR on different columns
    if ' OR ' in query_upper and len(parsed.where_conditions) > 1:
        cols = set(c.get('column', '') for c in parsed.where_conditions)
        if len(cols) > 1:
            issues.append(QueryIssue(
                severity='warning',
                title='OR on Different Columns',
                description='OR conditions on different columns often prevent efficient index usage.',
                fix='Consider UNION of separate queries, each using its own index'
            ))

    # NOT IN
    if 'NOT IN' in query_upper:
        issues.append(QueryIssue(
            severity='warning',
            title='NOT IN Usage',
            description='NOT IN can have unexpected behavior with NULL values and may not use indexes efficiently.',
            fix='Use NOT EXISTS for safer NULL handling and potentially better performance'
        ))

    # ORDER BY without LIMIT
    if parsed.order_by and not parsed.limit:
        issues.append(QueryIssue(
            severity='warning',
            title='ORDER BY Without LIMIT',
            description='Sorting all rows without a LIMIT can be expensive for large tables.',
            fix='Add LIMIT to retrieve only the rows you need'
        ))

    # DISTINCT overuse
    if 'DISTINCT' in query_upper:
        issues.append(QueryIssue(
            severity='info',
            title='DISTINCT Usage',
            description='DISTINCT requires sorting/hashing all results. Sometimes it indicates a JOIN issue.',
            fix='Verify if DISTINCT is necessary or if the JOIN logic can be fixed'
        ))

    # Subquery in SELECT
    if 'SELECT' in query_upper[query_upper.find('SELECT') + 6:]:
        issues.append(QueryIssue(
            severity='info',
            title='Subquery Detected',
            description='Subqueries can sometimes be rewritten as JOINs for better performance.',
            fix='Consider whether a JOIN would be more efficient'
        ))

    # No WHERE clause on large table
    if not parsed.where_conditions and parsed.tables:
        issues.append(QueryIssue(
            severity='info',
            title='No WHERE Clause',
            description='Query will scan the entire table. This is fine for small tables.',
            fix='Add filtering conditions if you need specific rows'
        ))

    return issues


def _calculate_overall_severity(issues: list[QueryIssue]) -> str:
    """Calculate overall severity based on detected issues."""
    if not issues:
        return 'good'

    severities = [i.severity for i in issues]
    if 'error' in severities:
        return 'critical'
    if 'warning' in severities:
        return 'warning'
    return 'good'


def _calculate_access_rating(explain_rows: list[ExplainRow]) -> str:
    """Calculate overall access rating from EXPLAIN rows."""
    if not explain_rows:
        return 'good'

    ratings = [row.get_type_rating() for row in explain_rows]
    if 'bad' in ratings:
        return 'bad'
    if 'caution' in ratings:
        return 'caution'
    return 'good'


def _generate_index_recommendations(parsed: ParsedQuery, dataset: Any) -> list[IndexRecommendation]:
    """Generate index recommendations based on query patterns."""
    recommendations = []

    if not parsed.tables:
        return recommendations

    table = parsed.tables[0]
    existing_indexes = dataset.indexes.get(table, {}) if hasattr(dataset, 'indexes') else {}
    existing_cols = set(idx[0] for idx in existing_indexes.values())

    # WHERE clause indexes
    where_cols = [c.get('column') for c in parsed.where_conditions if c.get('column')]
    for col in where_cols:
        if col and col not in existing_cols:
            recommendations.append(IndexRecommendation(
                type='WHERE filter',
                columns=[col],
                table=table,
                sql=f"CREATE INDEX idx_{table}_{col} ON {table}({col});",
                reason=f"Query filters on '{col}' - an index would speed up row lookup"
            ))

    # ORDER BY index
    if parsed.order_by:
        order_cols = [c[0] for c in parsed.order_by]
        if order_cols and order_cols[0] not in existing_cols:
            recommendations.append(IndexRecommendation(
                type='ORDER BY',
                columns=order_cols,
                table=table,
                sql=f"CREATE INDEX idx_{table}_{'_'.join(order_cols)} ON {table}({', '.join(order_cols)});",
                reason=f"Index on ORDER BY columns avoids filesort"
            ))

    # Composite index for WHERE + ORDER BY
    if where_cols and parsed.order_by:
        order_cols = [c[0] for c in parsed.order_by]
        all_cols = where_cols + [c for c in order_cols if c not in where_cols]
        if len(all_cols) > 1:
            recommendations.append(IndexRecommendation(
                type='Composite',
                columns=all_cols,
                table=table,
                sql=f"CREATE INDEX idx_{table}_composite ON {table}({', '.join(all_cols)});",
                reason='Composite index covers both WHERE and ORDER BY in one index'
            ))

    # Covering index
    if parsed.columns != ['*'] and len(parsed.columns) <= 5:
        select_cols = [_extract_column_name(c) for c in parsed.columns if _extract_column_name(c)]
        all_needed = list(set(select_cols + where_cols))
        if len(all_needed) <= 5 and len(all_needed) > 1:
            recommendations.append(IndexRecommendation(
                type='Covering',
                columns=all_needed,
                table=table,
                sql=f"CREATE INDEX idx_{table}_covering ON {table}({', '.join(all_needed)});",
                reason='Covering index includes all needed columns - query can be answered from index alone'
            ))

    # Return top 3 recommendations
    return recommendations[:3]


def _extract_column_name(col_expr: str) -> str | None:
    """Extract column name from expression."""
    col_expr = col_expr.strip()

    # Handle aliases
    if ' AS ' in col_expr.upper():
        col_expr = re.split(r'\s+AS\s+', col_expr, flags=re.IGNORECASE)[0].strip()

    # Handle table.column
    if '.' in col_expr:
        return col_expr.split('.')[-1].strip()

    # Handle functions
    match = re.match(r'\w+\(([^)]+)\)', col_expr)
    if match:
        inner = match.group(1).strip()
        if inner == '*':
            return None
        if '.' in inner:
            return inner.split('.')[-1].strip()
        return inner

    return col_expr.strip() if col_expr else None


def _generate_rewrites(query: str, parsed: ParsedQuery) -> list[QueryRewrite]:
    """Generate query rewrite suggestions."""
    rewrites = []
    query_upper = query.upper()

    # SELECT * rewrite
    if '*' in parsed.columns and parsed.tables:
        rewrites.append(QueryRewrite(
            original_pattern='SELECT *',
            rewritten=f"SELECT id, name, ... FROM {parsed.tables[0]}",
            reason='Specify only needed columns',
            improvement='Reduces data transfer and enables covering indexes'
        ))

    # YEAR() function rewrite
    if 'YEAR(' in query_upper:
        match = re.search(r"YEAR\((\w+)\)\s*=\s*(\d{4})", query, re.IGNORECASE)
        if match:
            col, year = match.groups()
            rewrites.append(QueryRewrite(
                original_pattern=f"YEAR({col}) = {year}",
                rewritten=f"{col} >= '{year}-01-01' AND {col} < '{int(year)+1}-01-01'",
                reason='Avoid function on column',
                improvement='Allows index usage on the date column'
            ))

    # Leading wildcard LIKE rewrite
    if "LIKE '%" in query or 'LIKE "%' in query:
        rewrites.append(QueryRewrite(
            original_pattern="LIKE '%value%'",
            rewritten="LIKE 'value%' (if possible) or use FULLTEXT INDEX",
            reason='Leading wildcard prevents B-tree index usage',
            improvement='Trailing wildcard can use B-tree index'
        ))

    # NOT IN rewrite
    if 'NOT IN' in query_upper:
        rewrites.append(QueryRewrite(
            original_pattern='NOT IN (subquery)',
            rewritten='NOT EXISTS (SELECT 1 FROM ... WHERE ...)',
            reason='NOT IN can fail with NULLs',
            improvement='NOT EXISTS handles NULLs correctly and may be faster'
        ))

    # OR to UNION rewrite
    if ' OR ' in query_upper and len(parsed.where_conditions) > 1:
        cols = set(c.get('column', '') for c in parsed.where_conditions)
        if len(cols) > 1:
            rewrites.append(QueryRewrite(
                original_pattern='WHERE col1 = x OR col2 = y',
                rewritten='(SELECT ... WHERE col1 = x) UNION (SELECT ... WHERE col2 = y)',
                reason='OR on different columns prevents single index usage',
                improvement='UNION allows each query to use its own index'
            ))

    return rewrites


def _generate_optimized_query(query: str, parsed: ParsedQuery, issues: list[QueryIssue]) -> str | None:
    """Generate an optimized version of the query if possible."""
    if not issues:
        return None

    optimized = query

    # Replace SELECT * with specific columns (if we can determine them)
    if any(i.title == 'SELECT * Usage' for i in issues) and parsed.tables:
        # We don't know which columns the user actually needs, so just show placeholder
        return None

    # Replace YEAR() function
    match = re.search(r"YEAR\((\w+)\)\s*=\s*(\d{4})", query, re.IGNORECASE)
    if match:
        col, year = match.groups()
        old_pattern = match.group(0)
        new_pattern = f"{col} >= '{year}-01-01' AND {col} < '{int(year)+1}-01-01'"
        optimized = re.sub(re.escape(old_pattern), new_pattern, optimized, flags=re.IGNORECASE)
        return optimized

    return None


def _generate_tips(analysis: QueryAnalysis) -> list[str]:
    """Generate performance tips based on analysis."""
    tips = []

    if analysis.access_rating == 'bad':
        tips.append("Consider adding indexes on filtered columns to avoid full table scans")

    if any(i.title == 'SELECT * Usage' for i in analysis.issues):
        tips.append("Selecting specific columns reduces I/O and memory usage")

    if analysis.explain_rows:
        for row in analysis.explain_rows:
            if 'Using filesort' in row.extra:
                tips.append("Add an index that matches your ORDER BY to avoid filesort")
            if 'Using temporary' in row.extra:
                tips.append("GROUP BY and ORDER BY on different columns causes temporary tables")

    if analysis.result and analysis.result.row_count > 100:
        tips.append("Consider adding LIMIT if you don't need all rows")

    if not tips:
        tips.append("Query looks reasonable! Check actual execution time on production data.")

    return tips
