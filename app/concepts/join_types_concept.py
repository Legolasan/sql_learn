"""
Join Types Concept - Comprehensive JOIN education with animated visualizer.
Covers INNER, LEFT, RIGHT, CROSS, SELF JOIN, EXISTS (semi-join), NOT EXISTS (anti-join).
"""

from typing import Any

from app.concepts.base import BaseConcept, Step


class JoinTypesConcept(BaseConcept):
    """Comprehensive concept covering all JOIN types with visual animations."""

    name = "join-types"
    display_name = "Join Types & Patterns"
    description = "Master INNER, LEFT, RIGHT, CROSS, SELF joins plus semi/anti-join patterns with animated visualizations"
    difficulty = "intermediate"

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        return [
            Step(
                title="Why JOINs Exist",
                description="In relational databases, data is split across tables to reduce redundancy. JOINs reunite this data by matching rows based on related columns.",
                highlight={'section': 'overview'}
            ),
            Step(
                title="INNER JOIN",
                description="Returns only rows where both tables have matching values. Non-matching rows from either side are excluded.",
                highlight={'join_type': 'inner'}
            ),
            Step(
                title="LEFT JOIN",
                description="Returns ALL rows from the left table, plus matching rows from the right. Non-matching right rows appear as NULL.",
                highlight={'join_type': 'left'}
            ),
            Step(
                title="RIGHT JOIN",
                description="Returns ALL rows from the right table, plus matching rows from the left. Non-matching left rows appear as NULL.",
                highlight={'join_type': 'right'}
            ),
            Step(
                title="CROSS JOIN",
                description="Returns the Cartesian product - every row from the left combined with every row from the right. Use with caution!",
                highlight={'join_type': 'cross'}
            ),
            Step(
                title="SELF JOIN",
                description="Joins a table to itself. Useful for hierarchical data like employees with managers, or comparing rows within same table.",
                highlight={'section': 'self_join'}
            ),
            Step(
                title="Semi-Join (EXISTS)",
                description="Returns rows from the first table where at least one match exists in the second. Does NOT duplicate rows.",
                highlight={'section': 'semi_join'}
            ),
            Step(
                title="Anti-Join (NOT EXISTS)",
                description="Returns rows from the first table where NO match exists in the second. Finds orphaned records.",
                highlight={'section': 'anti_join'}
            ),
            Step(
                title="Row Multiplication",
                description="When JOINs create more rows than expected! Happens with one-to-many or many-to-many relationships.",
                highlight={'section': 'multiplication'}
            ),
        ]

    def get_sample_queries(self) -> list[str]:
        return [
            # INNER JOIN examples
            "SELECT e.name, d.name AS dept FROM employees e INNER JOIN departments d ON e.department_id = d.id",
            "SELECT o.id, c.name FROM orders o INNER JOIN customers c ON o.customer_id = c.id",

            # LEFT JOIN examples
            "SELECT e.name, d.name AS dept FROM employees e LEFT JOIN departments d ON e.department_id = d.id",
            "SELECT d.name, e.name FROM departments d LEFT JOIN employees e ON d.id = e.department_id",
            "SELECT c.name, o.id FROM customers c LEFT JOIN orders o ON c.id = o.customer_id",

            # RIGHT JOIN examples
            "SELECT e.name, d.name FROM employees e RIGHT JOIN departments d ON e.department_id = d.id",

            # CROSS JOIN examples
            "SELECT e.name, p.name FROM employees e CROSS JOIN products p LIMIT 20",

            # SELF JOIN examples
            "SELECT e.name AS employee, m.name AS manager FROM employees e LEFT JOIN employees m ON e.manager_id = m.id",

            # Semi-join (EXISTS)
            "SELECT d.name FROM departments d WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id)",

            # Anti-join (NOT EXISTS)
            "SELECT d.name FROM departments d WHERE NOT EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id)",
            "SELECT c.name FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)",

            # Multi-table joins
            "SELECT c.name, o.id, e.name AS handled_by FROM customers c JOIN orders o ON c.id = o.customer_id JOIN employees e ON o.employee_id = e.id",

            # Row multiplication demo
            "SELECT d.name, e.name FROM departments d JOIN employees e ON d.id = e.department_id ORDER BY d.name",
        ]

    def get_visualization_data(self, query: str, dataset) -> dict:
        """Generate visualization data for JOIN concepts."""
        from app.engine.query_parser import parse_query, QueryType

        # Detect join type from query
        detected_join = self._detect_join_type(query)

        return {
            "join_overview": self._get_join_overview(),
            "detected_join": detected_join,
            "join_details": self._get_join_details(detected_join),
            "animation_data": self._get_animation_data(detected_join, dataset),
            "venn_diagrams": self._get_venn_diagrams(),
            "row_multiplication": self._get_row_multiplication_demo(dataset),
            "semi_anti_joins": self._get_semi_anti_join_patterns(),
            "self_join_demo": self._get_self_join_demo(dataset),
            "common_mistakes": self._get_common_mistakes(),
            "performance_tips": self._get_performance_tips(),
        }

    def _detect_join_type(self, query: str) -> dict:
        """Detect the join type used in the query."""
        query_upper = query.upper()

        join_type = "none"
        has_exists = False
        has_not_exists = False
        is_self_join = False

        if "CROSS JOIN" in query_upper:
            join_type = "cross"
        elif "LEFT OUTER JOIN" in query_upper or "LEFT JOIN" in query_upper:
            join_type = "left"
        elif "RIGHT OUTER JOIN" in query_upper or "RIGHT JOIN" in query_upper:
            join_type = "right"
        elif "FULL OUTER JOIN" in query_upper or "FULL JOIN" in query_upper:
            join_type = "full"
        elif "INNER JOIN" in query_upper or " JOIN " in query_upper:
            join_type = "inner"

        if "NOT EXISTS" in query_upper:
            has_not_exists = True
        elif "EXISTS" in query_upper:
            has_exists = True

        # Check for self-join (same table appears twice)
        import re
        tables = re.findall(r'\b(employees|departments|customers|products|orders|order_items)\s+(?:AS\s+)?(\w+)', query, re.IGNORECASE)
        table_names = [t[0].lower() for t in tables]
        is_self_join = len(table_names) != len(set(table_names))

        return {
            "type": join_type,
            "has_exists": has_exists,
            "has_not_exists": has_not_exists,
            "is_self_join": is_self_join,
            "description": self._get_join_description(join_type, has_exists, has_not_exists, is_self_join),
        }

    def _get_join_description(self, join_type: str, has_exists: bool, has_not_exists: bool, is_self_join: bool) -> str:
        """Get description based on detected join type."""
        if has_not_exists:
            return "Anti-join pattern (NOT EXISTS) - Returns rows from first table with NO match in second"
        if has_exists:
            return "Semi-join pattern (EXISTS) - Returns rows from first table where match EXISTS"
        if is_self_join:
            return "Self-join - Table joined to itself (common for hierarchical data)"

        descriptions = {
            "inner": "INNER JOIN - Only matching rows from both tables",
            "left": "LEFT JOIN - All rows from left table, matching from right (or NULL)",
            "right": "RIGHT JOIN - All rows from right table, matching from left (or NULL)",
            "full": "FULL OUTER JOIN - All rows from both tables, NULL where no match",
            "cross": "CROSS JOIN - Cartesian product (every combination)",
            "none": "No explicit JOIN detected",
        }
        return descriptions.get(join_type, "Unknown join type")

    def _get_join_overview(self) -> dict:
        """Get overview of all join types."""
        return {
            "title": "JOIN Types Reference",
            "types": [
                {
                    "name": "INNER JOIN",
                    "symbol": "∩",
                    "description": "Only matching rows from both tables",
                    "syntax": "SELECT * FROM A INNER JOIN B ON A.key = B.key",
                    "result": "Only rows where key exists in BOTH A and B",
                    "row_count": "≤ min(rows_A, rows_B)",
                },
                {
                    "name": "LEFT JOIN",
                    "symbol": "⟕",
                    "description": "All from left + matching from right",
                    "syntax": "SELECT * FROM A LEFT JOIN B ON A.key = B.key",
                    "result": "All rows from A, matched with B (or NULL)",
                    "row_count": "≥ rows_A",
                },
                {
                    "name": "RIGHT JOIN",
                    "symbol": "⟖",
                    "description": "All from right + matching from left",
                    "syntax": "SELECT * FROM A RIGHT JOIN B ON A.key = B.key",
                    "result": "All rows from B, matched with A (or NULL)",
                    "row_count": "≥ rows_B",
                },
                {
                    "name": "FULL OUTER JOIN",
                    "symbol": "⟗",
                    "description": "All rows from both tables",
                    "syntax": "SELECT * FROM A FULL OUTER JOIN B ON A.key = B.key",
                    "result": "All rows from A and B, NULL where no match",
                    "row_count": "rows_A + rows_B - matches",
                    "note": "MySQL doesn't support FULL OUTER JOIN directly - use UNION of LEFT and RIGHT",
                },
                {
                    "name": "CROSS JOIN",
                    "symbol": "×",
                    "description": "Cartesian product - every combination",
                    "syntax": "SELECT * FROM A CROSS JOIN B",
                    "result": "Every row from A combined with every row from B",
                    "row_count": "rows_A × rows_B",
                    "warning": "Can create HUGE result sets!",
                },
            ],
        }

    def _get_join_details(self, detected_join: dict) -> dict:
        """Get detailed info about the detected join type."""
        join_type = detected_join["type"]

        details = {
            "inner": {
                "title": "INNER JOIN Deep Dive",
                "how_it_works": [
                    "For each row in the LEFT table...",
                    "Find all matching rows in the RIGHT table (based on ON condition)",
                    "If match found: combine the rows",
                    "If NO match: row is excluded from results",
                ],
                "when_to_use": [
                    "You only want records that exist in BOTH tables",
                    "You need to combine related data",
                    "You want to filter out incomplete relationships",
                ],
                "gotchas": [
                    "NULL values never match (even NULL = NULL is FALSE)",
                    "Rows with no match are silently dropped",
                    "Can accidentally filter out data you wanted",
                ],
            },
            "left": {
                "title": "LEFT JOIN Deep Dive",
                "how_it_works": [
                    "Start with ALL rows from the LEFT table",
                    "For each row, look for matches in the RIGHT table",
                    "If match found: combine the rows",
                    "If NO match: fill RIGHT columns with NULL",
                ],
                "when_to_use": [
                    "You need all rows from the primary table",
                    "You want to find orphaned records (WHERE right.id IS NULL)",
                    "The right table data is optional/supplementary",
                ],
                "gotchas": [
                    "Order matters! A LEFT JOIN B ≠ B LEFT JOIN A",
                    "One-to-many can create duplicate rows from left table",
                    "WHERE conditions on right table can turn it into INNER JOIN",
                ],
            },
            "right": {
                "title": "RIGHT JOIN Deep Dive",
                "how_it_works": [
                    "Start with ALL rows from the RIGHT table",
                    "For each row, look for matches in the LEFT table",
                    "If match found: combine the rows",
                    "If NO match: fill LEFT columns with NULL",
                ],
                "when_to_use": [
                    "Less common - usually rewrite as LEFT JOIN",
                    "When query logic flows better this direction",
                    "Matching existing query patterns",
                ],
                "gotchas": [
                    "Can always be rewritten as LEFT JOIN (just swap tables)",
                    "Most developers prefer LEFT JOIN for consistency",
                ],
            },
            "cross": {
                "title": "CROSS JOIN Deep Dive",
                "how_it_works": [
                    "Take every row from the LEFT table",
                    "Combine it with every row from the RIGHT table",
                    "No ON condition needed (or allowed)",
                    "Result: rows_A × rows_B combinations",
                ],
                "when_to_use": [
                    "Generate all possible combinations",
                    "Create test data",
                    "Combine with dates for reporting grids",
                ],
                "gotchas": [
                    "10 rows × 10 rows = 100 rows",
                    "1000 rows × 1000 rows = 1,000,000 rows!",
                    "Always use LIMIT during development",
                ],
                "warning": "CROSS JOIN can crash your database if used carelessly!",
            },
        }

        return details.get(join_type, {
            "title": f"{join_type.upper()} JOIN",
            "how_it_works": ["See the join reference above"],
        })

    def _get_animation_data(self, detected_join: dict, dataset) -> dict:
        """Get data for the animated join visualization."""
        # Sample data for animation
        employees_sample = [
            {"id": 1, "name": "Alice", "department_id": 1},
            {"id": 2, "name": "Bob", "department_id": 1},
            {"id": 3, "name": "Carol", "department_id": 2},
            {"id": 4, "name": "Dave", "department_id": None},  # No department!
        ]

        departments_sample = [
            {"id": 1, "name": "Engineering"},
            {"id": 2, "name": "Sales"},
            {"id": 3, "name": "HR"},  # No employees!
        ]

        join_type = detected_join["type"]

        # Calculate results based on join type
        if join_type == "inner":
            results = [
                {"left": employees_sample[0], "right": departments_sample[0], "matched": True},
                {"left": employees_sample[1], "right": departments_sample[0], "matched": True},
                {"left": employees_sample[2], "right": departments_sample[1], "matched": True},
            ]
            excluded_left = [employees_sample[3]]  # Dave has no dept
            excluded_right = [departments_sample[2]]  # HR has no employees
        elif join_type == "left":
            results = [
                {"left": employees_sample[0], "right": departments_sample[0], "matched": True},
                {"left": employees_sample[1], "right": departments_sample[0], "matched": True},
                {"left": employees_sample[2], "right": departments_sample[1], "matched": True},
                {"left": employees_sample[3], "right": None, "matched": False},  # Dave with NULL
            ]
            excluded_left = []
            excluded_right = [departments_sample[2]]  # HR not included
        elif join_type == "right":
            results = [
                {"left": employees_sample[0], "right": departments_sample[0], "matched": True},
                {"left": employees_sample[1], "right": departments_sample[0], "matched": True},
                {"left": employees_sample[2], "right": departments_sample[1], "matched": True},
                {"left": None, "right": departments_sample[2], "matched": False},  # HR with NULL
            ]
            excluded_left = [employees_sample[3]]  # Dave not included
            excluded_right = []
        elif join_type == "cross":
            # First few of cross product
            results = []
            for emp in employees_sample[:2]:  # Just first 2 employees for demo
                for dept in departments_sample:
                    results.append({"left": emp, "right": dept, "matched": True})
            excluded_left = []
            excluded_right = []
        else:
            results = []
            excluded_left = []
            excluded_right = []

        return {
            "left_table": {
                "name": "employees",
                "rows": employees_sample,
                "key_column": "department_id",
            },
            "right_table": {
                "name": "departments",
                "rows": departments_sample,
                "key_column": "id",
            },
            "join_type": join_type,
            "results": results,
            "excluded_left": excluded_left,
            "excluded_right": excluded_right,
            "animation_steps": self._get_animation_steps(join_type),
        }

    def _get_animation_steps(self, join_type: str) -> list:
        """Get step-by-step animation instructions."""
        if join_type == "inner":
            return [
                {"step": 1, "action": "highlight_left", "row": 0, "text": "Take Alice (dept_id=1)"},
                {"step": 2, "action": "scan_right", "text": "Scan departments for id=1"},
                {"step": 3, "action": "match", "left": 0, "right": 0, "text": "Match! Engineering (id=1)"},
                {"step": 4, "action": "highlight_left", "row": 1, "text": "Take Bob (dept_id=1)"},
                {"step": 5, "action": "match", "left": 1, "right": 0, "text": "Match! Engineering (id=1)"},
                {"step": 6, "action": "highlight_left", "row": 2, "text": "Take Carol (dept_id=2)"},
                {"step": 7, "action": "match", "left": 2, "right": 1, "text": "Match! Sales (id=2)"},
                {"step": 8, "action": "highlight_left", "row": 3, "text": "Take Dave (dept_id=NULL)"},
                {"step": 9, "action": "no_match", "text": "No match! NULL never equals anything"},
                {"step": 10, "action": "exclude_left", "row": 3, "text": "Dave excluded from INNER JOIN"},
            ]
        elif join_type == "left":
            return [
                {"step": 1, "action": "highlight_left", "row": 0, "text": "Take Alice (dept_id=1)"},
                {"step": 2, "action": "match", "left": 0, "right": 0, "text": "Match! Engineering"},
                {"step": 3, "action": "highlight_left", "row": 1, "text": "Take Bob (dept_id=1)"},
                {"step": 4, "action": "match", "left": 1, "right": 0, "text": "Match! Engineering"},
                {"step": 5, "action": "highlight_left", "row": 2, "text": "Take Carol (dept_id=2)"},
                {"step": 6, "action": "match", "left": 2, "right": 1, "text": "Match! Sales"},
                {"step": 7, "action": "highlight_left", "row": 3, "text": "Take Dave (dept_id=NULL)"},
                {"step": 8, "action": "no_match_keep", "text": "No match, but LEFT JOIN keeps Dave"},
                {"step": 9, "action": "null_fill", "text": "Fill department columns with NULL"},
            ]
        elif join_type == "cross":
            return [
                {"step": 1, "action": "highlight_left", "row": 0, "text": "Take Alice"},
                {"step": 2, "action": "cross_all", "text": "Combine with EVERY department"},
                {"step": 3, "action": "show_result", "text": "3 rows created for Alice"},
                {"step": 4, "action": "highlight_left", "row": 1, "text": "Take Bob"},
                {"step": 5, "action": "cross_all", "text": "Combine with EVERY department"},
                {"step": 6, "action": "show_result", "text": "3 more rows for Bob"},
                {"step": 7, "action": "multiply", "text": "4 employees × 3 departments = 12 rows!"},
            ]
        return []

    def _get_venn_diagrams(self) -> list:
        """Get Venn diagram representations for each join type."""
        return [
            {
                "type": "inner",
                "name": "INNER JOIN",
                "left_only": False,
                "right_only": False,
                "intersection": True,
                "description": "Only the intersection",
            },
            {
                "type": "left",
                "name": "LEFT JOIN",
                "left_only": True,
                "right_only": False,
                "intersection": True,
                "description": "All of left + intersection",
            },
            {
                "type": "right",
                "name": "RIGHT JOIN",
                "left_only": False,
                "right_only": True,
                "intersection": True,
                "description": "All of right + intersection",
            },
            {
                "type": "full",
                "name": "FULL OUTER JOIN",
                "left_only": True,
                "right_only": True,
                "intersection": True,
                "description": "Everything from both",
            },
            {
                "type": "left_anti",
                "name": "LEFT ANTI JOIN",
                "left_only": True,
                "right_only": False,
                "intersection": False,
                "description": "Only left (NOT EXISTS)",
                "sql": "LEFT JOIN ... WHERE right.id IS NULL",
            },
        ]

    def _get_row_multiplication_demo(self, dataset) -> dict:
        """Demonstrate how JOINs can multiply rows."""
        return {
            "title": "⚠️ Row Multiplication Warning",
            "explanation": "When you JOIN on a one-to-many relationship, rows get duplicated!",
            "demo": {
                "left_table": "departments (3 rows)",
                "right_table": "employees (10 rows)",
                "join_condition": "departments.id = employees.department_id",
                "expected": "Maybe 3 rows? (one per department)",
                "actual": "10 rows! Each employee row duplicates its department",
            },
            "scenarios": [
                {
                    "name": "One-to-Many (Expected)",
                    "example": "departments JOIN employees",
                    "what_happens": "Each department repeats for each employee",
                    "result": "rows = count of employees (the 'many' side)",
                },
                {
                    "name": "Many-to-Many (Dangerous!)",
                    "example": "orders JOIN order_items ON order",
                    "what_happens": "Multiple items per order × multiple orders per customer",
                    "result": "rows can explode: 100 orders × 5 items = 500 rows",
                },
                {
                    "name": "Accidental Cross Join",
                    "example": "Missing or wrong ON condition",
                    "what_happens": "Every row matches every row",
                    "result": "rows = left_count × right_count = DISASTER",
                },
            ],
            "prevention": [
                "Check row counts before and after JOIN",
                "Use COUNT(DISTINCT primary_key) to verify",
                "Use GROUP BY when aggregating after JOIN",
                "Consider using EXISTS instead of JOIN when you just need to filter",
            ],
        }

    def _get_semi_anti_join_patterns(self) -> dict:
        """Explain semi-join and anti-join patterns."""
        return {
            "title": "Semi-Join & Anti-Join Patterns",
            "semi_join": {
                "name": "Semi-Join (EXISTS)",
                "purpose": "Find rows in A that have at least one match in B",
                "key_feature": "Does NOT duplicate rows (unlike INNER JOIN)",
                "syntax": """SELECT * FROM A
WHERE EXISTS (
    SELECT 1 FROM B
    WHERE B.a_id = A.id
)""",
                "equivalent_but_different": """-- This duplicates rows if multiple matches!
SELECT DISTINCT A.*
FROM A
INNER JOIN B ON B.a_id = A.id""",
                "examples": [
                    {
                        "description": "Departments that have employees",
                        "sql": "SELECT * FROM departments d WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id)",
                    },
                    {
                        "description": "Customers who have placed orders",
                        "sql": "SELECT * FROM customers c WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)",
                    },
                ],
            },
            "anti_join": {
                "name": "Anti-Join (NOT EXISTS)",
                "purpose": "Find rows in A that have NO match in B",
                "key_feature": "Find orphaned/missing relationships",
                "syntax": """SELECT * FROM A
WHERE NOT EXISTS (
    SELECT 1 FROM B
    WHERE B.a_id = A.id
)""",
                "alternative": """-- Also works, but NOT EXISTS is usually faster
SELECT A.*
FROM A
LEFT JOIN B ON B.a_id = A.id
WHERE B.id IS NULL""",
                "examples": [
                    {
                        "description": "Departments with no employees",
                        "sql": "SELECT * FROM departments d WHERE NOT EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id)",
                    },
                    {
                        "description": "Customers who never ordered",
                        "sql": "SELECT * FROM customers c WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id)",
                    },
                    {
                        "description": "Products never sold",
                        "sql": "SELECT * FROM products p WHERE NOT EXISTS (SELECT 1 FROM order_items oi WHERE oi.product_id = p.id)",
                    },
                ],
            },
            "why_exists_over_in": {
                "title": "Why EXISTS over IN?",
                "reasons": [
                    "EXISTS stops at first match (faster)",
                    "EXISTS handles NULL correctly",
                    "IN with NULL subquery can return unexpected results",
                ],
                "null_trap": {
                    "query": "SELECT * FROM A WHERE id NOT IN (SELECT a_id FROM B)",
                    "problem": "If B.a_id contains NULL, entire query returns NOTHING!",
                    "solution": "Use NOT EXISTS instead",
                },
            },
        }

    def _get_self_join_demo(self, dataset) -> dict:
        """Demonstrate self-joins."""
        return {
            "title": "Self-Join: Table Joins Itself",
            "why_needed": "When rows in a table reference other rows in the SAME table",
            "common_uses": [
                "Employee → Manager hierarchy",
                "Category → Parent Category",
                "Location → Parent Location",
                "User → Referred By User",
            ],
            "syntax_example": """-- Find employees and their managers
SELECT
    e.name AS employee,
    m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id""",
            "key_points": [
                "Must use table aliases (e and m) to distinguish the two 'copies'",
                "Use LEFT JOIN to include employees without managers (CEO)",
                "Can chain multiple times for deeper hierarchies",
            ],
            "hierarchy_query": """-- Three levels: Employee → Manager → Director
SELECT
    e.name AS employee,
    m.name AS manager,
    d.name AS director
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id
LEFT JOIN employees d ON m.manager_id = d.id""",
            "sample_data": [
                {"employee": "Alice", "manager": "Carol", "note": "Alice reports to Carol"},
                {"employee": "Bob", "manager": "Carol", "note": "Bob reports to Carol"},
                {"employee": "Carol", "manager": "Eve", "note": "Carol reports to Eve"},
                {"employee": "Eve", "manager": None, "note": "Eve is CEO (no manager)"},
            ],
        }

    def _get_common_mistakes(self) -> list:
        """Common JOIN mistakes and how to avoid them."""
        return [
            {
                "mistake": "Forgetting the ON condition",
                "wrong": "SELECT * FROM employees JOIN departments",
                "result": "Creates CROSS JOIN (every possible combination)",
                "right": "SELECT * FROM employees e JOIN departments d ON e.department_id = d.id",
            },
            {
                "mistake": "Filtering on RIGHT table in WHERE (turns LEFT JOIN into INNER)",
                "wrong": """SELECT * FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
WHERE d.name = 'Engineering'  -- This filters out NULLs!""",
                "result": "Employees without departments are excluded",
                "right": """SELECT * FROM employees e
LEFT JOIN departments d ON e.department_id = d.id AND d.name = 'Engineering'""",
            },
            {
                "mistake": "Using = NULL instead of IS NULL",
                "wrong": "SELECT * FROM employees e LEFT JOIN departments d ON e.department_id = d.id WHERE d.id = NULL",
                "result": "Returns 0 rows (NULL = NULL is FALSE)",
                "right": "... WHERE d.id IS NULL",
            },
            {
                "mistake": "Ambiguous column names",
                "wrong": "SELECT id, name FROM employees e JOIN departments d ON e.department_id = d.id",
                "result": "Error: 'id' is ambiguous (exists in both tables)",
                "right": "SELECT e.id, e.name, d.name AS dept FROM ...",
            },
            {
                "mistake": "Not considering one-to-many multiplication",
                "wrong": "SELECT SUM(order_total) FROM customers c JOIN orders o ON c.id = o.customer_id",
                "result": "If multiple orders per customer, sum is wrong",
                "right": "GROUP BY customer, or use subquery for pre-aggregation",
            },
        ]

    def _get_performance_tips(self) -> list:
        """Performance tips for JOINs."""
        return [
            {
                "tip": "Index your JOIN columns",
                "why": "Without index, database must scan entire table for each row",
                "example": "CREATE INDEX idx_emp_dept ON employees(department_id)",
            },
            {
                "tip": "JOIN smallest table first (sometimes)",
                "why": "Optimizer usually handles this, but smaller driving table = less work",
                "note": "Modern optimizers often reorder JOINs automatically",
            },
            {
                "tip": "Use EXISTS instead of JOIN when filtering only",
                "why": "EXISTS stops at first match, JOIN continues matching all",
                "when": "When you don't need columns from the second table",
            },
            {
                "tip": "Filter early with WHERE on driving table",
                "why": "Reduces rows before JOIN, less work overall",
                "example": "FROM employees WHERE salary > 50000 JOIN departments",
            },
            {
                "tip": "Avoid SELECT * with JOINs",
                "why": "Returns duplicate columns and more data than needed",
                "example": "SELECT e.name, d.name instead of SELECT *",
            },
        ]
