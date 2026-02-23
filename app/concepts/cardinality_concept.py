"""
Cardinality & Keys Concept - Primary keys, foreign keys, unique constraints,
and relationship types (one-to-one, one-to-many, many-to-many).
"""

from typing import Any

from app.concepts.base import BaseConcept, Step


class CardinalityConcept(BaseConcept):
    """Concept covering database keys and relationship cardinality."""

    name = "cardinality-keys"
    display_name = "Cardinality & Keys"
    description = "Understand PK/FK constraints, UNIQUE, and relationship types (1:1, 1:N, M:N) with constraint demos"
    difficulty = "intermediate"

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        return [
            Step(
                title="Why Keys Matter",
                description="Keys uniquely identify rows and establish relationships between tables. Without them, data integrity falls apart.",
                highlight={'section': 'overview'}
            ),
            Step(
                title="Primary Keys (PK)",
                description="A unique identifier for each row. Every table should have one. Cannot be NULL, must be unique.",
                highlight={'key_type': 'pk'}
            ),
            Step(
                title="Foreign Keys (FK)",
                description="A column that references another table's primary key. Creates relationships and enforces referential integrity.",
                highlight={'key_type': 'fk'}
            ),
            Step(
                title="UNIQUE Constraints",
                description="Ensures column values are unique across all rows. Unlike PK, can have multiple UNIQUE constraints and NULL values.",
                highlight={'key_type': 'unique'}
            ),
            Step(
                title="One-to-One (1:1)",
                description="Each row in Table A relates to exactly one row in Table B, and vice versa. Rare - often data can be in same table.",
                highlight={'relationship': '1:1'}
            ),
            Step(
                title="One-to-Many (1:N)",
                description="One row in Table A can relate to many rows in Table B. The most common relationship type. FK goes on the 'many' side.",
                highlight={'relationship': '1:N'}
            ),
            Step(
                title="Many-to-Many (M:N)",
                description="Many rows in A can relate to many rows in B. Requires a junction/bridge table with FKs to both tables.",
                highlight={'relationship': 'M:N'}
            ),
            Step(
                title="Surrogate vs Natural Keys",
                description="Surrogate keys are artificial IDs (auto-increment). Natural keys use real data (email, SSN). Trade-offs exist for both.",
                highlight={'section': 'keys_comparison'}
            ),
        ]

    def get_sample_queries(self) -> list[str]:
        return [
            # Show relationships
            "SELECT e.id, e.name, e.department_id, d.name AS dept FROM employees e JOIN departments d ON e.department_id = d.id",

            # Find orphaned records (no FK constraint demo)
            "SELECT e.name FROM employees e WHERE e.department_id NOT IN (SELECT id FROM departments)",

            # Show one-to-many
            "SELECT d.name AS department, COUNT(e.id) AS employee_count FROM departments d LEFT JOIN employees e ON d.id = e.department_id GROUP BY d.id, d.name",

            # Many-to-many through junction table
            "SELECT o.id AS order_id, p.name AS product, oi.quantity FROM orders o JOIN order_items oi ON o.id = oi.order_id JOIN products p ON oi.product_id = p.id",

            # Self-referential FK (manager)
            "SELECT e.name, m.name AS manager FROM employees e LEFT JOIN employees m ON e.manager_id = m.id",

            # Find duplicate values (what UNIQUE prevents)
            "SELECT department_id, COUNT(*) as emp_count FROM employees GROUP BY department_id HAVING COUNT(*) > 1",
        ]

    def get_visualization_data(self, query: str, dataset) -> dict:
        """Generate visualization data for cardinality concepts."""
        return {
            "key_types": self._get_key_types(),
            "relationships": self._get_relationship_types(),
            "our_schema": self._get_schema_diagram(dataset),
            "constraint_demo": self._get_constraint_demo(),
            "surrogate_vs_natural": self._get_key_comparison(),
            "common_mistakes": self._get_common_mistakes(),
            "best_practices": self._get_best_practices(),
        }

    def _get_key_types(self) -> dict:
        """Explain different key types."""
        return {
            "title": "Database Key Types",
            "keys": [
                {
                    "name": "PRIMARY KEY",
                    "symbol": "PK",
                    "color": "yellow",
                    "description": "Uniquely identifies each row in a table",
                    "rules": [
                        "Must be UNIQUE",
                        "Cannot be NULL",
                        "Only ONE per table",
                        "Creates clustered index (usually)",
                    ],
                    "syntax": "id INT PRIMARY KEY AUTO_INCREMENT",
                    "examples": ["id", "employee_id", "order_number"],
                },
                {
                    "name": "FOREIGN KEY",
                    "symbol": "FK",
                    "color": "blue",
                    "description": "References a primary key in another table",
                    "rules": [
                        "Must match a PK value (or be NULL)",
                        "Enforces referential integrity",
                        "Can have multiple per table",
                        "Creates relationship between tables",
                    ],
                    "syntax": """department_id INT,
FOREIGN KEY (department_id) REFERENCES departments(id)""",
                    "examples": ["department_id -> departments.id", "customer_id -> customers.id"],
                },
                {
                    "name": "UNIQUE",
                    "symbol": "UQ",
                    "color": "green",
                    "description": "Ensures no duplicate values in column",
                    "rules": [
                        "Values must be unique",
                        "NULL is allowed (one NULL per column)",
                        "Can have multiple per table",
                        "Creates non-clustered index",
                    ],
                    "syntax": "email VARCHAR(255) UNIQUE",
                    "examples": ["email", "username", "ssn"],
                },
                {
                    "name": "COMPOSITE KEY",
                    "symbol": "CK",
                    "color": "purple",
                    "description": "Primary key made of multiple columns",
                    "rules": [
                        "Combination must be unique",
                        "Common in junction tables",
                        "Each column can repeat individually",
                    ],
                    "syntax": "PRIMARY KEY (order_id, product_id)",
                    "examples": ["(order_id, product_id)", "(student_id, course_id)"],
                },
            ],
        }

    def _get_relationship_types(self) -> dict:
        """Explain cardinality relationships."""
        return {
            "title": "Relationship Cardinality",
            "types": [
                {
                    "name": "One-to-One (1:1)",
                    "notation": "1 ──── 1",
                    "description": "Each row in A matches exactly one row in B",
                    "real_examples": [
                        "User ↔ UserProfile",
                        "Employee ↔ ParkingSpot",
                        "Country ↔ Capital",
                    ],
                    "implementation": "Put FK in either table with UNIQUE constraint",
                    "sql_example": """CREATE TABLE user_profiles (
    id INT PRIMARY KEY,
    user_id INT UNIQUE,  -- UNIQUE enforces 1:1
    FOREIGN KEY (user_id) REFERENCES users(id)
);""",
                    "when_to_use": [
                        "Separating rarely-accessed data",
                        "Optional extensions to a table",
                        "Security isolation (sensitive fields)",
                    ],
                    "warning": "Often a sign you should just have one table",
                },
                {
                    "name": "One-to-Many (1:N)",
                    "notation": "1 ──── *",
                    "description": "One row in A can relate to many rows in B",
                    "real_examples": [
                        "Department → Employees",
                        "Customer → Orders",
                        "Author → Books",
                        "Category → Products",
                    ],
                    "implementation": "Put FK on the 'many' side (child table)",
                    "sql_example": """-- Department (1) to Employees (N)
CREATE TABLE employees (
    id INT PRIMARY KEY,
    department_id INT,  -- FK on the 'many' side
    FOREIGN KEY (department_id) REFERENCES departments(id)
);""",
                    "key_insight": "The FK always goes on the 'many' side!",
                },
                {
                    "name": "Many-to-Many (M:N)",
                    "notation": "* ──── *",
                    "description": "Many rows in A can relate to many rows in B",
                    "real_examples": [
                        "Students ↔ Courses",
                        "Orders ↔ Products",
                        "Users ↔ Roles",
                        "Actors ↔ Movies",
                    ],
                    "implementation": "Create a junction/bridge table with FKs to both",
                    "sql_example": """-- Orders (M) to Products (N)
CREATE TABLE order_items (  -- Junction table
    id INT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE (order_id, product_id)  -- Prevent duplicate entries
);""",
                    "junction_table_tips": [
                        "Name it: table1_table2 or describe the relationship",
                        "Can add extra columns (quantity, timestamp)",
                        "Consider composite PK vs surrogate ID",
                    ],
                },
                {
                    "name": "Self-Referential",
                    "notation": "─┐\n │\n─┘",
                    "description": "Table references itself",
                    "real_examples": [
                        "Employee → Manager (also an Employee)",
                        "Category → ParentCategory",
                        "Comment → ParentComment (threads)",
                    ],
                    "implementation": "FK references same table's PK",
                    "sql_example": """CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    manager_id INT,  -- References same table!
    FOREIGN KEY (manager_id) REFERENCES employees(id)
);""",
                },
            ],
        }

    def _get_schema_diagram(self, dataset) -> dict:
        """Generate schema diagram for our sample database."""
        return {
            "title": "Our Sample Database Schema",
            "tables": [
                {
                    "name": "departments",
                    "columns": [
                        {"name": "id", "type": "INT", "key": "PK"},
                        {"name": "name", "type": "VARCHAR(100)", "key": None},
                        {"name": "budget", "type": "DECIMAL", "key": None},
                        {"name": "location", "type": "VARCHAR(100)", "key": None, "nullable": True},
                    ],
                },
                {
                    "name": "employees",
                    "columns": [
                        {"name": "id", "type": "INT", "key": "PK"},
                        {"name": "name", "type": "VARCHAR(100)", "key": None},
                        {"name": "department_id", "type": "INT", "key": "FK", "references": "departments.id"},
                        {"name": "manager_id", "type": "INT", "key": "FK", "references": "employees.id", "nullable": True},
                        {"name": "salary", "type": "DECIMAL", "key": None},
                        {"name": "hire_date", "type": "DATE", "key": None},
                        {"name": "email", "type": "VARCHAR(255)", "key": "UQ", "nullable": True},
                        {"name": "phone", "type": "VARCHAR(20)", "key": None, "nullable": True},
                    ],
                },
                {
                    "name": "customers",
                    "columns": [
                        {"name": "id", "type": "INT", "key": "PK"},
                        {"name": "name", "type": "VARCHAR(100)", "key": None},
                        {"name": "email", "type": "VARCHAR(255)", "key": "UQ"},
                        {"name": "city", "type": "VARCHAR(100)", "key": None, "nullable": True},
                        {"name": "country", "type": "VARCHAR(100)", "key": None},
                        {"name": "credit_limit", "type": "DECIMAL", "key": None, "nullable": True},
                    ],
                },
                {
                    "name": "orders",
                    "columns": [
                        {"name": "id", "type": "INT", "key": "PK"},
                        {"name": "customer_id", "type": "INT", "key": "FK", "references": "customers.id"},
                        {"name": "employee_id", "type": "INT", "key": "FK", "references": "employees.id"},
                        {"name": "order_date", "type": "DATE", "key": None},
                        {"name": "shipped_date", "type": "DATE", "key": None, "nullable": True},
                        {"name": "status", "type": "VARCHAR(20)", "key": None},
                    ],
                },
                {
                    "name": "products",
                    "columns": [
                        {"name": "id", "type": "INT", "key": "PK"},
                        {"name": "name", "type": "VARCHAR(100)", "key": None},
                        {"name": "category", "type": "VARCHAR(50)", "key": None},
                        {"name": "price", "type": "DECIMAL", "key": None},
                        {"name": "stock_quantity", "type": "INT", "key": None},
                    ],
                },
                {
                    "name": "order_items",
                    "columns": [
                        {"name": "id", "type": "INT", "key": "PK"},
                        {"name": "order_id", "type": "INT", "key": "FK", "references": "orders.id"},
                        {"name": "product_id", "type": "INT", "key": "FK", "references": "products.id"},
                        {"name": "quantity", "type": "INT", "key": None},
                        {"name": "unit_price", "type": "DECIMAL", "key": None},
                        {"name": "discount", "type": "DECIMAL", "key": None, "nullable": True},
                    ],
                },
            ],
            "relationships": [
                {"from": "employees.department_id", "to": "departments.id", "type": "N:1", "label": "works in"},
                {"from": "employees.manager_id", "to": "employees.id", "type": "N:1", "label": "reports to"},
                {"from": "orders.customer_id", "to": "customers.id", "type": "N:1", "label": "placed by"},
                {"from": "orders.employee_id", "to": "employees.id", "type": "N:1", "label": "handled by"},
                {"from": "order_items.order_id", "to": "orders.id", "type": "N:1", "label": "part of"},
                {"from": "order_items.product_id", "to": "products.id", "type": "N:1", "label": "contains"},
            ],
        }

    def _get_constraint_demo(self) -> dict:
        """Demo showing what happens with/without constraints."""
        return {
            "title": "What Happens Without Constraints?",
            "scenarios": [
                {
                    "name": "Without Primary Key",
                    "problem": "Duplicate rows can exist",
                    "example_bad": """INSERT INTO employees VALUES (1, 'Alice', 1);
INSERT INTO employees VALUES (1, 'Alice', 1);  -- Duplicate allowed!""",
                    "result": "Two identical rows - which is the 'real' Alice?",
                    "fix": "PRIMARY KEY prevents duplicate IDs",
                },
                {
                    "name": "Without Foreign Key",
                    "problem": "Orphaned records can exist",
                    "example_bad": """INSERT INTO employees (id, name, department_id) VALUES (1, 'Bob', 999);
-- department_id 999 doesn't exist!""",
                    "result": "Bob references a non-existent department",
                    "fix": "FOREIGN KEY ensures referenced row exists",
                },
                {
                    "name": "Without UNIQUE",
                    "problem": "Duplicate business values allowed",
                    "example_bad": """INSERT INTO users (email) VALUES ('alice@example.com');
INSERT INTO users (email) VALUES ('alice@example.com');  -- Duplicate!""",
                    "result": "Two users with same email - which gets the password reset?",
                    "fix": "UNIQUE constraint on email column",
                },
                {
                    "name": "Without NOT NULL",
                    "problem": "Missing required data",
                    "example_bad": """INSERT INTO orders (id, customer_id) VALUES (1, NULL);
-- No customer for this order!""",
                    "result": "Order exists but we don't know who placed it",
                    "fix": "NOT NULL on customer_id",
                },
            ],
            "cascade_actions": {
                "title": "FK Cascade Options",
                "options": [
                    {
                        "action": "ON DELETE CASCADE",
                        "effect": "Delete child rows when parent is deleted",
                        "example": "Delete department → all employees deleted",
                        "use_when": "Child data is meaningless without parent",
                    },
                    {
                        "action": "ON DELETE SET NULL",
                        "effect": "Set FK to NULL when parent is deleted",
                        "example": "Delete department → employees.department_id = NULL",
                        "use_when": "Child can exist without parent",
                    },
                    {
                        "action": "ON DELETE RESTRICT",
                        "effect": "Prevent deletion if children exist",
                        "example": "Can't delete department with employees",
                        "use_when": "Want explicit cleanup before deletion",
                    },
                    {
                        "action": "ON UPDATE CASCADE",
                        "effect": "Update child FKs when parent PK changes",
                        "example": "Rarely needed if using surrogate keys",
                        "use_when": "Natural keys that might change",
                    },
                ],
            },
        }

    def _get_key_comparison(self) -> dict:
        """Compare surrogate vs natural keys."""
        return {
            "title": "Surrogate vs Natural Keys",
            "surrogate": {
                "name": "Surrogate Key",
                "definition": "Artificial identifier with no business meaning",
                "examples": ["id INT AUTO_INCREMENT", "UUID", "GUID"],
                "pros": [
                    "Never changes (stable references)",
                    "Small and fast (usually INT)",
                    "Simple to generate",
                    "No business logic dependency",
                ],
                "cons": [
                    "No business meaning",
                    "Requires lookup for human readability",
                    "Extra column in table",
                    "Sequential IDs can leak info (order count)",
                ],
                "sql": """CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,  -- Surrogate
    sku VARCHAR(50) UNIQUE,  -- Natural key kept for business use
    name VARCHAR(100)
);""",
            },
            "natural": {
                "name": "Natural Key",
                "definition": "Real-world identifier with business meaning",
                "examples": ["email", "SSN", "ISBN", "SKU", "country_code"],
                "pros": [
                    "Meaningful - no lookup needed",
                    "Already exists in data",
                    "Enforces business uniqueness",
                    "Good for small lookup tables",
                ],
                "cons": [
                    "Can change (email, phone)",
                    "May be large (VARCHAR vs INT)",
                    "Privacy concerns (SSN as key)",
                    "Composite natural keys are complex",
                ],
                "sql": """CREATE TABLE countries (
    code CHAR(2) PRIMARY KEY,  -- 'US', 'UK', 'CA'
    name VARCHAR(100)
);""",
            },
            "recommendation": {
                "use_surrogate": [
                    "Most tables (employees, orders, products)",
                    "When natural key might change",
                    "When natural key is large",
                    "Junction/bridge tables",
                ],
                "use_natural": [
                    "Small lookup tables (countries, currencies)",
                    "When natural key is small and stable",
                    "Status/type enums",
                    "When business requires specific IDs",
                ],
                "hybrid": "Use surrogate PK + UNIQUE constraint on natural key. Best of both worlds!",
            },
        }

    def _get_common_mistakes(self) -> list:
        """Common key/constraint mistakes."""
        return [
            {
                "mistake": "Using business data as primary key",
                "problem": "What if email changes? All FKs break.",
                "example": "PRIMARY KEY (email)",
                "fix": "Use surrogate key, make email UNIQUE",
            },
            {
                "mistake": "Forgetting the junction table",
                "problem": "Trying to store many-to-many in a single column",
                "example": "products VARCHAR(255) -- '1,2,3' (comma-separated IDs)",
                "fix": "Create proper junction table with FKs",
            },
            {
                "mistake": "FK on the wrong side",
                "problem": "Putting FK on the 'one' side of 1:N",
                "example": "department.employee_id -- Wrong! Dept can't store multiple employees",
                "fix": "FK goes on the 'many' side: employee.department_id",
            },
            {
                "mistake": "Missing NOT NULL on FK",
                "problem": "Allows orphaned relationships",
                "example": "order.customer_id INT (nullable) -- Orders without customers!",
                "fix": "order.customer_id INT NOT NULL",
            },
            {
                "mistake": "No index on foreign key",
                "problem": "Slow JOINs and constraint checks",
                "example": "FK without index",
                "fix": "MySQL auto-creates FK index. Others: CREATE INDEX manually",
            },
            {
                "mistake": "Overusing CASCADE DELETE",
                "problem": "Accidental mass deletion",
                "example": "Delete one customer → all orders → all order_items gone!",
                "fix": "Use RESTRICT or SET NULL; delete explicitly",
            },
        ]

    def _get_best_practices(self) -> list:
        """Best practices for keys and constraints."""
        return [
            {
                "practice": "Every table should have a primary key",
                "why": "Uniquely identifies rows, enables proper indexing",
                "tip": "Prefer INT AUTO_INCREMENT for simplicity",
            },
            {
                "practice": "Define all foreign keys explicitly",
                "why": "Database enforces relationships, prevents orphans",
                "tip": "Even if app logic 'should' prevent bad data",
            },
            {
                "practice": "Use UNIQUE constraints on business keys",
                "why": "Prevents duplicate emails, usernames, etc.",
                "tip": "Can have multiple UNIQUE constraints per table",
            },
            {
                "practice": "Name constraints meaningfully",
                "why": "Error messages become readable",
                "tip": "CONSTRAINT fk_employee_department FOREIGN KEY (...)",
            },
            {
                "practice": "Consider ON DELETE behavior carefully",
                "why": "CASCADE can cause unexpected mass deletions",
                "tip": "Default to RESTRICT, use CASCADE only when appropriate",
            },
            {
                "practice": "Document your relationships",
                "why": "Future developers (including you) will thank you",
                "tip": "ER diagrams, inline comments, or schema docs",
            },
        ]
