"""
CTE (Common Table Expressions) concept - Comprehensive coverage.
From basic WITH clauses to recursive CTEs for hierarchical data.
"""

from typing import Any
import re

from app.concepts.base import BaseConcept, Step


class CTEConcept(BaseConcept):
    name = "cte"
    display_name = "CTEs (Common Table Expressions)"
    description = "Master WITH clauses from basics to recursive CTEs. Learn to traverse hierarchies, simplify complex queries, and write readable SQL."
    difficulty = "advanced"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        query_upper = query.upper()

        # Detect CTE patterns in query
        has_cte = 'WITH' in query_upper and 'AS' in query_upper
        is_recursive = 'WITH RECURSIVE' in query_upper

        # Count CTEs in query
        cte_count = len(re.findall(r'\b(\w+)\s+AS\s*\(', query, re.IGNORECASE))

        # Detect CTE names
        cte_names = re.findall(r'WITH\s+(?:RECURSIVE\s+)?(\w+)\s+AS', query, re.IGNORECASE)
        cte_names += re.findall(r',\s*(\w+)\s+AS\s*\(', query, re.IGNORECASE)

        return {
            'query': query,
            'has_cte': has_cte,
            'is_recursive': is_recursive,
            'cte_count': cte_count,
            'cte_names': cte_names,

            # Core concepts
            'what_is_cte': self._get_what_is_cte(),
            'syntax_breakdown': self._get_syntax_breakdown(),

            # Types of CTEs
            'cte_types': self._get_cte_types(),

            # Recursive CTE deep dive
            'recursive_anatomy': self._get_recursive_anatomy(),
            'recursive_examples': self._get_recursive_examples(),
            'termination_rules': self._get_termination_rules(),

            # Comparisons
            'comparisons': self._get_comparisons(),

            # Use cases
            'use_cases': self._get_use_cases(),

            # Performance
            'performance': self._get_performance_info(),

            # Common mistakes
            'common_mistakes': self._get_common_mistakes(),

            # Execution visualization
            'execution_flow': self._get_execution_flow(query, is_recursive),

            # Organization hierarchy for demo
            'org_hierarchy': self._get_org_hierarchy(),
        }

    def _get_what_is_cte(self) -> dict:
        return {
            'definition': 'A CTE is a named temporary result set that exists only within the scope of a single statement.',
            'key_benefits': [
                {'benefit': 'Readability', 'description': 'Break complex queries into logical, named building blocks'},
                {'benefit': 'Reusability', 'description': 'Reference the same CTE multiple times without duplicating code'},
                {'benefit': 'Recursion', 'description': 'Traverse hierarchical/tree data with WITH RECURSIVE'},
                {'benefit': 'Maintainability', 'description': 'Easier to debug and modify than deeply nested subqueries'},
            ],
            'mysql_version': 'CTEs available since MySQL 8.0 (2018)',
            'analogy': 'Think of CTEs like variables in programming - give a complex expression a name, then use that name.',
        }

    def _get_syntax_breakdown(self) -> dict:
        return {
            'basic': {
                'title': 'Basic CTE Syntax',
                'template': '''WITH cte_name AS (
    -- Your SELECT query here
    SELECT ...
)
SELECT * FROM cte_name;''',
                'parts': [
                    {'part': 'WITH', 'description': 'Keyword that starts a CTE definition'},
                    {'part': 'cte_name', 'description': 'Name you give to the temporary result set'},
                    {'part': 'AS (...)', 'description': 'The query that defines the CTE\'s contents'},
                    {'part': 'Main query', 'description': 'Query that uses the CTE'},
                ],
            },
            'multiple': {
                'title': 'Multiple CTEs',
                'template': '''WITH
    cte1 AS (SELECT ...),
    cte2 AS (SELECT ... FROM cte1),  -- Can reference cte1!
    cte3 AS (SELECT ... FROM cte2)   -- Can reference cte1 or cte2!
SELECT * FROM cte3;''',
                'note': 'Each CTE can reference CTEs defined before it (not after).',
            },
            'recursive': {
                'title': 'Recursive CTE Syntax',
                'template': '''WITH RECURSIVE cte_name AS (
    -- Anchor member (base case)
    SELECT ... WHERE condition

    UNION ALL

    -- Recursive member (references itself)
    SELECT ... FROM cte_name WHERE termination_condition
)
SELECT * FROM cte_name;''',
                'parts': [
                    {'part': 'WITH RECURSIVE', 'description': 'Indicates this CTE will reference itself'},
                    {'part': 'Anchor', 'description': 'Starting point - rows that seed the recursion'},
                    {'part': 'UNION ALL', 'description': 'Combines anchor with recursive results'},
                    {'part': 'Recursive member', 'description': 'Query that references the CTE itself'},
                    {'part': 'Termination', 'description': 'Condition that eventually returns no rows'},
                ],
            },
        }

    def _get_cte_types(self) -> list[dict]:
        return [
            {
                'type': 'Simple CTE',
                'icon': '📝',
                'description': 'Basic named subquery for readability',
                'example': '''WITH high_earners AS (
    SELECT * FROM employees
    WHERE salary > 80000
)
SELECT name, salary FROM high_earners;''',
                'use_when': 'You want to name a complex subquery for clarity',
            },
            {
                'type': 'Multi-CTE Chain',
                'icon': '🔗',
                'description': 'Multiple CTEs building on each other',
                'example': '''WITH
    dept_totals AS (
        SELECT department_id, SUM(salary) as total
        FROM employees GROUP BY department_id
    ),
    dept_with_names AS (
        SELECT d.name, dt.total
        FROM dept_totals dt
        JOIN departments d ON dt.department_id = d.id
    )
SELECT * FROM dept_with_names
WHERE total > 200000;''',
                'use_when': 'You need to build up results in logical steps',
            },
            {
                'type': 'Recursive CTE',
                'icon': '🔄',
                'description': 'Self-referencing for hierarchical data',
                'example': '''WITH RECURSIVE org_chart AS (
    -- Anchor: top-level (no manager)
    SELECT id, name, manager_id, 1 as level
    FROM employees WHERE manager_id IS NULL

    UNION ALL

    -- Recursive: find direct reports
    SELECT e.id, e.name, e.manager_id, oc.level + 1
    FROM employees e
    JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT * FROM org_chart;''',
                'use_when': 'Traversing trees, graphs, or generating sequences',
            },
            {
                'type': 'Recursive with Path',
                'icon': '🛤️',
                'description': 'Track the full path through hierarchy',
                'example': '''WITH RECURSIVE category_path AS (
    SELECT id, name, parent_id,
           CAST(name AS CHAR(500)) as path
    FROM categories WHERE parent_id IS NULL

    UNION ALL

    SELECT c.id, c.name, c.parent_id,
           CONCAT(cp.path, ' > ', c.name)
    FROM categories c
    JOIN category_path cp ON c.parent_id = cp.id
)
SELECT * FROM category_path;''',
                'use_when': 'Need to show full ancestry path (breadcrumbs)',
            },
        ]

    def _get_recursive_anatomy(self) -> dict:
        return {
            'title': 'Anatomy of a Recursive CTE',
            'diagram': '''
┌─────────────────────────────────────────────────────────────┐
│  WITH RECURSIVE cte_name AS (                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ ANCHOR MEMBER (Base Case)                             │  │
│  │ ─────────────────────────────                         │  │
│  │ SELECT id, name, 1 as level                           │  │
│  │ FROM employees                                        │  │
│  │ WHERE manager_id IS NULL    ◄── Starting point        │  │
│  └───────────────────────────────────────────────────────┘  │
│                          │                                   │
│                    UNION ALL                                 │
│                          │                                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │ RECURSIVE MEMBER                                      │  │
│  │ ──────────────────                                    │  │
│  │ SELECT e.id, e.name, oc.level + 1                     │  │
│  │ FROM employees e                                      │  │
│  │ JOIN cte_name oc ON e.manager_id = oc.id              │  │
│  │          ▲                                            │  │
│  │          └── References itself!                       │  │
│  └───────────────────────────────────────────────────────┘  │
│  )                                                          │
│  SELECT * FROM cte_name;                                    │
└─────────────────────────────────────────────────────────────┘
''',
            'execution_steps': [
                {'step': 1, 'title': 'Execute Anchor', 'description': 'Run anchor member once to get seed rows'},
                {'step': 2, 'title': 'First Iteration', 'description': 'Run recursive member using anchor rows'},
                {'step': 3, 'title': 'Iterate', 'description': 'Run recursive member using previous iteration\'s results'},
                {'step': 4, 'title': 'Terminate', 'description': 'Stop when recursive member returns no rows'},
                {'step': 5, 'title': 'Combine', 'description': 'UNION ALL combines all iterations into final result'},
            ],
        }

    def _get_recursive_examples(self) -> list[dict]:
        return [
            {
                'name': 'Org Chart / Reporting Hierarchy',
                'icon': '👥',
                'description': 'Find all employees and their reporting levels',
                'sql': '''WITH RECURSIVE org_chart AS (
    -- CEO/top-level employees (no manager)
    SELECT id, name, manager_id,
           0 as level,
           CAST(name AS CHAR(200)) as path
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- All direct reports, incrementing level
    SELECT e.id, e.name, e.manager_id,
           oc.level + 1,
           CONCAT(oc.path, ' → ', e.name)
    FROM employees e
    INNER JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT
    REPEAT('  ', level) || name as employee,
    level,
    path
FROM org_chart
ORDER BY path;''',
                'output_preview': [
                    {'employee': 'Alice (CEO)', 'level': 0, 'path': 'Alice'},
                    {'employee': '  Bob', 'level': 1, 'path': 'Alice → Bob'},
                    {'employee': '    Carol', 'level': 2, 'path': 'Alice → Bob → Carol'},
                ],
            },
            {
                'name': 'Number Sequence',
                'icon': '🔢',
                'description': 'Generate a sequence of numbers',
                'sql': '''WITH RECURSIVE numbers AS (
    -- Anchor: start at 1
    SELECT 1 as n

    UNION ALL

    -- Add 1 until we reach 10
    SELECT n + 1
    FROM numbers
    WHERE n < 10
)
SELECT * FROM numbers;''',
                'output_preview': [
                    {'n': 1}, {'n': 2}, {'n': 3}, {'n': '...'}, {'n': 10}
                ],
            },
            {
                'name': 'Date Series',
                'icon': '📅',
                'description': 'Generate a range of dates',
                'sql': '''WITH RECURSIVE date_range AS (
    SELECT DATE('2024-01-01') as date

    UNION ALL

    SELECT DATE_ADD(date, INTERVAL 1 DAY)
    FROM date_range
    WHERE date < '2024-01-31'
)
SELECT * FROM date_range;''',
                'output_preview': [
                    {'date': '2024-01-01'}, {'date': '2024-01-02'}, {'date': '...'}, {'date': '2024-01-31'}
                ],
            },
            {
                'name': 'Fibonacci Sequence',
                'icon': '🐚',
                'description': 'Classic recursive algorithm',
                'sql': '''WITH RECURSIVE fib AS (
    -- Two anchor rows for Fibonacci
    SELECT 1 as n, 0 as fib_n, 1 as fib_next

    UNION ALL

    SELECT n + 1, fib_next, fib_n + fib_next
    FROM fib
    WHERE n < 10
)
SELECT n, fib_n as fibonacci FROM fib;''',
                'output_preview': [
                    {'n': 1, 'fibonacci': 0},
                    {'n': 2, 'fibonacci': 1},
                    {'n': 3, 'fibonacci': 1},
                    {'n': 4, 'fibonacci': 2},
                    {'n': 5, 'fibonacci': 3},
                ],
            },
            {
                'name': 'Bill of Materials',
                'icon': '🔧',
                'description': 'Find all components of a product (parts containing parts)',
                'sql': '''WITH RECURSIVE bom AS (
    -- Top-level product
    SELECT part_id, component_id, quantity, 1 as level
    FROM parts_structure
    WHERE part_id = 'BIKE-001'

    UNION ALL

    -- Sub-components
    SELECT ps.part_id, ps.component_id,
           ps.quantity * bom.quantity,  -- Multiply quantities
           bom.level + 1
    FROM parts_structure ps
    JOIN bom ON ps.part_id = bom.component_id
)
SELECT * FROM bom;''',
                'output_preview': [
                    {'part': 'BIKE-001', 'component': 'FRAME', 'qty': 1, 'level': 1},
                    {'part': 'FRAME', 'component': 'TUBE', 'qty': 4, 'level': 2},
                ],
            },
            {
                'name': 'Shortest Path (Graph)',
                'icon': '🗺️',
                'description': 'Find path between nodes in a graph',
                'sql': '''WITH RECURSIVE paths AS (
    -- Start at node A
    SELECT 'A' as start_node,
           target as current_node,
           cost,
           CAST(CONCAT('A->', target) AS CHAR(100)) as path
    FROM edges WHERE source = 'A'

    UNION ALL

    -- Extend path
    SELECT p.start_node,
           e.target,
           p.cost + e.cost,
           CONCAT(p.path, '->', e.target)
    FROM paths p
    JOIN edges e ON p.current_node = e.source
    WHERE LOCATE(e.target, p.path) = 0  -- Prevent cycles!
)
SELECT * FROM paths WHERE current_node = 'Z'
ORDER BY cost LIMIT 1;''',
                'output_preview': [
                    {'start': 'A', 'end': 'Z', 'cost': 15, 'path': 'A->B->D->Z'}
                ],
            },
        ]

    def _get_termination_rules(self) -> dict:
        return {
            'title': 'Preventing Infinite Loops',
            'warning': 'Recursive CTEs can run forever if not properly terminated!',
            'strategies': [
                {
                    'name': 'Counter Limit',
                    'description': 'Add a level/counter column and limit it',
                    'example': 'WHERE level < 10',
                    'icon': '🔢',
                },
                {
                    'name': 'MySQL Safety Limit',
                    'description': 'MySQL has cte_max_recursion_depth (default: 1000)',
                    'example': 'SET cte_max_recursion_depth = 5000;',
                    'icon': '🛡️',
                },
                {
                    'name': 'Cycle Detection',
                    'description': 'Track visited nodes in path string',
                    'example': "WHERE LOCATE(node_id, path) = 0",
                    'icon': '🔄',
                },
                {
                    'name': 'Natural Termination',
                    'description': 'Query naturally returns no rows (e.g., no more children)',
                    'example': 'JOIN finds no matching rows',
                    'icon': '✋',
                },
            ],
            'mysql_setting': {
                'variable': 'cte_max_recursion_depth',
                'default': 1000,
                'max': 4294967295,
                'note': 'Error 3636 if exceeded: "Recursive query aborted after X iterations"',
            },
        }

    def _get_comparisons(self) -> list[dict]:
        return [
            {
                'title': 'CTE vs Subquery',
                'cte_pros': [
                    'Named and readable',
                    'Can be referenced multiple times',
                    'Supports recursion',
                    'Easier to debug (can SELECT from CTE alone)',
                ],
                'cte_cons': [
                    'Slight overhead for simple cases',
                    'MySQL 8.0+ only',
                ],
                'subquery_pros': [
                    'Works on older MySQL versions',
                    'Fine for simple, one-time use',
                ],
                'subquery_cons': [
                    'Harder to read when nested',
                    'Must duplicate if used multiple times',
                    'No recursion possible',
                ],
                'verdict': 'Use CTE when query is complex or subquery would be repeated.',
                'example_before': '''SELECT * FROM employees
WHERE department_id IN (
    SELECT department_id FROM (
        SELECT department_id, AVG(salary) as avg
        FROM employees GROUP BY department_id
    ) t WHERE avg > 70000
);''',
                'example_after': '''WITH dept_avgs AS (
    SELECT department_id, AVG(salary) as avg
    FROM employees GROUP BY department_id
),
high_paying_depts AS (
    SELECT department_id FROM dept_avgs WHERE avg > 70000
)
SELECT * FROM employees
WHERE department_id IN (SELECT department_id FROM high_paying_depts);''',
            },
            {
                'title': 'CTE vs Temporary Table',
                'cte_pros': [
                    'No DDL needed (no CREATE/DROP)',
                    'Scope limited to single statement',
                    'Optimizer can inline (sometimes faster)',
                    'No disk I/O for small results',
                ],
                'cte_cons': [
                    'Cannot be indexed',
                    'Only available in one statement',
                    'Re-evaluated if referenced multiple times (usually)',
                ],
                'temp_table_pros': [
                    'Can add indexes',
                    'Reusable across statements in session',
                    'Explicit materialization control',
                ],
                'temp_table_cons': [
                    'Requires CREATE/DROP',
                    'Disk I/O overhead',
                    'Must manage lifecycle',
                ],
                'verdict': 'Use CTE for single-statement needs; temp table for cross-statement reuse or when indexes needed.',
            },
            {
                'title': 'CTE vs View',
                'cte_pros': [
                    'No schema changes needed',
                    'Query-local (no naming conflicts)',
                    'Can be recursive',
                ],
                'cte_cons': [
                    'Not reusable across queries',
                    'Must redefine each time',
                ],
                'view_pros': [
                    'Reusable across entire database',
                    'Can be secured with permissions',
                    'Persisted definition',
                ],
                'view_cons': [
                    'Requires CREATE VIEW permission',
                    'Global namespace (naming matters)',
                    'Cannot be recursive',
                ],
                'verdict': 'Use CTE for one-off queries; View for frequently reused query patterns.',
            },
        ]

    def _get_use_cases(self) -> list[dict]:
        return [
            {
                'category': 'Hierarchical Data',
                'icon': '🌳',
                'examples': [
                    'Org charts (employee → manager)',
                    'Category trees (parent → child categories)',
                    'File systems (folder → subfolder)',
                    'Comment threads (reply chains)',
                    'Bill of materials (product → components)',
                ],
            },
            {
                'category': 'Sequence Generation',
                'icon': '🔢',
                'examples': [
                    'Number series (1, 2, 3, ...)',
                    'Date ranges for reporting',
                    'Time slots for scheduling',
                    'Fibonacci, factorial, etc.',
                ],
            },
            {
                'category': 'Graph Traversal',
                'icon': '🕸️',
                'examples': [
                    'Shortest path between nodes',
                    'Find all connected nodes',
                    'Social network (friends of friends)',
                    'Dependency resolution',
                ],
            },
            {
                'category': 'Query Simplification',
                'icon': '📖',
                'examples': [
                    'Break up deeply nested subqueries',
                    'Name intermediate calculations',
                    'Reuse same aggregation multiple times',
                    'Self-documenting SQL',
                ],
            },
            {
                'category': 'Running Calculations',
                'icon': '📊',
                'examples': [
                    'Running totals',
                    'Moving averages',
                    'Cumulative percentages',
                    'Period-over-period comparisons',
                ],
            },
        ]

    def _get_performance_info(self) -> dict:
        return {
            'title': 'CTE Performance in MySQL',
            'key_points': [
                {
                    'point': 'Materialization',
                    'description': 'MySQL 8.0 can materialize CTEs (compute once, reuse). Happens when CTE is referenced multiple times.',
                    'tip': 'Check EXPLAIN for "Materialize" operation.',
                },
                {
                    'point': 'Inlining',
                    'description': 'If CTE is referenced once, optimizer may inline it like a subquery.',
                    'tip': 'Single-reference CTEs have no overhead vs subquery.',
                },
                {
                    'point': 'Recursive CTEs',
                    'description': 'Each iteration produces rows; all are UNION ALLed together.',
                    'tip': 'Limit depth and add WHERE conditions in recursive member.',
                },
                {
                    'point': 'No Indexes',
                    'description': 'CTE results cannot be indexed. Large CTEs may need temp table instead.',
                    'tip': 'If JOINing large CTE multiple times, consider temp table with index.',
                },
            ],
            'optimizer_hints': [
                {'hint': 'MERGE', 'description': 'Force inlining: /*+ MERGE(cte_name) */'},
                {'hint': 'NO_MERGE', 'description': 'Force materialization: /*+ NO_MERGE(cte_name) */'},
            ],
            'explain_indicators': [
                {'indicator': 'Materialize', 'meaning': 'CTE is being computed and stored'},
                {'indicator': 'Recursive', 'meaning': 'Recursive CTE execution'},
                {'indicator': 'derived', 'meaning': 'CTE treated as derived table'},
            ],
        }

    def _get_common_mistakes(self) -> list[dict]:
        return [
            {
                'mistake': 'Missing RECURSIVE keyword',
                'wrong': '''WITH tree AS (
    SELECT * FROM nodes WHERE parent IS NULL
    UNION ALL
    SELECT n.* FROM nodes n JOIN tree t ON n.parent = t.id
)''',
                'right': '''WITH RECURSIVE tree AS (
    SELECT * FROM nodes WHERE parent IS NULL
    UNION ALL
    SELECT n.* FROM nodes n JOIN tree t ON n.parent = t.id
)''',
                'explanation': 'Self-referencing CTEs MUST use WITH RECURSIVE.',
            },
            {
                'mistake': 'Using UNION instead of UNION ALL',
                'wrong': '''WITH RECURSIVE nums AS (
    SELECT 1 as n
    UNION
    SELECT n + 1 FROM nums WHERE n < 10
)''',
                'right': '''WITH RECURSIVE nums AS (
    SELECT 1 as n
    UNION ALL
    SELECT n + 1 FROM nums WHERE n < 10
)''',
                'explanation': 'UNION removes duplicates (slower). Use UNION ALL for recursion unless you need deduplication.',
            },
            {
                'mistake': 'No termination condition',
                'wrong': '''WITH RECURSIVE inf AS (
    SELECT 1 as n
    UNION ALL
    SELECT n + 1 FROM inf  -- Runs forever!
)''',
                'right': '''WITH RECURSIVE bounded AS (
    SELECT 1 as n
    UNION ALL
    SELECT n + 1 FROM bounded WHERE n < 100
)''',
                'explanation': 'Always include a WHERE clause in recursive member to stop iteration.',
            },
            {
                'mistake': 'Referencing CTE before definition',
                'wrong': '''WITH
    b AS (SELECT * FROM a),  -- Error: 'a' not yet defined
    a AS (SELECT * FROM t)
SELECT * FROM b;''',
                'right': '''WITH
    a AS (SELECT * FROM t),
    b AS (SELECT * FROM a)  -- OK: 'a' defined above
SELECT * FROM b;''',
                'explanation': 'CTEs can only reference CTEs defined earlier in the WITH clause.',
            },
            {
                'mistake': 'Forgetting column aliases with UNION',
                'wrong': '''WITH RECURSIVE tree AS (
    SELECT id, name, 1 FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, level + 1 FROM employees e JOIN tree...
)''',
                'right': '''WITH RECURSIVE tree AS (
    SELECT id, name, 1 AS level FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, t.level + 1 FROM employees e JOIN tree t...
)''',
                'explanation': 'Anchor member column names are used for the CTE. Use aliases!',
            },
        ]

    def _get_execution_flow(self, query: str, is_recursive: bool) -> list[dict]:
        """Generate execution flow visualization based on query type."""
        if is_recursive:
            return [
                {'step': 1, 'phase': 'Parse', 'description': 'Parse WITH RECURSIVE clause, identify anchor and recursive members', 'icon': '📝'},
                {'step': 2, 'phase': 'Anchor', 'description': 'Execute anchor member, store results as iteration 0', 'icon': '⚓'},
                {'step': 3, 'phase': 'Iterate', 'description': 'Execute recursive member using previous iteration\'s rows', 'icon': '🔄'},
                {'step': 4, 'phase': 'Check', 'description': 'If recursive member returned rows, go to step 3', 'icon': '❓'},
                {'step': 5, 'phase': 'Combine', 'description': 'UNION ALL all iterations together', 'icon': '🔗'},
                {'step': 6, 'phase': 'Execute', 'description': 'Run main query against complete CTE', 'icon': '▶️'},
            ]
        else:
            return [
                {'step': 1, 'phase': 'Parse', 'description': 'Parse WITH clause, identify CTE definitions', 'icon': '📝'},
                {'step': 2, 'phase': 'Optimize', 'description': 'Decide: materialize or inline each CTE', 'icon': '⚙️'},
                {'step': 3, 'phase': 'Execute CTEs', 'description': 'Execute each CTE in definition order', 'icon': '▶️'},
                {'step': 4, 'phase': 'Main Query', 'description': 'Execute main SELECT using CTE results', 'icon': '🎯'},
            ]

    def _get_org_hierarchy(self) -> dict:
        """Sample org hierarchy for visualization."""
        return {
            'title': 'Example: Employee Hierarchy',
            'description': 'Traverse reporting structure with recursive CTE',
            'data': [
                {'id': 1, 'name': 'Alice (CEO)', 'manager_id': None, 'level': 0},
                {'id': 2, 'name': 'Bob (VP Eng)', 'manager_id': 1, 'level': 1},
                {'id': 3, 'name': 'Carol (VP Sales)', 'manager_id': 1, 'level': 1},
                {'id': 4, 'name': 'David (Eng Manager)', 'manager_id': 2, 'level': 2},
                {'id': 5, 'name': 'Eva (Sales Manager)', 'manager_id': 3, 'level': 2},
                {'id': 6, 'name': 'Frank (Developer)', 'manager_id': 4, 'level': 3},
                {'id': 7, 'name': 'Grace (Developer)', 'manager_id': 4, 'level': 3},
                {'id': 8, 'name': 'Henry (Sales Rep)', 'manager_id': 5, 'level': 3},
            ],
            'iterations': [
                {'iteration': 0, 'label': 'Anchor', 'rows': ['Alice (CEO)'], 'description': 'Start with CEO (manager_id IS NULL)'},
                {'iteration': 1, 'label': 'Iteration 1', 'rows': ['Bob', 'Carol'], 'description': 'Find direct reports of CEO'},
                {'iteration': 2, 'label': 'Iteration 2', 'rows': ['David', 'Eva'], 'description': 'Find reports of Bob & Carol'},
                {'iteration': 3, 'label': 'Iteration 3', 'rows': ['Frank', 'Grace', 'Henry'], 'description': 'Find reports of David & Eva'},
                {'iteration': 4, 'label': 'Termination', 'rows': [], 'description': 'No more reports found → stop'},
            ],
        }

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        viz_data = self.get_visualization_data(query, dataset)

        steps = [
            Step(
                title="What is a CTE?",
                description="A named temporary result set that exists only within a single statement. Like a variable for SQL!",
                highlight={'section': 'intro'}
            ),
            Step(
                title="CTE Syntax",
                description="WITH cte_name AS (SELECT ...) - then use cte_name in your main query",
                highlight={'section': 'syntax'}
            ),
        ]

        if viz_data['has_cte']:
            steps.append(Step(
                title=f"Your CTE: {', '.join(viz_data['cte_names'])}",
                description=f"Found {viz_data['cte_count']} CTE(s) in your query",
                highlight={'ctes': viz_data['cte_names']}
            ))

        if viz_data['is_recursive']:
            steps.extend([
                Step(
                    title="Recursive CTE Detected!",
                    description="Your CTE references itself - this enables hierarchy traversal",
                    highlight={'section': 'recursive'}
                ),
                Step(
                    title="Anchor Member",
                    description="The first SELECT is the anchor - it seeds the recursion with initial rows",
                    highlight={'part': 'anchor'}
                ),
                Step(
                    title="Recursive Member",
                    description="The second SELECT references the CTE itself, building on previous results",
                    highlight={'part': 'recursive'}
                ),
                Step(
                    title="Termination",
                    description="Recursion stops when the recursive member returns no new rows",
                    highlight={'part': 'termination'}
                ),
            ])
        else:
            steps.append(Step(
                title="Non-Recursive CTE",
                description="This is a simple CTE - executed once and results are available to main query",
                highlight={'section': 'simple'}
            ))

        steps.extend([
            Step(
                title="Execution Flow",
                description="CTEs execute top-to-bottom, each can reference those defined before it",
                highlight={'section': 'execution'}
            ),
            Step(
                title="Best Practices",
                description="Use CTEs to break complex queries into readable steps. Name them well!",
                highlight={'section': 'best_practices'}
            ),
        ])

        return steps

    def get_sample_queries(self) -> list[str]:
        return [
            # Simple CTE
            "WITH high_earners AS (SELECT * FROM employees WHERE salary > 80000) SELECT name, salary FROM high_earners ORDER BY salary DESC",

            # Multi-CTE
            "WITH dept_totals AS (SELECT department_id, SUM(salary) as total FROM employees GROUP BY department_id), big_depts AS (SELECT * FROM dept_totals WHERE total > 200000) SELECT * FROM big_depts",

            # Recursive - Number sequence
            "WITH RECURSIVE nums AS (SELECT 1 as n UNION ALL SELECT n + 1 FROM nums WHERE n < 10) SELECT * FROM nums",

            # Recursive - Hierarchy (simulated)
            "WITH RECURSIVE org AS (SELECT id, name, department_id, 0 as level FROM employees WHERE id = 1 UNION ALL SELECT e.id, e.name, e.department_id, o.level + 1 FROM employees e JOIN org o ON e.department_id = o.department_id WHERE e.id > o.id AND o.level < 2) SELECT * FROM org",
        ]
