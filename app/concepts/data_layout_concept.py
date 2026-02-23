"""
Data Layout Concept - Understanding how MySQL stores data physically.
Covers clustered indexes, secondary indexes, covering indexes, and page structure.
"""

from typing import Any

from app.concepts.base import BaseConcept, Step


class DataLayoutConcept(BaseConcept):
    """Data layout and index structure visualization."""

    name = "data-layout"
    display_name = "Data Layout & Index Structure"
    description = "Understand clustered indexes, secondary indexes, covering indexes, and how data is stored on disk"
    difficulty = "intermediate"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        """Generate visualization data for data layout concepts."""
        return {
            "overview": self._get_overview(),
            "clustered_index": self._get_clustered_index(),
            "secondary_index": self._get_secondary_index(),
            "covering_index": self._get_covering_index(),
            "page_structure": self._get_page_structure(),
            "explain_examples": self._get_explain_examples(),
            "optimization_tips": self._get_optimization_tips(),
        }

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        return [
            Step(
                title="Data Layout Overview",
                description="InnoDB organizes data in B+Tree structures where the table itself IS the primary key index.",
                highlight={'section': 'overview'}
            ),
            Step(
                title="Clustered Index",
                description="The primary key determines physical row order. Leaf nodes contain the actual row data.",
                highlight={'section': 'clustered_index'}
            ),
            Step(
                title="Secondary Indexes",
                description="Secondary indexes store the indexed columns + primary key. Lookups require a second read.",
                highlight={'section': 'secondary_index'}
            ),
            Step(
                title="Covering Indexes",
                description="When an index contains all columns needed by a query, no table access is required.",
                highlight={'section': 'covering_index'}
            ),
            Step(
                title="Page Structure",
                description="Data is organized in 16KB pages. Understanding page structure helps optimize queries.",
                highlight={'section': 'page_structure'}
            ),
        ]

    def get_sample_queries(self) -> list[str]:
        return [
            "EXPLAIN SELECT * FROM employees WHERE id = 5",
            "EXPLAIN SELECT name FROM employees WHERE department_id = 2",
            "EXPLAIN SELECT id, name FROM employees WHERE name = 'John'",
            "SHOW INDEX FROM employees",
        ]

    def _get_overview(self) -> dict:
        return {
            "title": "How InnoDB Stores Data",
            "key_insight": "In InnoDB, the table IS the clustered index (primary key B+Tree)",
            "structure": {
                "tablespace": "Container for tables and indexes (*.ibd files)",
                "segment": "Collection of extents for a specific object",
                "extent": "64 contiguous pages (1MB)",
                "page": "16KB - basic unit of I/O",
                "row": "Actual data within pages",
            },
            "why_matters": [
                "Primary key choice affects ALL queries",
                "Secondary indexes always include PK (storage cost)",
                "Random inserts fragment the clustered index",
                "Sequential PKs (auto_increment) = efficient inserts",
            ],
        }

    def _get_clustered_index(self) -> dict:
        return {
            "title": "Clustered Index = The Table",
            "description": "InnoDB stores table data in a B+Tree ordered by primary key. The leaf nodes ARE the rows.",
            "key_points": [
                "Every InnoDB table has exactly one clustered index",
                "If no PK defined, InnoDB uses first UNIQUE NOT NULL index",
                "If no suitable index, InnoDB creates hidden 6-byte row ID",
                "Rows are physically ordered by the clustered index key",
            ],
            "btree_visualization": {
                "description": "B+Tree structure for employees table (PK: id)",
                "internal_nodes": [
                    {"keys": [50], "description": "Root: routes to left (id<50) or right (id>=50)"},
                ],
                "leaf_nodes": [
                    {
                        "range": "id 1-49",
                        "rows": [
                            {"id": 1, "name": "Alice", "salary": 75000, "dept_id": 1},
                            {"id": 2, "name": "Bob", "salary": 82000, "dept_id": 2},
                            {"id": 3, "name": "Carol", "salary": 68000, "dept_id": 1},
                        ],
                        "note": "Actual row data stored here!"
                    },
                    {
                        "range": "id 50-99",
                        "rows": [
                            {"id": 50, "name": "David", "salary": 91000, "dept_id": 3},
                            {"id": 51, "name": "Eve", "salary": 77000, "dept_id": 2},
                        ],
                        "note": "Rows ordered by id within page"
                    },
                ],
            },
            "lookup_example": {
                "query": "SELECT * FROM employees WHERE id = 51",
                "steps": [
                    {"step": 1, "action": "Read root page", "result": "51 >= 50, go right"},
                    {"step": 2, "action": "Read leaf page", "result": "Find row with id=51"},
                    {"step": 3, "action": "Return row data", "result": "Eve, 77000, dept_id=2"},
                ],
                "io_cost": "2 page reads (root + leaf)",
            },
            "pk_design_tips": [
                "Use AUTO_INCREMENT for sequential inserts (no page splits)",
                "Keep PK small - it's duplicated in every secondary index",
                "UUID as PK = random inserts = fragmentation",
                "Composite PK order matters for range queries",
            ],
        }

    def _get_secondary_index(self) -> dict:
        return {
            "title": "Secondary Indexes: The Double Lookup",
            "description": "Secondary indexes store indexed columns + primary key. Finding rows requires TWO lookups.",
            "key_insight": "Secondary index lookup = Index B+Tree search + Clustered index lookup",
            "structure": {
                "leaf_contents": "Indexed column(s) + Primary Key value",
                "not_stored": "Other row columns (must go back to clustered index)",
            },
            "btree_visualization": {
                "description": "Secondary index on name column",
                "leaf_nodes": [
                    {
                        "entries": [
                            {"name": "Alice", "pk": 1},
                            {"name": "Bob", "pk": 2},
                            {"name": "Carol", "pk": 3},
                        ],
                        "note": "Sorted by name, stores PK"
                    },
                    {
                        "entries": [
                            {"name": "David", "pk": 50},
                            {"name": "Eve", "pk": 51},
                        ],
                        "note": "Only name + id stored"
                    },
                ],
            },
            "double_lookup_example": {
                "query": "SELECT * FROM employees WHERE name = 'Eve'",
                "steps": [
                    {"step": 1, "action": "Search name index", "location": "Secondary Index", "result": "Find name='Eve', pk=51"},
                    {"step": 2, "action": "Lookup pk=51", "location": "Clustered Index", "result": "Find full row"},
                    {"step": 3, "action": "Return row", "result": "Eve, 77000, dept_id=2"},
                ],
                "io_cost": "4 page reads (2 for secondary index + 2 for clustered index)",
                "explain_output": "type: ref, key: idx_name, Extra: (none) = needs table lookup",
            },
            "when_expensive": [
                "Large result sets (many PK lookups)",
                "Wide rows (each lookup reads entire row)",
                "PK not in buffer pool (random I/O)",
            ],
            "optimization": "If you only need indexed columns + PK, query is faster (covering index)",
        }

    def _get_covering_index(self) -> dict:
        return {
            "title": "Covering Index: Index-Only Scans",
            "description": "When an index contains ALL columns needed by a query, no clustered index lookup is required.",
            "key_insight": "EXPLAIN shows 'Using index' in Extra column = covering index!",
            "examples": [
                {
                    "name": "Not Covering",
                    "index": "INDEX(name)",
                    "query": "SELECT name, salary FROM employees WHERE name = 'Eve'",
                    "covered": False,
                    "why": "salary not in index - must read clustered index",
                    "extra": "(none)",
                },
                {
                    "name": "Covering",
                    "index": "INDEX(name, salary)",
                    "query": "SELECT name, salary FROM employees WHERE name = 'Eve'",
                    "covered": True,
                    "why": "Both name and salary in index!",
                    "extra": "Using index",
                },
                {
                    "name": "PK Always Included",
                    "index": "INDEX(name)",
                    "query": "SELECT id, name FROM employees WHERE name = 'Eve'",
                    "covered": True,
                    "why": "Secondary indexes include PK automatically",
                    "extra": "Using index",
                },
            ],
            "demo_comparison": {
                "title": "Same Query, Different Index",
                "query": "SELECT name, salary FROM employees WHERE department_id = 2",
                "scenarios": [
                    {
                        "index": "INDEX(department_id)",
                        "pages_read": "Index pages + Clustered index pages for each row",
                        "io_pattern": "Random (jumping around clustered index)",
                        "performance": "Slower for large results",
                    },
                    {
                        "index": "INDEX(department_id, name, salary)",
                        "pages_read": "Only index pages",
                        "io_pattern": "Sequential (reading index in order)",
                        "performance": "Faster, especially for large results",
                    },
                ],
            },
            "design_tips": [
                "Put columns for WHERE, ORDER BY, GROUP BY first",
                "Add SELECT columns to make it covering",
                "Don't over-index - each index has write cost",
                "Wide covering indexes increase storage and write overhead",
            ],
            "tradeoffs": {
                "benefits": ["Faster reads", "Less I/O", "Better cache usage"],
                "costs": ["More storage", "Slower writes", "More maintenance"],
            },
        }

    def _get_page_structure(self) -> dict:
        return {
            "title": "InnoDB Page Structure (16KB)",
            "description": "Understanding page layout helps you optimize row sizes and query patterns.",
            "page_layout": [
                {"section": "File Header", "size": "38 bytes", "purpose": "Page type, checksum, pointers"},
                {"section": "Page Header", "size": "56 bytes", "purpose": "Record count, free space info"},
                {"section": "Infimum/Supremum", "size": "26 bytes", "purpose": "Boundary records"},
                {"section": "User Records", "size": "Variable", "purpose": "Actual row data"},
                {"section": "Free Space", "size": "Variable", "purpose": "Room for new records"},
                {"section": "Page Directory", "size": "Variable", "purpose": "Slot pointers for binary search"},
                {"section": "File Trailer", "size": "8 bytes", "purpose": "Checksum for crash detection"},
            ],
            "row_storage": {
                "description": "Each row has overhead beyond just the data",
                "components": [
                    {"name": "Record Header", "size": "5+ bytes", "purpose": "Metadata, next record pointer"},
                    {"name": "Hidden Columns", "size": "6+7 bytes", "purpose": "Transaction ID, rollback pointer"},
                    {"name": "User Columns", "size": "Variable", "purpose": "Your actual data"},
                ],
                "example": {
                    "columns": "INT (4) + VARCHAR(100) (avg 50) + DATETIME (8)",
                    "user_data": "~62 bytes",
                    "overhead": "~18 bytes",
                    "total": "~80 bytes per row",
                    "rows_per_page": "~200 rows in 16KB page",
                },
            },
            "why_select_star_bad": {
                "title": "Why SELECT * Hurts Performance",
                "reasons": [
                    "Reads entire row even if you only need 2 columns",
                    "More pages to read from disk",
                    "More memory in buffer pool",
                    "Can't use covering indexes",
                    "More network transfer",
                ],
                "demo": {
                    "bad_query": "SELECT * FROM employees WHERE dept_id = 2",
                    "good_query": "SELECT id, name FROM employees WHERE dept_id = 2",
                    "difference": "Good query might use covering index, reads fewer bytes",
                },
            },
        }

    def _get_explain_examples(self) -> dict:
        return {
            "title": "Reading EXPLAIN for Index Usage",
            "key_columns": [
                {"column": "type", "good": "const, eq_ref, ref", "bad": "ALL (full scan)", "meaning": "Access method"},
                {"column": "key", "good": "Shows index name", "bad": "NULL", "meaning": "Index used"},
                {"column": "rows", "good": "Small number", "bad": "Large number", "meaning": "Estimated rows"},
                {"column": "Extra", "good": "Using index", "bad": "Using filesort", "meaning": "Execution details"},
            ],
            "examples": [
                {
                    "query": "SELECT * FROM employees WHERE id = 5",
                    "explain": {
                        "type": "const",
                        "key": "PRIMARY",
                        "rows": 1,
                        "extra": "",
                    },
                    "analysis": "Best case - direct PK lookup, 1 row",
                },
                {
                    "query": "SELECT * FROM employees WHERE name = 'Alice'",
                    "explain": {
                        "type": "ref",
                        "key": "idx_name",
                        "rows": 1,
                        "extra": "",
                    },
                    "analysis": "Uses name index, then PK lookup for full row",
                },
                {
                    "query": "SELECT id, name FROM employees WHERE name = 'Alice'",
                    "explain": {
                        "type": "ref",
                        "key": "idx_name",
                        "rows": 1,
                        "extra": "Using index",
                    },
                    "analysis": "Covering index! No PK lookup needed",
                },
                {
                    "query": "SELECT * FROM employees WHERE salary > 50000",
                    "explain": {
                        "type": "ALL",
                        "key": "NULL",
                        "rows": 1000,
                        "extra": "Using where",
                    },
                    "analysis": "Full table scan - no index on salary",
                },
            ],
        }

    def _get_optimization_tips(self) -> list:
        return [
            {
                "tip": "Choose Primary Key Wisely",
                "why": "PK determines physical row order and is stored in every secondary index",
                "do": "Use AUTO_INCREMENT or naturally sequential values",
                "dont": "Use UUID or random values as PK",
            },
            {
                "tip": "Select Only Needed Columns",
                "why": "Fewer columns = potential covering index, less I/O",
                "do": "SELECT id, name, email FROM users",
                "dont": "SELECT * FROM users",
            },
            {
                "tip": "Design Covering Indexes",
                "why": "Eliminates clustered index lookup (the 'double read')",
                "do": "INDEX(status, created_at, id) for status+date queries",
                "dont": "INDEX(status) then SELECT * (forces PK lookup)",
            },
            {
                "tip": "Mind Index Column Order",
                "why": "Leftmost prefix must be used for index to be effective",
                "do": "INDEX(a, b, c) works for WHERE a=? or WHERE a=? AND b=?",
                "dont": "INDEX(a, b, c) for WHERE b=? (can't use index)",
            },
            {
                "tip": "Keep Rows Small",
                "why": "More rows per page = fewer I/O operations",
                "do": "Use appropriate column types, normalize large text",
                "dont": "Store large BLOBs inline with frequently queried data",
            },
            {
                "tip": "Use EXPLAIN",
                "why": "Shows actual index usage and row estimates",
                "do": "Check 'type' and 'Extra' columns",
                "dont": "Assume your index is being used without checking",
            },
        ]
