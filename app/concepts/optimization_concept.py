"""Query optimization visualization concept."""

from typing import Any

from app.concepts.base import BaseConcept, Step
from app.engine.query_parser import parse_query


class OptimizationConcept(BaseConcept):
    name = "optimization"
    display_name = "Query Optimization"
    description = "Learn to identify and fix slow queries. See anti-patterns and their optimized alternatives."
    difficulty = "advanced"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        parsed = parse_query(query)
        issues = self._detect_issues(query, parsed)

        # Optimization patterns
        patterns = [
            {
                'name': 'SELECT * Anti-Pattern',
                'bad': "SELECT * FROM employees WHERE department_id = 1",
                'good': "SELECT id, name, salary FROM employees WHERE department_id = 1",
                'why': "Fetches unnecessary columns, can't use covering index, more data transfer",
                'impact': 'medium',
                'detected': '*' in parsed.columns
            },
            {
                'name': 'Function on Indexed Column',
                'bad': "SELECT * FROM orders WHERE YEAR(order_date) = 2023",
                'good': "SELECT * FROM orders WHERE order_date >= '2023-01-01' AND order_date < '2024-01-01'",
                'why': "Functions prevent index usage - MySQL must scan all rows",
                'impact': 'high',
                'detected': any(func in query.upper() for func in ['YEAR(', 'MONTH(', 'DATE(', 'UPPER(', 'LOWER('])
            },
            {
                'name': 'Leading Wildcard LIKE',
                'bad': "SELECT * FROM products WHERE name LIKE '%phone%'",
                'good': "SELECT * FROM products WHERE name LIKE 'phone%'  -- or use FULLTEXT",
                'why': "Leading % prevents B-tree index usage",
                'impact': 'high',
                'detected': "LIKE '%" in query.upper() or 'LIKE "%' in query
            },
            {
                'name': 'OR on Different Columns',
                'bad': "SELECT * FROM users WHERE email = 'x' OR phone = 'y'",
                'good': "SELECT * FROM users WHERE email = 'x' UNION SELECT * FROM users WHERE phone = 'y'",
                'why': "OR often prevents index usage; UNION can use separate indexes",
                'impact': 'medium',
                'detected': ' OR ' in query.upper() and len(parsed.where_conditions) > 1
            },
            {
                'name': 'NOT IN with NULLs',
                'bad': "SELECT * FROM t1 WHERE id NOT IN (SELECT id FROM t2)",
                'good': "SELECT * FROM t1 WHERE NOT EXISTS (SELECT 1 FROM t2 WHERE t2.id = t1.id)",
                'why': "NOT IN returns no rows if subquery contains NULL; NOT EXISTS is safer",
                'impact': 'high',
                'detected': 'NOT IN' in query.upper()
            },
            {
                'name': 'Missing LIMIT on Large Result',
                'bad': "SELECT * FROM logs ORDER BY created_at DESC",
                'good': "SELECT * FROM logs ORDER BY created_at DESC LIMIT 100",
                'why': "Without LIMIT, sorts and returns all rows - very expensive",
                'impact': 'high',
                'detected': parsed.order_by and not parsed.limit
            },
            {
                'name': 'Implicit Type Conversion',
                'bad': "SELECT * FROM users WHERE phone = 1234567890  -- phone is VARCHAR",
                'good': "SELECT * FROM users WHERE phone = '1234567890'",
                'why': "Type mismatch forces conversion, prevents index usage",
                'impact': 'high',
                'detected': False  # Hard to detect without schema
            },
            {
                'name': 'SELECT DISTINCT Overuse',
                'bad': "SELECT DISTINCT * FROM employees JOIN departments ON ...",
                'good': "Fix the JOIN logic instead of masking duplicates with DISTINCT",
                'why': "DISTINCT requires sorting/hashing all results - expensive",
                'impact': 'medium',
                'detected': 'DISTINCT' in query.upper()
            },
        ]

        # Index recommendations
        index_recommendations = self._generate_index_recommendations(parsed)

        # Rewrite suggestions
        rewrites = self._suggest_rewrites(query, parsed)

        return {
            'query': query,
            'parsed': {
                'tables': parsed.tables,
                'columns': parsed.columns,
                'where': parsed.where_conditions,
                'order_by': parsed.order_by,
                'limit': parsed.limit
            },
            'issues': issues,
            'patterns': [p for p in patterns if p['detected']],
            'all_patterns': patterns,
            'index_recommendations': index_recommendations,
            'rewrites': rewrites,
            'checklist': self._get_optimization_checklist()
        }

    def _detect_issues(self, query: str, parsed) -> list[dict]:
        issues = []

        if '*' in parsed.columns:
            issues.append({
                'severity': 'warning',
                'issue': 'Using SELECT *',
                'fix': 'Specify only needed columns'
            })

        if parsed.order_by and not parsed.limit:
            issues.append({
                'severity': 'warning',
                'issue': 'ORDER BY without LIMIT',
                'fix': 'Add LIMIT to avoid sorting entire table'
            })

        if 'LIKE "%' in query or "LIKE '%" in query:
            issues.append({
                'severity': 'error',
                'issue': 'Leading wildcard in LIKE',
                'fix': 'Use trailing wildcard or FULLTEXT index'
            })

        for func in ['YEAR(', 'MONTH(', 'DATE(', 'UPPER(', 'LOWER(']:
            if func in query.upper():
                issues.append({
                    'severity': 'error',
                    'issue': f'Function {func}) on column',
                    'fix': 'Rewrite to avoid function on indexed column'
                })
                break

        return issues

    def _generate_index_recommendations(self, parsed) -> list[dict]:
        recommendations = []

        # Index for WHERE columns
        for cond in parsed.where_conditions:
            col = cond.get('column')
            if col:
                recommendations.append({
                    'type': 'WHERE filter',
                    'column': col,
                    'suggestion': f"CREATE INDEX idx_{col} ON {parsed.tables[0]}({col});" if parsed.tables else f"Index on {col}",
                    'reason': f"Query filters on {col}"
                })

        # Composite index for WHERE + ORDER BY
        if parsed.where_conditions and parsed.order_by:
            where_cols = [c['column'] for c in parsed.where_conditions]
            order_cols = [c[0] for c in parsed.order_by]
            all_cols = where_cols + [c for c in order_cols if c not in where_cols]
            if len(all_cols) > 1:
                recommendations.append({
                    'type': 'Composite',
                    'column': ', '.join(all_cols),
                    'suggestion': f"CREATE INDEX idx_composite ON {parsed.tables[0]}({', '.join(all_cols)});" if parsed.tables else "Composite index",
                    'reason': 'Covers both WHERE and ORDER BY'
                })

        # Covering index
        if parsed.columns != ['*'] and len(parsed.columns) <= 5:
            all_needed = list(set(parsed.columns + [c['column'] for c in parsed.where_conditions]))
            recommendations.append({
                'type': 'Covering',
                'column': ', '.join(all_needed),
                'suggestion': f"CREATE INDEX idx_covering ON {parsed.tables[0]}({', '.join(all_needed)});" if parsed.tables else "Covering index",
                'reason': 'All columns in index - no table access needed'
            })

        return recommendations[:3]  # Top 3 recommendations

    def _suggest_rewrites(self, query: str, parsed) -> list[dict]:
        rewrites = []

        if '*' in parsed.columns and parsed.tables:
            rewrites.append({
                'original': query,
                'rewritten': query.replace('SELECT *', 'SELECT id, name, ...'),  # Placeholder
                'reason': 'Specify columns for better performance'
            })

        return rewrites

    def _get_optimization_checklist(self) -> list[dict]:
        return [
            {'item': 'Use EXPLAIN to analyze query', 'priority': 1},
            {'item': 'Check for full table scans (type=ALL)', 'priority': 1},
            {'item': 'Verify indexes are being used', 'priority': 1},
            {'item': 'Look for "Using filesort" or "Using temporary"', 'priority': 2},
            {'item': 'Avoid SELECT * - specify columns', 'priority': 2},
            {'item': 'Add LIMIT when possible', 'priority': 2},
            {'item': 'Check for functions on indexed columns', 'priority': 2},
            {'item': 'Consider covering indexes', 'priority': 3},
            {'item': 'Review subqueries - can they be JOINs?', 'priority': 3},
            {'item': 'Check data types match (avoid implicit conversion)', 'priority': 3},
        ]

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        viz_data = self.get_visualization_data(query, dataset)

        steps = [
            Step(
                title="Analyze Query",
                description=f"Checking query against common anti-patterns...",
                highlight={'analyze': True}
            )
        ]

        if viz_data['issues']:
            for issue in viz_data['issues']:
                icon = '🔴' if issue['severity'] == 'error' else '🟡'
                steps.append(Step(
                    title=f"{icon} {issue['issue']}",
                    description=f"Fix: {issue['fix']}",
                    highlight={'issue': issue['issue']}
                ))
        else:
            steps.append(Step(
                title="✅ No major issues detected",
                description="Query looks reasonable. Check EXPLAIN for actual performance.",
                highlight={'clean': True}
            ))

        if viz_data['index_recommendations']:
            steps.append(Step(
                title="Index Recommendations",
                description=f"Found {len(viz_data['index_recommendations'])} potential indexes",
                highlight={'indexes': True}
            ))

        steps.append(Step(
            title="Next: Run EXPLAIN",
            description="Use the EXPLAIN concept to see actual query plan",
            highlight={'next': True}
        ))

        return steps

    def get_sample_queries(self) -> list[str]:
        return [
            "SELECT * FROM employees WHERE YEAR(hire_date) = 2020",
            "SELECT * FROM products WHERE name LIKE '%phone%'",
            "SELECT * FROM employees WHERE department_id = 1 OR salary > 80000",
            "SELECT * FROM logs ORDER BY created_at DESC",
            "SELECT DISTINCT * FROM employees JOIN orders ON employees.id = orders.employee_id",
        ]
