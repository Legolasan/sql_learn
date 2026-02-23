"""
Data Types & Nulls concept - Understanding MySQL data types and NULL semantics.
Includes interactive NULL trap quiz demonstrations.
"""

from typing import Any
import re

from app.concepts.base import BaseConcept, Step


class DataTypesNullsConcept(BaseConcept):
    name = "data-types-nulls"
    display_name = "Data Types & NULLs"
    description = "Understand MySQL data types and master NULL semantics. Interactive quizzes reveal common NULL traps like COUNT(*) vs COUNT(col)."
    difficulty = "beginner"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        return {
            'query': query,

            # Data types reference
            'numeric_types': self._get_numeric_types(),
            'string_types': self._get_string_types(),
            'date_types': self._get_date_types(),
            'other_types': self._get_other_types(),

            # NULL semantics
            'null_basics': self._get_null_basics(),
            'null_operators': self._get_null_operators(),

            # Interactive NULL trap quizzes
            'null_traps': self._get_null_traps(),

            # Type conversion
            'type_conversion': self._get_type_conversion(),

            # Best practices
            'best_practices': self._get_best_practices(),
        }

    def _get_numeric_types(self) -> list[dict]:
        return [
            {
                'category': 'Integers',
                'types': [
                    {'name': 'TINYINT', 'range': '-128 to 127', 'unsigned': '0 to 255', 'bytes': 1, 'use': 'Boolean flags, small numbers'},
                    {'name': 'SMALLINT', 'range': '-32,768 to 32,767', 'unsigned': '0 to 65,535', 'bytes': 2, 'use': 'Small counters'},
                    {'name': 'MEDIUMINT', 'range': '-8M to 8M', 'unsigned': '0 to 16M', 'bytes': 3, 'use': 'Medium counters'},
                    {'name': 'INT', 'range': '-2B to 2B', 'unsigned': '0 to 4B', 'bytes': 4, 'use': 'Most common choice'},
                    {'name': 'BIGINT', 'range': '-9×10^18 to 9×10^18', 'unsigned': '0 to 18×10^18', 'bytes': 8, 'use': 'Very large numbers, auto_increment IDs'},
                ],
            },
            {
                'category': 'Decimals',
                'types': [
                    {'name': 'DECIMAL(M,D)', 'description': 'Exact fixed-point', 'example': 'DECIMAL(10,2) for money', 'use': 'Financial data, precise calculations'},
                    {'name': 'FLOAT', 'description': '4-byte floating point', 'precision': '~7 significant digits', 'use': 'Scientific data (approximate OK)'},
                    {'name': 'DOUBLE', 'description': '8-byte floating point', 'precision': '~15 significant digits', 'use': 'Higher precision floating point'},
                ],
                'warning': 'Never use FLOAT/DOUBLE for money! Use DECIMAL instead.',
            },
        ]

    def _get_string_types(self) -> list[dict]:
        return [
            {
                'name': 'CHAR(N)',
                'description': 'Fixed-length string',
                'max_length': '255 characters',
                'storage': 'Always uses N bytes',
                'example': "CHAR(2) for country codes: 'US', 'UK'",
                'pros': ['Slightly faster for fixed-length data'],
                'cons': ['Wastes space if data varies in length'],
            },
            {
                'name': 'VARCHAR(N)',
                'description': 'Variable-length string',
                'max_length': '65,535 characters (row limit)',
                'storage': 'Length + 1-2 bytes overhead',
                'example': "VARCHAR(100) for names",
                'pros': ['Efficient storage for varying lengths'],
                'cons': ['Slightly slower than CHAR'],
            },
            {
                'name': 'TEXT',
                'description': 'Large text storage',
                'max_length': '65,535 bytes (~64KB)',
                'storage': 'Stored separately from row',
                'example': 'Product descriptions, comments',
                'pros': ['Large capacity'],
                'cons': ['Cannot index fully, slower'],
            },
            {
                'name': 'MEDIUMTEXT / LONGTEXT',
                'description': 'Very large text',
                'max_length': '16MB / 4GB',
                'storage': 'Stored separately',
                'example': 'Full articles, documents',
                'pros': ['Huge capacity'],
                'cons': ['Performance considerations'],
            },
        ]

    def _get_date_types(self) -> list[dict]:
        return [
            {
                'name': 'DATE',
                'format': 'YYYY-MM-DD',
                'range': '1000-01-01 to 9999-12-31',
                'storage': '3 bytes',
                'example': "'2024-03-15'",
                'use': 'Dates without time (birthdays, deadlines)',
            },
            {
                'name': 'TIME',
                'format': 'HH:MM:SS',
                'range': '-838:59:59 to 838:59:59',
                'storage': '3 bytes',
                'example': "'14:30:00'",
                'use': 'Time of day, durations',
            },
            {
                'name': 'DATETIME',
                'format': 'YYYY-MM-DD HH:MM:SS',
                'range': '1000-01-01 to 9999-12-31',
                'storage': '8 bytes',
                'example': "'2024-03-15 14:30:00'",
                'use': 'Specific moments (no timezone)',
            },
            {
                'name': 'TIMESTAMP',
                'format': 'YYYY-MM-DD HH:MM:SS',
                'range': '1970-01-01 to 2038-01-19',
                'storage': '4 bytes',
                'example': "'2024-03-15 14:30:00'",
                'use': 'Auto-updating timestamps, timezone-aware',
                'special': 'Stored as UTC, converted to session timezone on retrieval',
            },
            {
                'name': 'YEAR',
                'format': 'YYYY',
                'range': '1901 to 2155',
                'storage': '1 byte',
                'example': "'2024'",
                'use': 'Year values only',
            },
        ]

    def _get_other_types(self) -> list[dict]:
        return [
            {
                'name': 'BOOLEAN / BOOL',
                'description': 'Actually TINYINT(1)',
                'values': 'TRUE (1), FALSE (0)',
                'note': 'MySQL has no native boolean; TRUE/FALSE are just aliases for 1/0',
            },
            {
                'name': 'ENUM',
                'description': 'One value from a defined list',
                'example': "ENUM('small', 'medium', 'large')",
                'storage': '1-2 bytes',
                'pros': 'Fast comparisons, enforces valid values',
                'cons': 'Changing the list requires ALTER TABLE',
            },
            {
                'name': 'SET',
                'description': 'Zero or more values from a list',
                'example': "SET('read', 'write', 'delete')",
                'storage': '1-8 bytes',
                'use': 'Multiple flags/permissions',
            },
            {
                'name': 'JSON',
                'description': 'Native JSON document storage',
                'example': '{"name": "John", "age": 30}',
                'since': 'MySQL 5.7+',
                'pros': 'Flexible schema, can query inside JSON',
                'cons': 'Less performant than columns',
            },
        ]

    def _get_null_basics(self) -> dict:
        return {
            'title': 'Understanding NULL',
            'definition': 'NULL represents the absence of a value. It is NOT zero, NOT an empty string, NOT false. NULL means "unknown" or "not applicable".',
            'key_rules': [
                {'rule': 'NULL = NULL is FALSE', 'explanation': 'Nothing equals NULL, not even NULL itself'},
                {'rule': 'NULL <> NULL is FALSE', 'explanation': 'NULL is not "not equal" to NULL either'},
                {'rule': 'NULL + 10 = NULL', 'explanation': 'Any arithmetic with NULL results in NULL'},
                {'rule': "NULL || 'text' = NULL", 'explanation': 'CONCAT with NULL produces NULL'},
                {'rule': 'NULL in WHERE evaluates to UNKNOWN', 'explanation': 'UNKNOWN is treated as FALSE for filtering'},
            ],
            'correct_usage': {
                'check_null': 'col IS NULL',
                'check_not_null': 'col IS NOT NULL',
                'coalesce': "COALESCE(col, 'default') -- Returns first non-NULL value",
                'ifnull': "IFNULL(col, 0) -- MySQL-specific alternative",
                'nullif': "NULLIF(col, 'N/A') -- Returns NULL if values match",
            },
        }

    def _get_null_operators(self) -> list[dict]:
        return [
            {'operator': 'IS NULL', 'correct': True, 'example': "WHERE phone IS NULL"},
            {'operator': 'IS NOT NULL', 'correct': True, 'example': "WHERE email IS NOT NULL"},
            {'operator': '= NULL', 'correct': False, 'example': "WHERE phone = NULL -- Always FALSE!"},
            {'operator': '<> NULL', 'correct': False, 'example': "WHERE phone <> NULL -- Always FALSE!"},
            {'operator': 'COALESCE(a, b, c)', 'correct': True, 'example': "COALESCE(phone, email, 'no contact')"},
            {'operator': 'IFNULL(a, b)', 'correct': True, 'example': "IFNULL(discount, 0)"},
            {'operator': '<=> (NULL-safe equal)', 'correct': True, 'example': "WHERE a <=> b -- Works with NULLs!"},
        ]

    def _get_null_traps(self) -> list[dict]:
        """Interactive quiz questions about NULL behavior."""
        return [
            {
                'id': 'count_trap',
                'title': 'COUNT(*) vs COUNT(column)',
                'scenario': "Table 'employees' has 20 rows. 3 employees have NULL phone numbers.",
                'question': "What does COUNT(phone) return?",
                'options': ['20', '17', '3', 'NULL'],
                'correct': '17',
                'explanation': 'COUNT(column) only counts non-NULL values. COUNT(*) counts all rows.',
                'demo_query': "SELECT COUNT(*) as all_rows, COUNT(phone) as phones FROM employees",
            },
            {
                'id': 'sum_trap',
                'title': 'SUM with NULL values',
                'scenario': "Table has discount values: 10, NULL, 20, NULL, 15",
                'question': "What does SUM(discount) return?",
                'options': ['45', '0', 'NULL', 'Error'],
                'correct': '45',
                'explanation': 'SUM ignores NULL values. It sums only the non-NULL values: 10+20+15=45.',
                'demo_query': "SELECT SUM(discount) FROM order_items",
            },
            {
                'id': 'avg_trap',
                'title': 'AVG with NULL values',
                'scenario': "Column has: 10, NULL, 20, NULL, 15 (5 rows total)",
                'question': "What does AVG(value) return?",
                'options': ['9 (45/5)', '15 (45/3)', 'NULL', '0'],
                'correct': '15 (45/3)',
                'explanation': 'AVG ignores NULLs in both sum AND count. It only averages non-NULL values.',
                'demo_query': "SELECT AVG(discount) FROM order_items",
            },
            {
                'id': 'concat_trap',
                'title': 'CONCAT with NULL',
                'scenario': "first_name = 'John', middle_name = NULL, last_name = 'Doe'",
                'question': "What does CONCAT(first_name, ' ', middle_name, ' ', last_name) return?",
                'options': ["'John Doe'", "'John  Doe'", "NULL", "'John NULL Doe'"],
                'correct': 'NULL',
                'explanation': "CONCAT returns NULL if ANY argument is NULL. Use CONCAT_WS or COALESCE instead.",
                'demo_query': "SELECT CONCAT(name, ' - ', phone) FROM employees WHERE phone IS NULL LIMIT 1",
                'fix': "CONCAT_WS(' ', first_name, middle_name, last_name) -- Skips NULLs",
            },
            {
                'id': 'where_not_equal',
                'title': 'WHERE with != and NULL',
                'scenario': "10 employees total. 3 have department_id = 1, 5 have other departments, 2 have NULL.",
                'question': "How many rows does WHERE department_id != 1 return?",
                'options': ['7 (all non-1)', '5 (only non-NULL, non-1)', '2 (NULLs)', '10'],
                'correct': '5 (only non-NULL, non-1)',
                'explanation': "!= NULL evaluates to UNKNOWN (treated as FALSE). NULLs are excluded!",
                'demo_query': "SELECT COUNT(*) FROM employees WHERE department_id != 1",
                'fix': "WHERE department_id != 1 OR department_id IS NULL",
            },
            {
                'id': 'not_in_trap',
                'title': 'NOT IN with NULL in list',
                'scenario': "You run: WHERE id NOT IN (1, 2, NULL)",
                'question': "How many rows are returned?",
                'options': ['All except 1 and 2', 'None (0 rows)', 'All rows', 'Error'],
                'correct': 'None (0 rows)',
                'explanation': "NOT IN with NULL returns no rows! x NOT IN (1, NULL) = x != 1 AND x != NULL = UNKNOWN",
                'demo_query': "SELECT * FROM employees WHERE id NOT IN (1, 2, NULL)",
                'fix': "Ensure subqueries used in NOT IN cannot return NULL",
            },
            {
                'id': 'order_by_null',
                'title': 'ORDER BY with NULLs',
                'scenario': "Sorting a column that has some NULL values",
                'question': "Where do NULLs appear with ORDER BY col ASC?",
                'options': ['First', 'Last', 'Excluded', 'Error'],
                'correct': 'First',
                'explanation': "In MySQL, NULLs sort FIRST with ASC, LAST with DESC. Use COALESCE or IS NULL in ORDER BY to control placement.",
                'demo_query': "SELECT name, phone FROM employees ORDER BY phone ASC LIMIT 5",
                'fix': "ORDER BY phone IS NULL, phone ASC -- NULLs last",
            },
        ]

    def _get_type_conversion(self) -> dict:
        return {
            'title': 'Type Conversion',
            'implicit': {
                'description': 'MySQL automatically converts types when needed',
                'examples': [
                    {'expression': "'10' + 5", 'result': '15', 'note': 'String to number'},
                    {'expression': "1 = '1'", 'result': 'TRUE', 'note': 'Comparison converts'},
                    {'expression': "'abc' + 0", 'result': '0', 'note': "Non-numeric string = 0"},
                ],
                'warning': 'Implicit conversion can cause unexpected results and prevent index usage!',
            },
            'explicit': {
                'description': 'Use CAST() or CONVERT() for explicit conversion',
                'examples': [
                    {'sql': "CAST('2024-03-15' AS DATE)", 'purpose': 'String to date'},
                    {'sql': "CAST(price AS SIGNED)", 'purpose': 'Decimal to integer'},
                    {'sql': "CAST(123 AS CHAR)", 'purpose': 'Number to string'},
                    {'sql': "CONVERT(col, DECIMAL(10,2))", 'purpose': 'Alternative syntax'},
                ],
            },
        }

    def _get_best_practices(self) -> list[dict]:
        return [
            {
                'practice': 'Choose the smallest type that fits',
                'why': 'Smaller types = faster queries, less storage',
                'example': 'Use TINYINT for status flags, not INT',
            },
            {
                'practice': 'Use DECIMAL for money',
                'why': 'FLOAT/DOUBLE have rounding errors',
                'example': 'DECIMAL(10,2) for up to 99,999,999.99',
            },
            {
                'practice': 'Use VARCHAR over CHAR for variable data',
                'why': 'CHAR pads with spaces, wastes storage',
                'example': 'VARCHAR(100) for names, CHAR(2) for codes',
            },
            {
                'practice': 'Consider NOT NULL constraints',
                'why': 'Avoids NULL trap bugs, clearer intent',
                'example': "status VARCHAR(20) NOT NULL DEFAULT 'active'",
            },
            {
                'practice': 'Use TIMESTAMP for auto-updated times',
                'why': 'Automatically updates, timezone-aware',
                'example': 'updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP',
            },
            {
                'practice': 'Be explicit with COALESCE for NULLs',
                'why': 'Prevents NULL from propagating unexpectedly',
                'example': 'COALESCE(discount, 0) * quantity',
            },
        ]

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        return [
            Step(
                title="Data Types Overview",
                description="MySQL has numeric, string, date/time, and special types. Choose the right type for performance and data integrity.",
                highlight={'section': 'types'}
            ),
            Step(
                title="What is NULL?",
                description="NULL is not zero, not empty string, not false. NULL means 'unknown' or 'not applicable'.",
                highlight={'section': 'null_basics'}
            ),
            Step(
                title="NULL Trap: COUNT",
                description="COUNT(*) counts all rows. COUNT(column) counts only non-NULL values. This is a common source of bugs!",
                highlight={'trap': 'count_trap'}
            ),
            Step(
                title="NULL Trap: Aggregates",
                description="SUM, AVG, MIN, MAX all ignore NULL values. AVG divides by non-NULL count only.",
                highlight={'trap': 'aggregates'}
            ),
            Step(
                title="NULL Trap: Comparisons",
                description="NULL = NULL is FALSE! Use IS NULL / IS NOT NULL. The <=> operator is NULL-safe.",
                highlight={'trap': 'comparisons'}
            ),
            Step(
                title="NULL Trap: NOT IN",
                description="NOT IN with NULL in the list returns zero rows! Be careful with subqueries.",
                highlight={'trap': 'not_in'}
            ),
            Step(
                title="Best Practices",
                description="Choose appropriate types, use NOT NULL when possible, use COALESCE to handle NULLs explicitly.",
                highlight={'section': 'best_practices'}
            ),
        ]

    def get_sample_queries(self) -> list[str]:
        return [
            # COUNT trap
            "SELECT COUNT(*) as total, COUNT(phone) as with_phone FROM employees",
            "SELECT COUNT(*) as total, COUNT(email) as with_email FROM employees",

            # NULL in WHERE
            "SELECT name, phone FROM employees WHERE phone IS NULL",
            "SELECT name, phone FROM employees WHERE phone IS NOT NULL",

            # COALESCE
            "SELECT name, COALESCE(phone, 'No phone') as contact FROM employees",
            "SELECT name, IFNULL(phone, email) as contact FROM employees",

            # NULL in aggregates
            "SELECT AVG(discount), SUM(discount), COUNT(discount) FROM order_items",

            # NULL-safe comparison
            "SELECT * FROM employees WHERE manager_id <=> NULL",

            # ORDER BY with NULLs
            "SELECT name, phone FROM employees ORDER BY phone ASC",
            "SELECT name, phone FROM employees ORDER BY phone IS NULL, phone ASC",
        ]
