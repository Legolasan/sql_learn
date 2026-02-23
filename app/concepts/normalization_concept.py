"""Database normalization visualization concept."""

from typing import Any

from app.concepts.base import BaseConcept, Step


class NormalizationConcept(BaseConcept):
    name = "normalization"
    display_name = "Normalization"
    description = "Learn 1NF, 2NF, 3NF and when to denormalize. See how to eliminate data redundancy."
    difficulty = "intermediate"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        # Unnormalized example
        unnormalized = {
            'table': 'orders_denormalized',
            'description': 'Everything in one table - lots of redundancy!',
            'data': [
                {'order_id': 1, 'customer_name': 'Alice', 'customer_email': 'alice@email.com', 'customer_city': 'NYC', 'product_name': 'Laptop', 'product_price': 999, 'quantity': 1},
                {'order_id': 2, 'customer_name': 'Alice', 'customer_email': 'alice@email.com', 'customer_city': 'NYC', 'product_name': 'Mouse', 'product_price': 29, 'quantity': 2},
                {'order_id': 3, 'customer_name': 'Bob', 'customer_email': 'bob@email.com', 'customer_city': 'LA', 'product_name': 'Laptop', 'product_price': 999, 'quantity': 1},
            ],
            'problems': [
                'Customer info repeated for each order',
                'Product price repeated',
                'Update anomaly: change Alice\'s email in one row but not others',
                'Delete anomaly: deleting last order loses customer data',
                'Insert anomaly: can\'t add customer without an order'
            ]
        }

        # Normal forms
        normal_forms = [
            {
                'form': '1NF',
                'name': 'First Normal Form',
                'rule': 'Eliminate repeating groups. Each cell contains single value.',
                'violation_example': {
                    'bad': {'order_id': 1, 'products': 'Laptop, Mouse, Keyboard'},
                    'good': [
                        {'order_id': 1, 'product': 'Laptop'},
                        {'order_id': 1, 'product': 'Mouse'},
                        {'order_id': 1, 'product': 'Keyboard'}
                    ]
                },
                'fix': 'Create separate row for each value, or separate table',
                'achieved_by': 'Atomic values in each column'
            },
            {
                'form': '2NF',
                'name': 'Second Normal Form',
                'rule': 'Remove partial dependencies. Non-key columns depend on WHOLE primary key.',
                'violation_example': {
                    'table': 'order_items(order_id, product_id, product_name, quantity)',
                    'problem': 'product_name depends only on product_id, not (order_id, product_id)',
                },
                'fix': 'Move product_name to products table',
                'achieved_by': 'Each non-key column depends on entire composite key'
            },
            {
                'form': '3NF',
                'name': 'Third Normal Form',
                'rule': 'Remove transitive dependencies. Non-key columns depend ONLY on primary key.',
                'violation_example': {
                    'table': 'employees(emp_id, dept_id, dept_name, dept_location)',
                    'problem': 'dept_name depends on dept_id, not emp_id (transitive)',
                },
                'fix': 'Create separate departments table',
                'achieved_by': 'No non-key column depends on another non-key column'
            },
            {
                'form': 'BCNF',
                'name': 'Boyce-Codd Normal Form',
                'rule': 'Every determinant is a candidate key.',
                'violation_example': {
                    'table': 'student_courses(student, course, professor)',
                    'problem': 'professor → course (each professor teaches one course), but professor isn\'t a key',
                },
                'fix': 'Split into (student, professor) and (professor, course)',
                'achieved_by': 'Stricter version of 3NF'
            }
        ]

        # Normalized schema example
        normalized = {
            'tables': [
                {
                    'name': 'customers',
                    'columns': ['customer_id (PK)', 'name', 'email', 'city'],
                    'sample': [
                        {'customer_id': 1, 'name': 'Alice', 'email': 'alice@email.com', 'city': 'NYC'},
                        {'customer_id': 2, 'name': 'Bob', 'email': 'bob@email.com', 'city': 'LA'}
                    ]
                },
                {
                    'name': 'products',
                    'columns': ['product_id (PK)', 'name', 'price'],
                    'sample': [
                        {'product_id': 1, 'name': 'Laptop', 'price': 999},
                        {'product_id': 2, 'name': 'Mouse', 'price': 29}
                    ]
                },
                {
                    'name': 'orders',
                    'columns': ['order_id (PK)', 'customer_id (FK)', 'order_date'],
                    'sample': [
                        {'order_id': 1, 'customer_id': 1, 'order_date': '2024-01-15'},
                        {'order_id': 2, 'customer_id': 1, 'order_date': '2024-01-16'}
                    ]
                },
                {
                    'name': 'order_items',
                    'columns': ['order_id (FK)', 'product_id (FK)', 'quantity'],
                    'sample': [
                        {'order_id': 1, 'product_id': 1, 'quantity': 1},
                        {'order_id': 2, 'product_id': 2, 'quantity': 2}
                    ]
                }
            ],
            'benefits': [
                'No data redundancy',
                'Update customer email in ONE place',
                'Can add customer without order',
                'Delete order without losing customer',
                'Consistent data guaranteed'
            ]
        }

        # When to denormalize
        denormalization = {
            'title': 'When to Denormalize',
            'description': 'Sometimes breaking normalization improves performance',
            'valid_reasons': [
                'Heavy read workloads with complex JOINs',
                'Analytics/reporting tables',
                'Caching frequently accessed computed values',
                'Reducing JOIN count for critical queries'
            ],
            'techniques': [
                {'name': 'Redundant columns', 'example': 'Store customer_name in orders to avoid JOIN'},
                {'name': 'Summary tables', 'example': 'Pre-computed daily_sales aggregates'},
                {'name': 'Materialized views', 'example': 'Cached query results'},
            ],
            'tradeoffs': [
                'More storage space',
                'Update anomalies (must update multiple places)',
                'Complexity in keeping data in sync'
            ]
        }

        # Constraints deep-dive
        constraints = {
            'title': 'Database Constraints',
            'description': 'Constraints enforce data integrity rules at the database level',
            'types': [
                {
                    'name': 'PRIMARY KEY',
                    'description': 'Unique identifier for each row. Cannot be NULL.',
                    'syntax': 'PRIMARY KEY (column)',
                    'example': 'id INT PRIMARY KEY AUTO_INCREMENT',
                },
                {
                    'name': 'FOREIGN KEY',
                    'description': 'References primary key in another table. Enforces referential integrity.',
                    'syntax': 'FOREIGN KEY (col) REFERENCES table(col)',
                    'example': 'FOREIGN KEY (dept_id) REFERENCES departments(id)',
                    'cascade_options': [
                        {'action': 'ON DELETE CASCADE', 'effect': 'Delete child rows when parent deleted'},
                        {'action': 'ON DELETE SET NULL', 'effect': 'Set FK to NULL when parent deleted'},
                        {'action': 'ON DELETE RESTRICT', 'effect': 'Prevent deletion if children exist (default)'},
                        {'action': 'ON UPDATE CASCADE', 'effect': 'Update FK when parent PK changes'},
                    ],
                },
                {
                    'name': 'UNIQUE',
                    'description': 'No duplicate values allowed. Can be NULL (unless NOT NULL also specified).',
                    'syntax': 'UNIQUE (column)',
                    'example': 'email VARCHAR(255) UNIQUE',
                },
                {
                    'name': 'NOT NULL',
                    'description': 'Column cannot contain NULL values.',
                    'syntax': 'column_name TYPE NOT NULL',
                    'example': 'name VARCHAR(100) NOT NULL',
                },
                {
                    'name': 'CHECK',
                    'description': 'Custom validation rule for column values.',
                    'syntax': 'CHECK (condition)',
                    'example': 'age INT CHECK (age >= 0 AND age <= 150)',
                    'note': 'MySQL 8.0.16+ enforces CHECK constraints (earlier versions parsed but ignored them)',
                },
                {
                    'name': 'DEFAULT',
                    'description': 'Default value when no value is provided on INSERT.',
                    'syntax': 'DEFAULT value',
                    'example': 'status VARCHAR(20) DEFAULT \'active\'',
                },
            ],
        }

        # Generated/Computed columns
        generated_columns = {
            'title': 'Generated (Computed) Columns',
            'description': 'Columns whose values are computed from other columns',
            'types': [
                {
                    'name': 'VIRTUAL',
                    'storage': 'Not stored on disk - computed on read',
                    'pros': ['No extra storage', 'Always up-to-date'],
                    'cons': ['Computed every read', 'Cannot be indexed in all cases'],
                    'syntax': 'col_name TYPE AS (expression) VIRTUAL',
                },
                {
                    'name': 'STORED',
                    'storage': 'Stored on disk - computed on write',
                    'pros': ['No computation on read', 'Can be indexed'],
                    'cons': ['Uses disk space', 'Must be updated on write'],
                    'syntax': 'col_name TYPE AS (expression) STORED',
                },
            ],
            'examples': [
                {
                    'name': 'Full Name',
                    'sql': 'full_name VARCHAR(200) AS (CONCAT(first_name, \' \', last_name)) VIRTUAL',
                    'use_case': 'Combine first and last name without storing',
                },
                {
                    'name': 'Age from Birth Date',
                    'sql': 'age INT AS (TIMESTAMPDIFF(YEAR, birth_date, CURDATE())) VIRTUAL',
                    'use_case': 'Calculate age dynamically',
                },
                {
                    'name': 'Total Price',
                    'sql': 'total DECIMAL(10,2) AS (quantity * unit_price) STORED',
                    'use_case': 'Pre-compute for faster queries, can be indexed',
                },
                {
                    'name': 'JSON Extract',
                    'sql': 'email VARCHAR(255) AS (JSON_UNQUOTE(JSON_EXTRACT(data, \'$.email\'))) STORED',
                    'use_case': 'Extract JSON field for indexing',
                },
            ],
        }

        # Extended denormalization with tradeoffs
        denormalization_extended = {
            'title': 'Denormalization Deep Dive',
            'description': 'Strategic breaking of normal forms for performance',
            'when_to_denormalize': [
                'Read-heavy workloads (90%+ reads)',
                'Complex reporting queries with many JOINs',
                'Real-time dashboards needing fast response',
                'Data that rarely changes',
            ],
            'when_not_to_denormalize': [
                'Write-heavy applications',
                'Data that changes frequently',
                'When data consistency is critical',
                'Early in development (optimize later)',
            ],
            'techniques': [
                {
                    'name': 'Redundant Columns',
                    'description': 'Store frequently accessed data in multiple tables',
                    'example': {
                        'normalized': 'SELECT o.*, c.name FROM orders o JOIN customers c ON o.customer_id = c.id',
                        'denormalized': 'SELECT * FROM orders -- customer_name stored in orders table',
                    },
                    'tradeoff': 'Faster reads, but must update customer_name in orders when customer changes',
                },
                {
                    'name': 'Summary Tables',
                    'description': 'Pre-aggregated data for reporting',
                    'example': {
                        'realtime': 'SELECT DATE(order_date), SUM(total) FROM orders GROUP BY DATE(order_date)',
                        'summary': 'SELECT * FROM daily_sales -- pre-computed each night',
                    },
                    'tradeoff': 'Instant reporting, but data may be stale',
                },
                {
                    'name': 'Materialized Data',
                    'description': 'Cache complex calculations or derived values',
                    'example': {
                        'computed': 'SELECT *, (SELECT AVG(score) FROM reviews WHERE product_id = p.id) FROM products p',
                        'cached': 'SELECT *, avg_rating FROM products -- avg_rating column updated via trigger',
                    },
                    'tradeoff': 'Fast reads, requires trigger/job to maintain',
                },
            ],
            'schema_comparison': {
                'title': 'Normalized vs Denormalized Schema',
                'normalized': {
                    'tables': ['customers', 'orders', 'order_items', 'products'],
                    'joins_for_report': 4,
                    'storage': 'Minimal (no redundancy)',
                    'write_speed': 'Fast (update one place)',
                    'read_speed': 'Slower (many JOINs)',
                    'consistency': 'Guaranteed',
                },
                'denormalized': {
                    'tables': ['order_details_flat'],
                    'joins_for_report': 0,
                    'storage': 'Higher (redundant data)',
                    'write_speed': 'Slower (update many rows)',
                    'read_speed': 'Fast (single table scan)',
                    'consistency': 'Risk of anomalies',
                },
            },
        }

        return {
            'query': query,
            'unnormalized': unnormalized,
            'normal_forms': normal_forms,
            'normalized': normalized,
            'denormalization': denormalization,
            'constraints': constraints,
            'generated_columns': generated_columns,
            'denormalization_extended': denormalization_extended,
        }

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        return [
            Step(
                title="Start: Unnormalized Data",
                description="All data in one table with lots of redundancy",
                highlight={'stage': 'unnormalized'}
            ),
            Step(
                title="1NF: Atomic Values",
                description="Each cell contains single value, no repeating groups",
                highlight={'form': '1NF'}
            ),
            Step(
                title="2NF: No Partial Dependencies",
                description="Non-key columns depend on WHOLE primary key",
                highlight={'form': '2NF'}
            ),
            Step(
                title="3NF: No Transitive Dependencies",
                description="Non-key columns depend ONLY on primary key",
                highlight={'form': '3NF'}
            ),
            Step(
                title="Result: Normalized Schema",
                description="Separate tables for customers, products, orders, order_items",
                highlight={'stage': 'normalized'}
            ),
            Step(
                title="Consider: Denormalization",
                description="Sometimes break rules for performance - but carefully!",
                highlight={'denorm': True}
            ),
            Step(
                title="Database Constraints",
                description="Enforce data integrity with PRIMARY KEY, FOREIGN KEY, UNIQUE, CHECK, and DEFAULT constraints.",
                highlight={'constraints': True}
            ),
            Step(
                title="Generated Columns",
                description="Compute column values automatically from other columns (VIRTUAL or STORED).",
                highlight={'generated': True}
            ),
        ]

    def get_sample_queries(self) -> list[str]:
        return [
            "SELECT * FROM orders_denormalized",
            "SELECT o.*, c.name, c.email FROM orders o JOIN customers c ON o.customer_id = c.id",
            "SELECT c.name, COUNT(*) as order_count FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.id",
        ]
