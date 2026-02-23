"""Index types visualization concept."""

from typing import Any

from app.concepts.base import BaseConcept, Step


class IndexTypesConcept(BaseConcept):
    name = "index-types"
    display_name = "Index Types"
    description = "Compare B-Tree, Hash, Full-Text, and Spatial indexes. Learn when to use each type."
    difficulty = "intermediate"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        # Parse to see what kind of query this is
        query_upper = query.upper()

        # Determine which index type would be best
        recommended_index = self._recommend_index(query_upper)

        index_types = [
            {
                'name': 'B-Tree',
                'description': 'Default index type. Stores data in a balanced tree structure.',
                'best_for': [
                    'Equality comparisons (=)',
                    'Range queries (>, <, BETWEEN)',
                    'Sorting (ORDER BY)',
                    'Leftmost prefix matching (LIKE "abc%")'
                ],
                'not_for': [
                    'Full-text search',
                    'Suffix matching (LIKE "%abc")',
                    'Spatial data'
                ],
                'complexity': 'O(log n) for search',
                'example_query': "SELECT * FROM users WHERE age > 25",
                'create_syntax': "CREATE INDEX idx_age ON users(age);",
                'visual': 'tree',
                'is_recommended': recommended_index == 'btree'
            },
            {
                'name': 'Hash',
                'description': 'Uses hash function for exact lookups. Memory tables only in MySQL.',
                'best_for': [
                    'Exact equality (=)',
                    'Very fast point lookups',
                    'Memory/HEAP tables'
                ],
                'not_for': [
                    'Range queries (>, <)',
                    'Sorting',
                    'Partial matching',
                    'InnoDB tables (uses B-Tree internally)'
                ],
                'complexity': 'O(1) for exact match',
                'example_query': "SELECT * FROM cache WHERE key = 'session_123'",
                'create_syntax': "CREATE INDEX idx_key USING HASH ON cache(key);",
                'visual': 'hash',
                'is_recommended': recommended_index == 'hash'
            },
            {
                'name': 'Full-Text',
                'description': 'Specialized for text search. Builds inverted index of words.',
                'best_for': [
                    'Natural language search',
                    'Boolean text search',
                    'Relevance ranking',
                    'Large text columns'
                ],
                'not_for': [
                    'Exact string matching',
                    'Numeric comparisons',
                    'Short strings'
                ],
                'complexity': 'Varies by search complexity',
                'example_query': "SELECT * FROM articles WHERE MATCH(content) AGAINST('database optimization')",
                'create_syntax': "CREATE FULLTEXT INDEX idx_content ON articles(content);",
                'visual': 'inverted',
                'is_recommended': recommended_index == 'fulltext'
            },
            {
                'name': 'Spatial (R-Tree)',
                'description': 'For geographic/geometric data. Organizes data by bounding boxes.',
                'best_for': [
                    'Geographic queries',
                    'Finding nearby points',
                    'Containment queries',
                    'GIS applications'
                ],
                'not_for': [
                    'Non-spatial data',
                    'Text search',
                    'Simple numeric ranges'
                ],
                'complexity': 'O(log n) for spatial queries',
                'example_query': "SELECT * FROM stores WHERE ST_Contains(region, point)",
                'create_syntax': "CREATE SPATIAL INDEX idx_location ON stores(location);",
                'visual': 'rtree',
                'is_recommended': recommended_index == 'spatial'
            },
        ]

        # Composite index info
        composite_info = {
            'title': 'Composite (Multi-Column) Indexes',
            'description': 'Index on multiple columns. Column order matters!',
            'example': "CREATE INDEX idx_name_age ON users(last_name, first_name, age);",
            'rules': [
                'Leftmost prefix rule: Index is used only from left to right',
                'Index on (a, b, c) works for: (a), (a, b), (a, b, c)',
                'Does NOT work for: (b), (c), (b, c)',
                'Put high-selectivity columns first',
                'Put equality conditions before range conditions'
            ],
            'visual_example': [
                {'columns': '(last_name, first_name, age)', 'query': 'WHERE last_name = "Smith"', 'uses_index': True},
                {'columns': '(last_name, first_name, age)', 'query': 'WHERE first_name = "John"', 'uses_index': False},
                {'columns': '(last_name, first_name, age)', 'query': 'WHERE last_name = "Smith" AND age > 25', 'uses_index': 'Partial'},
            ]
        }

        # Covering index info
        covering_info = {
            'title': 'Covering Indexes',
            'description': 'When the index contains ALL columns needed by the query.',
            'benefit': 'No need to access the table - everything is in the index!',
            'example': {
                'index': "CREATE INDEX idx_cover ON orders(customer_id, order_date, total);",
                'query': "SELECT order_date, total FROM orders WHERE customer_id = 123;",
                'explanation': "Index has customer_id (filter), order_date, total (selected) - no table access needed!"
            },
            'explain_sign': 'Look for "Using index" in EXPLAIN Extra column'
        }

        return {
            'query': query,
            'index_types': index_types,
            'recommended': recommended_index,
            'composite_info': composite_info,
            'covering_info': covering_info
        }

    def _recommend_index(self, query: str) -> str:
        if 'MATCH' in query and 'AGAINST' in query:
            return 'fulltext'
        elif 'ST_' in query or 'SPATIAL' in query or 'POINT' in query:
            return 'spatial'
        elif '=' in query and '>' not in query and '<' not in query and 'BETWEEN' not in query:
            return 'hash'  # Though B-Tree is usually fine too
        else:
            return 'btree'

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        viz_data = self.get_visualization_data(query, dataset)

        steps = [
            Step(
                title="Analyze Query Pattern",
                description=f"Looking at your query to determine best index type...",
                highlight={'analysis': True}
            )
        ]

        for idx_type in viz_data['index_types']:
            if idx_type['is_recommended']:
                steps.append(Step(
                    title=f"Recommended: {idx_type['name']}",
                    description=f"{idx_type['description']} Best for your query pattern.",
                    highlight={'type': idx_type['name']}
                ))
                steps.append(Step(
                    title=f"Why {idx_type['name']}?",
                    description=f"Good for: {', '.join(idx_type['best_for'][:2])}",
                    highlight={'reasons': True}
                ))

        steps.append(Step(
            title="Consider Composite Index",
            description="If filtering on multiple columns, a multi-column index might help.",
            highlight={'composite': True}
        ))

        steps.append(Step(
            title="Covering Index Opportunity",
            description="If you SELECT specific columns, include them in the index to avoid table access.",
            highlight={'covering': True}
        ))

        return steps

    def get_sample_queries(self) -> list[str]:
        return [
            "SELECT * FROM employees WHERE salary > 50000 ORDER BY salary",
            "SELECT * FROM employees WHERE id = 5",
            "SELECT * FROM products WHERE MATCH(description) AGAINST('wireless headphones')",
            "SELECT name, salary FROM employees WHERE department_id = 1",
        ]
