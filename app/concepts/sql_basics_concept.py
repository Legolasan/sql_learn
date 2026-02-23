"""
SQL Basics concept - Comprehensive coverage of fundamental SQL operations.
Covers SELECT, WHERE, ORDER BY, LIMIT, and common operators.
"""

from typing import Any
import re

from app.concepts.base import BaseConcept, Step


class SQLBasicsConcept(BaseConcept):
    name = "sql-basics"
    display_name = "SQL Basics"
    description = "Master the fundamentals: SELECT, WHERE, ORDER BY, LIMIT. Learn filtering with AND/OR, IN, BETWEEN, LIKE, and pattern matching."
    difficulty = "beginner"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        query_upper = query.upper()

        # Detect query components
        has_select = 'SELECT' in query_upper
        has_where = 'WHERE' in query_upper
        has_order_by = 'ORDER BY' in query_upper
        has_limit = 'LIMIT' in query_upper
        has_offset = 'OFFSET' in query_upper
        has_distinct = 'DISTINCT' in query_upper

        # Detect operators
        operators_used = []
        if ' AND ' in query_upper:
            operators_used.append('AND')
        if ' OR ' in query_upper:
            operators_used.append('OR')
        if ' IN ' in query_upper or ' IN(' in query_upper:
            operators_used.append('IN')
        if ' BETWEEN ' in query_upper:
            operators_used.append('BETWEEN')
        if ' LIKE ' in query_upper:
            operators_used.append('LIKE')
        if ' REGEXP ' in query_upper or ' RLIKE ' in query_upper:
            operators_used.append('REGEXP')
        if ' NOT ' in query_upper:
            operators_used.append('NOT')
        if ' IS NULL' in query_upper:
            operators_used.append('IS NULL')
        if ' IS NOT NULL' in query_upper:
            operators_used.append('IS NOT NULL')

        return {
            'query': query,
            'components': {
                'select': has_select,
                'where': has_where,
                'order_by': has_order_by,
                'limit': has_limit,
                'offset': has_offset,
                'distinct': has_distinct,
            },
            'operators_used': operators_used,

            # Reference sections
            'select_syntax': self._get_select_syntax(),
            'where_operators': self._get_where_operators(),
            'pattern_matching': self._get_pattern_matching(),
            'order_limit': self._get_order_limit(),
            'aliases': self._get_aliases(),
            'common_mistakes': self._get_common_mistakes(),
            'quick_reference': self._get_quick_reference(),

            # Schema info
            'available_tables': self._get_available_tables(),
        }

    def _get_select_syntax(self) -> dict:
        return {
            'title': 'SELECT Statement Structure',
            'basic_syntax': '''SELECT [DISTINCT] column1, column2, ...
FROM table_name
[WHERE condition]
[ORDER BY column [ASC|DESC]]
[LIMIT count [OFFSET start]];''',
            'execution_order': [
                {'step': 1, 'clause': 'FROM', 'description': 'Identify the source table(s)'},
                {'step': 2, 'clause': 'WHERE', 'description': 'Filter rows that match conditions'},
                {'step': 3, 'clause': 'SELECT', 'description': 'Choose columns to return'},
                {'step': 4, 'clause': 'DISTINCT', 'description': 'Remove duplicate rows (if specified)'},
                {'step': 5, 'clause': 'ORDER BY', 'description': 'Sort the results'},
                {'step': 6, 'clause': 'LIMIT/OFFSET', 'description': 'Return only a subset of rows'},
            ],
            'select_variations': [
                {'syntax': 'SELECT *', 'meaning': 'Select all columns', 'note': 'Avoid in production - be explicit'},
                {'syntax': 'SELECT col1, col2', 'meaning': 'Select specific columns', 'note': 'Best practice'},
                {'syntax': 'SELECT DISTINCT col', 'meaning': 'Select unique values only', 'note': 'Removes duplicates'},
                {'syntax': 'SELECT col AS alias', 'meaning': 'Rename column in output', 'note': 'Use for clarity'},
            ],
        }

    def _get_where_operators(self) -> list[dict]:
        return [
            {
                'category': 'Comparison Operators',
                'operators': [
                    {'op': '=', 'description': 'Equal to', 'example': "WHERE salary = 50000"},
                    {'op': '<> or !=', 'description': 'Not equal to', 'example': "WHERE status <> 'cancelled'"},
                    {'op': '<', 'description': 'Less than', 'example': "WHERE price < 100"},
                    {'op': '>', 'description': 'Greater than', 'example': "WHERE quantity > 10"},
                    {'op': '<=', 'description': 'Less than or equal', 'example': "WHERE age <= 65"},
                    {'op': '>=', 'description': 'Greater than or equal', 'example': "WHERE hire_date >= '2020-01-01'"},
                ],
            },
            {
                'category': 'Logical Operators',
                'operators': [
                    {'op': 'AND', 'description': 'Both conditions must be true', 'example': "WHERE salary > 50000 AND department_id = 1"},
                    {'op': 'OR', 'description': 'Either condition can be true', 'example': "WHERE city = 'NYC' OR city = 'LA'"},
                    {'op': 'NOT', 'description': 'Negates a condition', 'example': "WHERE NOT status = 'cancelled'"},
                ],
            },
            {
                'category': 'Range & Set Operators',
                'operators': [
                    {'op': 'BETWEEN', 'description': 'Value in range (inclusive)', 'example': "WHERE salary BETWEEN 50000 AND 80000"},
                    {'op': 'IN', 'description': 'Value matches any in list', 'example': "WHERE country IN ('USA', 'UK', 'Canada')"},
                    {'op': 'NOT IN', 'description': 'Value not in list', 'example': "WHERE status NOT IN ('cancelled', 'returned')"},
                ],
            },
            {
                'category': 'NULL Operators',
                'operators': [
                    {'op': 'IS NULL', 'description': 'Value is NULL', 'example': "WHERE phone IS NULL"},
                    {'op': 'IS NOT NULL', 'description': 'Value is not NULL', 'example': "WHERE email IS NOT NULL"},
                ],
                'warning': "Never use = NULL or != NULL - they don't work! Always use IS NULL / IS NOT NULL.",
            },
        ]

    def _get_pattern_matching(self) -> dict:
        return {
            'title': 'Pattern Matching',
            'like': {
                'description': 'Simple pattern matching with wildcards',
                'wildcards': [
                    {'char': '%', 'meaning': 'Any sequence of characters (0 or more)', 'example': "'%son' matches 'Wilson', 'Anderson'"},
                    {'char': '_', 'meaning': 'Any single character', 'example': "'_ob' matches 'Bob', 'Rob'"},
                ],
                'examples': [
                    {'pattern': "LIKE 'A%'", 'matches': 'Starts with A', 'sample': 'Alice, Acme'},
                    {'pattern': "LIKE '%son'", 'matches': 'Ends with son', 'sample': 'Wilson, Anderson'},
                    {'pattern': "LIKE '%tech%'", 'matches': 'Contains tech', 'sample': 'TechStart, Biotech'},
                    {'pattern': "LIKE 'J_n'", 'matches': 'J + any char + n', 'sample': 'Jon, Jan'},
                    {'pattern': "LIKE '___'", 'matches': 'Exactly 3 characters', 'sample': 'Bob, NYC'},
                ],
                'escape': "Use ESCAPE to match literal % or _: LIKE '%10\\%%' ESCAPE '\\\\'",
            },
            'regexp': {
                'description': 'Full regular expression support (more powerful than LIKE)',
                'syntax': "WHERE column REGEXP 'pattern'",
                'examples': [
                    {'pattern': "REGEXP '^A'", 'meaning': 'Starts with A'},
                    {'pattern': "REGEXP 'son$'", 'meaning': 'Ends with son'},
                    {'pattern': "REGEXP '[0-9]+'", 'meaning': 'Contains digits'},
                    {'pattern': "REGEXP '^[A-Z]{2,3}$'", 'meaning': '2-3 uppercase letters'},
                    {'pattern': "REGEXP 'cat|dog'", 'meaning': 'Contains cat or dog'},
                ],
                'note': 'REGEXP is case-insensitive by default. Use REGEXP BINARY for case-sensitive.',
            },
        }

    def _get_order_limit(self) -> dict:
        return {
            'title': 'Sorting & Pagination',
            'order_by': {
                'syntax': 'ORDER BY column [ASC|DESC], column2 [ASC|DESC]',
                'examples': [
                    {'sql': 'ORDER BY salary DESC', 'meaning': 'Highest salary first'},
                    {'sql': 'ORDER BY name ASC', 'meaning': 'Alphabetical A-Z (default)'},
                    {'sql': 'ORDER BY department_id, salary DESC', 'meaning': 'By dept, then by salary within dept'},
                    {'sql': 'ORDER BY 2', 'meaning': 'By 2nd column in SELECT (not recommended)'},
                ],
                'nulls': 'NULLs sort first with ASC, last with DESC in MySQL',
            },
            'limit': {
                'syntax': 'LIMIT count [OFFSET skip]',
                'alternative': 'LIMIT skip, count  (older syntax, confusing order!)',
                'examples': [
                    {'sql': 'LIMIT 10', 'meaning': 'First 10 rows'},
                    {'sql': 'LIMIT 10 OFFSET 20', 'meaning': 'Skip 20, return next 10 (page 3)'},
                    {'sql': 'LIMIT 20, 10', 'meaning': 'Same as above (skip, count) - avoid!'},
                ],
                'pagination_formula': 'Page N with size P: LIMIT P OFFSET (N-1)*P',
            },
        }

    def _get_aliases(self) -> dict:
        return {
            'title': 'Aliases & Quoting',
            'column_aliases': {
                'syntax': 'SELECT column AS alias_name',
                'examples': [
                    {'before': 'SELECT first_name', 'after': "SELECT first_name AS 'First Name'"},
                    {'before': 'SELECT COUNT(*)', 'after': 'SELECT COUNT(*) AS total_count'},
                    {'before': 'SELECT salary * 12', 'after': 'SELECT salary * 12 AS annual_salary'},
                ],
                'note': 'AS is optional but improves readability',
            },
            'table_aliases': {
                'syntax': 'FROM table_name AS t',
                'examples': [
                    {'sql': 'FROM employees AS e', 'usage': 'e.name, e.salary'},
                    {'sql': 'FROM order_items oi', 'usage': 'oi.quantity (AS is optional)'},
                ],
                'when': 'Required for self-joins, helpful for long table names',
            },
            'quoting': {
                'strings': "Use single quotes: 'Hello World'",
                'identifiers': 'Use backticks for reserved words: `order`, `select`',
                'reserved_words': ['ORDER', 'SELECT', 'FROM', 'WHERE', 'GROUP', 'BY', 'LIMIT', 'INDEX', 'KEY'],
                'tip': 'When in doubt, use backticks around column/table names',
            },
        }

    def _get_common_mistakes(self) -> list[dict]:
        return [
            {
                'mistake': 'Using = NULL instead of IS NULL',
                'wrong': "WHERE email = NULL",
                'right': "WHERE email IS NULL",
                'why': 'NULL is not a value, it\'s the absence of value. = never matches NULL.',
            },
            {
                'mistake': 'Forgetting quotes around strings',
                'wrong': "WHERE name = John",
                'right': "WHERE name = 'John'",
                'why': 'Unquoted text is interpreted as column names.',
            },
            {
                'mistake': 'Using double quotes for strings',
                'wrong': 'WHERE city = "New York"',
                'right': "WHERE city = 'New York'",
                'why': 'MySQL accepts both, but SQL standard uses single quotes. Double quotes are for identifiers in ANSI mode.',
            },
            {
                'mistake': 'Incorrect BETWEEN range',
                'wrong': 'WHERE date BETWEEN "2024-12-31" AND "2024-01-01"',
                'right': 'WHERE date BETWEEN "2024-01-01" AND "2024-12-31"',
                'why': 'BETWEEN requires low value first, high value second.',
            },
            {
                'mistake': 'Mixing AND/OR without parentheses',
                'wrong': "WHERE a = 1 OR b = 2 AND c = 3",
                'right': "WHERE a = 1 OR (b = 2 AND c = 3)",
                'why': 'AND has higher precedence. Use parentheses to make intent clear.',
            },
            {
                'mistake': 'LIMIT before ORDER BY',
                'wrong': 'SELECT * FROM emp LIMIT 5 ORDER BY salary',
                'right': 'SELECT * FROM emp ORDER BY salary LIMIT 5',
                'why': 'ORDER BY must come before LIMIT.',
            },
        ]

    def _get_quick_reference(self) -> dict:
        return {
            'title': 'Quick Reference Card',
            'sections': [
                {
                    'name': 'Basic Query',
                    'items': [
                        'SELECT * FROM table',
                        'SELECT col1, col2 FROM table',
                        'SELECT DISTINCT col FROM table',
                    ],
                },
                {
                    'name': 'Filtering',
                    'items': [
                        "WHERE col = 'value'",
                        'WHERE col > 100 AND col < 200',
                        "WHERE col IN ('a', 'b', 'c')",
                        'WHERE col BETWEEN 10 AND 20',
                        "WHERE col LIKE 'A%'",
                        'WHERE col IS NULL',
                    ],
                },
                {
                    'name': 'Sorting & Limiting',
                    'items': [
                        'ORDER BY col ASC',
                        'ORDER BY col DESC',
                        'ORDER BY col1, col2 DESC',
                        'LIMIT 10',
                        'LIMIT 10 OFFSET 20',
                    ],
                },
            ],
        }

    def _get_available_tables(self) -> list[dict]:
        return [
            {'name': 'employees', 'columns': 'id, name, department_id, manager_id, salary, hire_date, email, phone', 'rows': 20},
            {'name': 'departments', 'columns': 'id, name, budget, location', 'rows': 6},
            {'name': 'customers', 'columns': 'id, name, email, city, country, credit_limit, created_at', 'rows': 10},
            {'name': 'products', 'columns': 'id, name, category, price, stock_quantity, weight, is_active', 'rows': 12},
            {'name': 'orders', 'columns': 'id, customer_id, employee_id, order_date, shipped_date, status, notes', 'rows': 15},
            {'name': 'order_items', 'columns': 'id, order_id, product_id, quantity, unit_price, discount', 'rows': 26},
        ]

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        viz_data = self.get_visualization_data(query, dataset)

        steps = [
            Step(
                title="SELECT Basics",
                description="SELECT specifies which columns to retrieve. Use * for all columns, or list specific ones.",
                highlight={'section': 'select'}
            ),
            Step(
                title="FROM Clause",
                description="FROM identifies the source table. Every query needs exactly one table (for now - JOINs come later!).",
                highlight={'section': 'from'}
            ),
        ]

        if viz_data['components']['where']:
            steps.append(Step(
                title="WHERE Filtering",
                description=f"Your query uses: {', '.join(viz_data['operators_used']) or 'basic comparison'}",
                highlight={'section': 'where', 'operators': viz_data['operators_used']}
            ))

        if viz_data['components']['order_by']:
            steps.append(Step(
                title="ORDER BY Sorting",
                description="Results are sorted. ASC = ascending (default), DESC = descending.",
                highlight={'section': 'order_by'}
            ))

        if viz_data['components']['limit']:
            steps.append(Step(
                title="LIMIT/OFFSET",
                description="LIMIT restricts results. OFFSET skips rows (for pagination).",
                highlight={'section': 'limit'}
            ))

        steps.append(Step(
            title="Execution Complete",
            description="Query processed! Try modifying it to see different results.",
            highlight={'section': 'complete'}
        ))

        return steps

    def get_sample_queries(self) -> list[str]:
        return [
            # Basic SELECT
            "SELECT * FROM employees",
            "SELECT name, salary FROM employees",
            "SELECT DISTINCT department_id FROM employees",

            # WHERE with comparison
            "SELECT name, salary FROM employees WHERE salary > 80000",
            "SELECT * FROM products WHERE price < 100",

            # AND/OR
            "SELECT name FROM employees WHERE department_id = 1 AND salary > 90000",
            "SELECT name FROM customers WHERE country = 'USA' OR country = 'UK'",

            # IN/BETWEEN
            "SELECT * FROM orders WHERE status IN ('pending', 'processing')",
            "SELECT name, salary FROM employees WHERE salary BETWEEN 60000 AND 90000",

            # LIKE patterns
            "SELECT name FROM employees WHERE name LIKE 'A%'",
            "SELECT * FROM customers WHERE email LIKE '%@company.com'",

            # NULL checks
            "SELECT name FROM employees WHERE phone IS NULL",
            "SELECT * FROM orders WHERE shipped_date IS NOT NULL",

            # ORDER BY
            "SELECT name, salary FROM employees ORDER BY salary DESC",
            "SELECT * FROM products ORDER BY category, price DESC",

            # LIMIT/OFFSET
            "SELECT name, salary FROM employees ORDER BY salary DESC LIMIT 5",
            "SELECT * FROM orders ORDER BY order_date DESC LIMIT 10 OFFSET 5",

            # Aliases
            "SELECT name AS employee_name, salary AS annual_pay FROM employees",
        ]
