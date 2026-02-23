"""
MySQL Introduction Concept - From Zero to Understanding Internals.
Covers what MySQL is, query types (DDL/DML/DCL/TCL), InnoDB basics,
page structure, and read/write flow.
"""

from typing import Any
import re

from app.concepts.base import BaseConcept, Step


class MySQLIntroConcept(BaseConcept):
    """Introduction to MySQL for complete beginners."""

    name = "mysql-intro"
    display_name = "Introduction to MySQL"
    description = "What is MySQL? Learn query types (DDL/DML/DCL), InnoDB storage, page structure, and how reads/writes work."
    difficulty = "beginner"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        """Generate visualization data for MySQL introduction."""
        query_type = self._detect_query_type(query)

        return {
            'query': query,
            'detected_type': query_type,
            'what_is_mysql': self._get_what_is_mysql(),
            'query_types': self._get_query_types(),
            'innodb_overview': self._get_innodb_overview(),
            'page_structure': self._get_page_structure(),
            'read_flow': self._get_read_flow(),
            'write_flow': self._get_write_flow(),
            'sample_queries_by_type': self._get_sample_queries_by_type(),
        }

    def _detect_query_type(self, query: str) -> dict:
        """Detect if query is DDL, DML, DCL, or TCL."""
        if not query or not query.strip():
            return {'type': None, 'category': None, 'color': 'gray'}

        query_upper = query.strip().upper()

        # DDL - Data Definition Language
        ddl_keywords = {
            'CREATE': 'CREATE',
            'ALTER': 'ALTER',
            'DROP': 'DROP',
            'TRUNCATE': 'TRUNCATE',
            'RENAME': 'RENAME',
        }
        for keyword, category in ddl_keywords.items():
            if query_upper.startswith(keyword):
                return {'type': 'DDL', 'category': category, 'color': 'blue', 'description': 'Data Definition Language - Defines database structure'}

        # DML - Data Manipulation Language
        dml_keywords = {
            'SELECT': 'SELECT',
            'INSERT': 'INSERT',
            'UPDATE': 'UPDATE',
            'DELETE': 'DELETE',
            'MERGE': 'MERGE',
            'REPLACE': 'REPLACE',
        }
        for keyword, category in dml_keywords.items():
            if query_upper.startswith(keyword):
                return {'type': 'DML', 'category': category, 'color': 'green', 'description': 'Data Manipulation Language - Works with data'}

        # DCL - Data Control Language
        dcl_keywords = {
            'GRANT': 'GRANT',
            'REVOKE': 'REVOKE',
        }
        for keyword, category in dcl_keywords.items():
            if query_upper.startswith(keyword):
                return {'type': 'DCL', 'category': category, 'color': 'orange', 'description': 'Data Control Language - Controls access permissions'}

        # TCL - Transaction Control Language
        tcl_keywords = {
            'COMMIT': 'COMMIT',
            'ROLLBACK': 'ROLLBACK',
            'SAVEPOINT': 'SAVEPOINT',
            'START TRANSACTION': 'START TRANSACTION',
            'BEGIN': 'BEGIN',
            'SET AUTOCOMMIT': 'SET AUTOCOMMIT',
        }
        for keyword, category in tcl_keywords.items():
            if query_upper.startswith(keyword):
                return {'type': 'TCL', 'category': category, 'color': 'purple', 'description': 'Transaction Control Language - Manages transactions'}

        # DQL could be separated but we'll keep SELECT under DML
        # Check for SHOW commands (MySQL specific)
        if query_upper.startswith('SHOW'):
            return {'type': 'DML', 'category': 'SHOW', 'color': 'green', 'description': 'Data Manipulation Language - Display information'}

        # Unknown
        return {'type': 'Unknown', 'category': query_upper.split()[0] if query_upper.split() else 'UNKNOWN', 'color': 'gray', 'description': 'Could not classify this query type'}

    def _get_what_is_mysql(self) -> dict:
        """Explain MySQL basics."""
        return {
            'title': 'What is MySQL?',
            'tagline': 'The world\'s most popular open-source relational database',
            'simple_explanation': 'MySQL is software that stores and organizes your data in a structured way, allowing you to easily find, update, and manage information.',
            'key_concepts': [
                {
                    'term': 'Database',
                    'definition': 'A collection of organized data (like a digital filing cabinet)',
                    'analogy': 'Think of it as a warehouse full of organized boxes',
                    'icon': 'database',
                },
                {
                    'term': 'Table',
                    'definition': 'A structured set of data organized in rows and columns',
                    'analogy': 'Like a spreadsheet with specific rules',
                    'icon': 'table',
                },
                {
                    'term': 'Row (Record)',
                    'definition': 'A single entry in a table (one complete unit of data)',
                    'analogy': 'One employee\'s complete information',
                    'icon': 'row',
                },
                {
                    'term': 'Column (Field)',
                    'definition': 'A specific attribute that all rows share',
                    'analogy': 'Name, Email, Salary - each is a column',
                    'icon': 'column',
                },
            ],
            'rdbms': {
                'full_form': 'Relational Database Management System',
                'meaning': 'Data is stored in tables that can relate to each other',
                'example': 'An employee belongs to a department - that\'s a relationship!',
            },
            'client_server': {
                'title': 'Client-Server Architecture',
                'description': 'MySQL runs as a server that clients connect to',
                'components': [
                    {'name': 'MySQL Server', 'role': 'Stores data, processes queries, manages connections'},
                    {'name': 'Client', 'role': 'Your app, command line, or tool that sends SQL queries'},
                    {'name': 'SQL', 'role': 'The language used to communicate with the server'},
                ],
            },
            'why_mysql': [
                {'point': 'Open Source', 'detail': 'Free to use and modify'},
                {'point': 'ACID Compliant', 'detail': 'Transactions are reliable and consistent'},
                {'point': 'Scalable', 'detail': 'Handles small apps to massive enterprises'},
                {'point': 'Well Supported', 'detail': 'Huge community, tons of resources'},
                {'point': 'Battle Tested', 'detail': 'Used by Facebook, Twitter, Netflix, and more'},
            ],
        }

    def _get_query_types(self) -> dict:
        """DDL, DML, DCL, TCL with examples."""
        return {
            'title': 'SQL Query Types',
            'description': 'SQL commands are categorized by what they do',
            'types': [
                {
                    'name': 'DDL',
                    'full_name': 'Data Definition Language',
                    'purpose': 'Define and modify database structure',
                    'color': 'blue',
                    'commands': [
                        {'command': 'CREATE', 'description': 'Create new tables, databases, indexes', 'example': 'CREATE TABLE users (id INT, name VARCHAR(100));'},
                        {'command': 'ALTER', 'description': 'Modify existing structure', 'example': 'ALTER TABLE users ADD email VARCHAR(255);'},
                        {'command': 'DROP', 'description': 'Delete tables or databases', 'example': 'DROP TABLE users;'},
                        {'command': 'TRUNCATE', 'description': 'Remove all rows from a table', 'example': 'TRUNCATE TABLE logs;'},
                    ],
                    'key_point': 'DDL changes are auto-committed (cannot be rolled back in MySQL)',
                },
                {
                    'name': 'DML',
                    'full_name': 'Data Manipulation Language',
                    'purpose': 'Work with the actual data',
                    'color': 'green',
                    'commands': [
                        {'command': 'SELECT', 'description': 'Retrieve data from tables', 'example': 'SELECT * FROM employees WHERE salary > 50000;'},
                        {'command': 'INSERT', 'description': 'Add new rows', 'example': "INSERT INTO employees (name, salary) VALUES ('Alice', 60000);"},
                        {'command': 'UPDATE', 'description': 'Modify existing rows', 'example': 'UPDATE employees SET salary = 70000 WHERE id = 1;'},
                        {'command': 'DELETE', 'description': 'Remove rows', 'example': 'DELETE FROM employees WHERE id = 1;'},
                    ],
                    'key_point': 'DML changes can be rolled back if inside a transaction',
                },
                {
                    'name': 'DCL',
                    'full_name': 'Data Control Language',
                    'purpose': 'Control access and permissions',
                    'color': 'orange',
                    'commands': [
                        {'command': 'GRANT', 'description': 'Give permissions to users', 'example': "GRANT SELECT ON database.* TO 'user'@'localhost';"},
                        {'command': 'REVOKE', 'description': 'Remove permissions from users', 'example': "REVOKE INSERT ON database.* FROM 'user'@'localhost';"},
                    ],
                    'key_point': 'DCL is about security - who can do what',
                },
                {
                    'name': 'TCL',
                    'full_name': 'Transaction Control Language',
                    'purpose': 'Manage transactions',
                    'color': 'purple',
                    'commands': [
                        {'command': 'START TRANSACTION', 'description': 'Begin a transaction', 'example': 'START TRANSACTION;'},
                        {'command': 'COMMIT', 'description': 'Save all changes permanently', 'example': 'COMMIT;'},
                        {'command': 'ROLLBACK', 'description': 'Undo all changes since last commit', 'example': 'ROLLBACK;'},
                        {'command': 'SAVEPOINT', 'description': 'Create a point to rollback to', 'example': "SAVEPOINT before_update;"},
                    ],
                    'key_point': 'Transactions group operations so they all succeed or all fail',
                },
            ],
        }

    def _get_innodb_overview(self) -> dict:
        """Simplified InnoDB architecture for beginners."""
        return {
            'title': 'InnoDB: The Storage Engine',
            'description': 'InnoDB is MySQL\'s default storage engine - the component that actually stores and retrieves your data.',
            'what_is_storage_engine': {
                'simple': 'The "how" behind storing data on disk and retrieving it',
                'analogy': 'If MySQL is a restaurant, InnoDB is the kitchen - it does the actual work behind the scenes',
            },
            'why_innodb': [
                {
                    'feature': 'ACID Transactions',
                    'meaning': 'Atomicity, Consistency, Isolation, Durability',
                    'benefit': 'Your data stays consistent even if the server crashes',
                },
                {
                    'feature': 'Row-Level Locking',
                    'meaning': 'Only locks the rows being modified',
                    'benefit': 'Multiple users can write to the same table simultaneously',
                },
                {
                    'feature': 'Foreign Keys',
                    'meaning': 'Enforces relationships between tables',
                    'benefit': 'Prevents orphaned data (e.g., order without a customer)',
                },
                {
                    'feature': 'Crash Recovery',
                    'meaning': 'Automatic recovery after unexpected shutdown',
                    'benefit': 'Your committed data is never lost',
                },
            ],
            'key_components': [
                {
                    'name': 'Buffer Pool',
                    'type': 'Memory',
                    'description': 'Caches data and index pages in RAM for fast access',
                    'icon': 'memory',
                },
                {
                    'name': 'Redo Log',
                    'type': 'Disk',
                    'description': 'Records all changes for crash recovery (Write-Ahead Log)',
                    'icon': 'log',
                },
                {
                    'name': 'Data Files',
                    'type': 'Disk',
                    'description': 'The actual .ibd files storing your table data',
                    'icon': 'file',
                },
            ],
            'acid_breakdown': [
                {'letter': 'A', 'term': 'Atomicity', 'meaning': 'All or nothing - transaction fully completes or fully fails'},
                {'letter': 'C', 'term': 'Consistency', 'meaning': 'Data always moves from one valid state to another'},
                {'letter': 'I', 'term': 'Isolation', 'meaning': 'Concurrent transactions don\'t interfere with each other'},
                {'letter': 'D', 'term': 'Durability', 'meaning': 'Once committed, data survives crashes and power failures'},
            ],
        }

    def _get_page_structure(self) -> dict:
        """16KB page layout with sections."""
        return {
            'title': 'Page Structure: How Data is Organized',
            'description': 'InnoDB stores data in 16KB pages - the fundamental unit of storage.',
            'why_pages': {
                'reason': 'Reading/writing in fixed-size chunks is efficient',
                'size': '16KB (16,384 bytes)',
                'analogy': 'Like a standard shipping container - everything fits the same size box',
            },
            'sections': [
                {
                    'name': 'Page Header',
                    'size': '38 bytes',
                    'purpose': 'Metadata about the page',
                    'contains': ['Page number', 'Previous/next page pointers', 'Page type', 'Checksum'],
                    'color': 'blue',
                },
                {
                    'name': 'Infimum & Supremum',
                    'size': '26 bytes',
                    'purpose': 'Virtual boundary records',
                    'contains': ['Infimum = smallest record (before all)', 'Supremum = largest record (after all)'],
                    'color': 'teal',
                },
                {
                    'name': 'User Records',
                    'size': 'Variable',
                    'purpose': 'Your actual data rows',
                    'contains': ['Row data', 'Row headers', 'Hidden columns (row_id, trx_id, roll_ptr)'],
                    'color': 'green',
                },
                {
                    'name': 'Free Space',
                    'size': 'Variable',
                    'purpose': 'Space for new records',
                    'contains': ['Unused space that shrinks as records are added'],
                    'color': 'gray',
                },
                {
                    'name': 'Page Directory',
                    'size': 'Variable',
                    'purpose': 'Speeds up record lookup',
                    'contains': ['Slots pointing to records', 'Enables binary search within page'],
                    'color': 'orange',
                },
                {
                    'name': 'Page Trailer',
                    'size': '8 bytes',
                    'purpose': 'Integrity checking',
                    'contains': ['Checksum (validates page isn\'t corrupted)'],
                    'color': 'red',
                },
            ],
            'page_types': [
                {'type': 'INDEX', 'description': 'Contains data or index records (most common)'},
                {'type': 'UNDO_LOG', 'description': 'Stores undo information for rollback'},
                {'type': 'INODE', 'description': 'Segment metadata'},
                {'type': 'ALLOCATED', 'description': 'Freshly allocated, not yet used'},
            ],
            'fun_fact': 'A 16KB page can hold roughly 400-500 typical rows, or just 2-3 rows if you have very large columns!',
        }

    def _get_read_flow(self) -> list:
        """Step-by-step read process."""
        return [
            {
                'step': 1,
                'title': 'Client Sends Query',
                'description': 'Your application sends a SELECT query to MySQL',
                'component': 'client',
                'detail': 'SELECT * FROM employees WHERE id = 5',
                'color': 'blue',
            },
            {
                'step': 2,
                'title': 'Query Parsing & Optimization',
                'description': 'MySQL parses the SQL, checks syntax, and creates an execution plan',
                'component': 'parser',
                'detail': 'Parser validates syntax, Optimizer chooses best index/path',
                'color': 'gray',
            },
            {
                'step': 3,
                'title': 'Check Buffer Pool',
                'description': 'Look for the needed data page in memory cache',
                'component': 'buffer_pool',
                'detail': 'If found (cache HIT) = fast! If not (cache MISS) = go to disk',
                'color': 'green',
            },
            {
                'step': 4,
                'title': 'Read from Disk (if needed)',
                'description': 'If page not in buffer pool, read it from the .ibd data file',
                'component': 'disk',
                'detail': 'This is the slow part - disk I/O takes milliseconds',
                'color': 'orange',
            },
            {
                'step': 5,
                'title': 'Load into Buffer Pool',
                'description': 'The page is loaded into buffer pool for future queries',
                'component': 'buffer_pool',
                'detail': 'Now subsequent queries for this page will be fast',
                'color': 'green',
            },
            {
                'step': 6,
                'title': 'Return Results',
                'description': 'MySQL extracts the matching rows and sends them back',
                'component': 'client',
                'detail': 'Results sent to client, query complete!',
                'color': 'blue',
            },
        ]

    def _get_write_flow(self) -> list:
        """Step-by-step write process with WAL."""
        return [
            {
                'step': 1,
                'title': 'Client Sends Write Query',
                'description': 'Your application sends an INSERT, UPDATE, or DELETE',
                'component': 'client',
                'detail': "INSERT INTO employees (name) VALUES ('Alice')",
                'color': 'blue',
            },
            {
                'step': 2,
                'title': 'Find/Load Page in Buffer Pool',
                'description': 'Locate the page to modify (load from disk if needed)',
                'component': 'buffer_pool',
                'detail': 'The page we need to modify must be in memory',
                'color': 'green',
            },
            {
                'step': 3,
                'title': 'Write to Redo Log (WAL)',
                'description': 'Record the change in the redo log FIRST',
                'component': 'redo_log',
                'detail': 'Write-Ahead Logging: log the change before modifying data',
                'color': 'orange',
                'important': True,
            },
            {
                'step': 4,
                'title': 'Modify Page in Buffer Pool',
                'description': 'Apply the change to the in-memory page (now "dirty")',
                'component': 'buffer_pool',
                'detail': 'Page is modified in RAM but not yet written to disk',
                'color': 'green',
            },
            {
                'step': 5,
                'title': 'Acknowledge to Client',
                'description': 'On COMMIT, tell the client the write succeeded',
                'component': 'client',
                'detail': 'Client gets OK - even though data isn\'t on disk yet!',
                'color': 'blue',
            },
            {
                'step': 6,
                'title': 'Background Flush to Disk',
                'description': 'Later, dirty pages are written to data files',
                'component': 'disk',
                'detail': 'Checkpoint process writes dirty pages to .ibd files',
                'color': 'purple',
                'async': True,
            },
        ]

    def _get_sample_queries_by_type(self) -> dict:
        """Sample queries organized by type."""
        return {
            'DDL': [
                "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100));",
                "ALTER TABLE users ADD email VARCHAR(255);",
                "DROP TABLE users;",
            ],
            'DML': [
                "SELECT * FROM employees WHERE salary > 50000;",
                "INSERT INTO employees (name, salary) VALUES ('John', 60000);",
                "UPDATE employees SET salary = 70000 WHERE id = 1;",
                "DELETE FROM employees WHERE id = 1;",
            ],
            'DCL': [
                "GRANT SELECT ON database.* TO 'user'@'localhost';",
                "REVOKE INSERT ON database.* FROM 'user'@'localhost';",
            ],
            'TCL': [
                "START TRANSACTION;",
                "COMMIT;",
                "ROLLBACK;",
            ],
        }

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        """Return step-by-step breakdown for animation."""
        return [
            Step(
                title="What is MySQL?",
                description="MySQL is a relational database management system (RDBMS) that stores data in tables with relationships.",
                highlight={'section': 'intro'}
            ),
            Step(
                title="Tables, Rows & Columns",
                description="Data is organized in tables (like spreadsheets). Rows are records, columns are attributes.",
                highlight={'section': 'tables'}
            ),
            Step(
                title="Query Types: DDL",
                description="Data Definition Language - CREATE, ALTER, DROP. These define the structure of your database.",
                highlight={'section': 'ddl'}
            ),
            Step(
                title="Query Types: DML",
                description="Data Manipulation Language - SELECT, INSERT, UPDATE, DELETE. These work with actual data.",
                highlight={'section': 'dml'}
            ),
            Step(
                title="Query Types: DCL & TCL",
                description="DCL controls permissions (GRANT/REVOKE). TCL manages transactions (COMMIT/ROLLBACK).",
                highlight={'section': 'dcl'}
            ),
            Step(
                title="InnoDB Storage Engine",
                description="InnoDB is MySQL's default engine. It provides ACID transactions, row-level locking, and crash recovery.",
                highlight={'section': 'innodb'}
            ),
            Step(
                title="16KB Pages",
                description="InnoDB stores data in 16KB pages - the smallest unit of I/O. Pages contain headers, records, and directories.",
                highlight={'section': 'pages'}
            ),
            Step(
                title="How Reads Work",
                description="SELECT queries check the Buffer Pool (RAM cache) first. On cache miss, data is loaded from disk.",
                highlight={'section': 'reads'}
            ),
            Step(
                title="How Writes Work",
                description="Writes go to the Redo Log first (WAL), then modify pages in memory. Dirty pages are flushed to disk later.",
                highlight={'section': 'writes'}
            ),
        ]

    def get_sample_queries(self) -> list[str]:
        """Return sample queries for this concept."""
        return [
            # DDL
            "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100));",
            "ALTER TABLE users ADD email VARCHAR(255);",
            # DML
            "SELECT * FROM employees",
            "SELECT name, salary FROM employees WHERE salary > 50000",
            "INSERT INTO employees (name, salary) VALUES ('Alice', 60000);",
            "UPDATE employees SET salary = 70000 WHERE id = 1;",
            # DCL
            "GRANT SELECT ON mydb.* TO 'reader'@'localhost';",
            # TCL
            "START TRANSACTION;",
            "COMMIT;",
        ]
