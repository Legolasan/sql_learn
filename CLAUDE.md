# MySQL Learning Visualizer

An interactive Flask application for learning MySQL concepts through visual animations and hands-on query execution.

## Repository & Deployment

- **GitHub:** https://github.com/Legolasan/sql_learn
- **Live Site:** https://legolasan.in/learn/mysql/
- **Portfolio Home:** https://legolasan.in/

When making changes, commit and push to the GitHub repo.

---

## Quick Start

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python run.py
```

App runs at `http://localhost:5000`

---

## Project Architecture

```
mysql_learn/
├── run.py                    # Entry point
├── requirements.txt          # Dependencies (flask, python-dotenv)
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── routes/
│   │   ├── main.py          # Home page routes
│   │   └── concepts.py      # Concept view & query execution routes
│   ├── concepts/
│   │   ├── base.py          # BaseConcept abstract class & Step dataclass
│   │   ├── __init__.py      # Concept registry (register all concepts here)
│   │   └── *_concept.py     # Individual concept implementations
│   ├── engine/
│   │   ├── dataset.py       # Static dataset (Employee, Department, etc.)
│   │   ├── query_parser.py  # SQL parser (extracts tables, columns, conditions)
│   │   ├── query_executor.py # Executes queries against static dataset
│   │   ├── errors.py        # QueryError exception class
│   │   ├── btree.py         # B-Tree implementation for visualization
│   │   ├── explain.py       # EXPLAIN plan generator
│   │   └── execution_order.py # SQL execution order logic
│   └── templates/
│       ├── base.html        # Base layout (Tailwind CSS, HTMX, Alpine.js)
│       ├── index.html       # Home page with concept cards
│       ├── concept_view.html # Concept page wrapper
│       ├── components/
│       │   ├── error_display.html  # Error message component
│       │   └── results_table.html  # Query results table
│       └── concepts/
│           └── *.html       # Individual concept templates
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask 3.x |
| Frontend | Tailwind CSS (CDN), HTMX, Alpine.js |
| Data | Static Python dataclasses (no real database) |
| Templates | Jinja2 |

---

## Database Schema (Static Dataset)

The app uses an in-memory static dataset with 6 tables:

### Tables

```
employees (10 rows)
├── id: INT (PK)
├── name: VARCHAR
├── department_id: INT (FK -> departments.id)
├── manager_id: INT (FK -> employees.id, nullable) -- Self-referential
├── salary: DECIMAL
├── hire_date: DATE
├── email: VARCHAR (nullable) -- For NULL demos
└── phone: VARCHAR (nullable)

departments (4 rows)
├── id: INT (PK)
├── name: VARCHAR
├── budget: DECIMAL
└── location: VARCHAR (nullable)

customers (8 rows)
├── id: INT (PK)
├── name: VARCHAR
├── email: VARCHAR (UNIQUE)
├── city: VARCHAR (nullable)
├── country: VARCHAR
├── credit_limit: DECIMAL (nullable)
└── created_at: DATETIME

products (10 rows)
├── id: INT (PK)
├── name: VARCHAR
├── category: VARCHAR
├── price: DECIMAL
├── stock_quantity: INT
├── weight: DECIMAL (nullable) -- NULL for digital products
└── is_active: BOOLEAN

orders (12 rows)
├── id: INT (PK)
├── customer_id: INT (FK -> customers.id)
├── employee_id: INT (FK -> employees.id)
├── order_date: DATE
├── shipped_date: DATE (nullable)
├── status: VARCHAR
└── notes: VARCHAR (nullable)

order_items (25 rows) -- Junction table for M:N
├── id: INT (PK)
├── order_id: INT (FK -> orders.id)
├── product_id: INT (FK -> products.id)
├── quantity: INT
├── unit_price: DECIMAL
└── discount: DECIMAL (nullable)
```

### Relationships

- `departments` 1:N `employees` (one-to-many)
- `employees` 1:N `employees` (self-referential: manager)
- `customers` 1:N `orders` (one-to-many)
- `employees` 1:N `orders` (sales rep)
- `orders` M:N `products` via `order_items` (many-to-many)

### NULL Values (Strategic)

The dataset includes NULL values for demonstrating NULL traps:
- `employees.email`, `employees.phone` - some NULL
- `employees.manager_id` - NULL for CEO/top managers
- `departments.location` - some NULL
- `orders.shipped_date` - NULL for pending orders
- `products.weight` - NULL for digital products
- `order_items.discount` - NULL means no discount

---

## Concepts System

### BaseConcept Class

All concepts extend `BaseConcept` from `app/concepts/base.py`:

```python
class BaseConcept(ABC):
    name: str           # URL slug (e.g., "btree")
    display_name: str   # UI name (e.g., "B-Tree Indexing")
    description: str    # Short description
    difficulty: str     # "beginner" | "intermediate" | "advanced"

    @abstractmethod
    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        """Return data for the template."""
        pass

    @abstractmethod
    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        """Return animation steps."""
        pass

    def get_sample_queries(self) -> list[str]:
        """Optional: sample queries for the concept."""
        return []
```

### Step Dataclass

```python
@dataclass
class Step:
    title: str
    description: str
    highlight: dict[str, Any]  # Data to highlight in visualization
    data_snapshot: Any = None  # Optional state at this step
```

### Registered Concepts (15 total)

| Concept | Slug | Difficulty |
|---------|------|------------|
| SQL Basics | `sql-basics` | beginner |
| Data Types & NULLs | `data-types-nulls` | beginner |
| B-Tree Indexing | `btree` | beginner |
| EXPLAIN Plans | `explain` | intermediate |
| Execution Order | `exec-order` | intermediate |
| Join Types | `join-types` | intermediate |
| Joins (Original) | `joins` | intermediate |
| WHERE vs HAVING | `where-having` | intermediate |
| Index Types | `index-types` | intermediate |
| Cardinality & Keys | `cardinality-keys` | intermediate |
| Subqueries | `subqueries` | intermediate |
| CTEs | `cte` | intermediate |
| Query Optimization | `optimization` | advanced |
| Transactions & Locking | `transactions` | advanced |
| Normalization | `normalization` | advanced |

---

## Adding a New Concept

### 1. Create the concept file

```python
# app/concepts/my_concept.py
from typing import Any
from app.concepts.base import BaseConcept, Step

class MyNewConcept(BaseConcept):
    name = "my-concept"  # URL: /concept/my-concept
    display_name = "My New Concept"
    description = "Learn about something cool"
    difficulty = "beginner"  # or "intermediate" or "advanced"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        return {
            'some_data': self._calculate_something(query),
            'more_data': [...],
        }

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        return [
            Step(
                title="Step 1",
                description="First thing to learn",
                highlight={'section': 'intro'}
            ),
            Step(
                title="Step 2",
                description="Second thing",
                highlight={'section': 'main'}
            ),
        ]

    def get_sample_queries(self) -> list[str]:
        return [
            "SELECT * FROM employees",
            "SELECT name, salary FROM employees WHERE salary > 50000",
        ]

    def _calculate_something(self, query: str) -> dict:
        # Helper methods
        return {}
```

### 2. Create the template

```html
<!-- app/templates/concepts/my-concept.html -->
<div class="space-y-6">
    <!-- Hero Section -->
    <div class="bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg p-6">
        <h3 class="text-2xl font-bold mb-2">My Concept Title</h3>
        <p class="text-blue-100">{{ viz_data.some_data }}</p>
    </div>

    <!-- Content Sections -->
    <div class="bg-white border rounded-lg p-4">
        <!-- Your visualization content -->
    </div>

    <!-- Step Controls (copy from existing concept) -->
    <div class="bg-gray-50 rounded-lg p-4">
        <!-- Navigation buttons -->
    </div>
</div>

{# Include error and results components #}
{% include 'components/error_display.html' %}
{% include 'components/results_table.html' %}
```

### 3. Register in `__init__.py`

```python
# app/concepts/__init__.py
from app.concepts.my_concept import MyNewConcept

# Add to imports, then register:
register_concept(MyNewConcept())
```

---

## Query Executor

The `query_executor.py` runs SQL queries against the static dataset:

### Supported Features

| Feature | Supported |
|---------|-----------|
| SELECT columns, * | Yes |
| SELECT with aliases | Yes |
| WHERE =, >, <, >=, <=, != | Yes |
| WHERE LIKE | Yes |
| WHERE IN | Yes |
| WHERE AND/OR | Yes |
| WHERE IS NULL / IS NOT NULL | Yes |
| ORDER BY ASC/DESC | Yes |
| LIMIT, OFFSET | Yes |
| GROUP BY | Yes |
| HAVING | Yes |
| COUNT, SUM, AVG, MAX, MIN | Yes |
| INNER/LEFT/RIGHT/CROSS JOIN | Yes |
| CTEs (WITH clause) | Yes |
| Recursive CTEs | Yes |
| Subqueries | Partial |

### Available Tables

```python
AVAILABLE_TABLES = ['employees', 'departments', 'customers', 'products', 'orders', 'order_items']
```

---

## Template Patterns

### Using Alpine.js for Interactivity

```html
<div x-data="{ showAnswer: false, selectedOption: null }">
    <button @click="showAnswer = !showAnswer">
        <span x-text="showAnswer ? 'Hide' : 'Show'"></span> Answer
    </button>
    <div x-show="showAnswer" x-transition>
        Answer content here
    </div>
</div>
```

### Using HTMX for Dynamic Loading

```html
<button hx-get="/concept/my-concept/step/{{ current_step + 1 }}"
        hx-target="#visualization-area"
        hx-swap="innerHTML">
    Next Step
</button>
```

### Tailwind CSS Classes (Common)

```
Containers: bg-white border rounded-lg p-4
Headers: bg-gray-50 px-4 py-3 border-b
Cards: border rounded-lg overflow-hidden hover:shadow-md
Buttons: px-3 py-1 bg-gray-200 rounded hover:bg-gray-300
Gradients: bg-gradient-to-r from-blue-600 to-indigo-600
```

---

## Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Home page with concept cards |
| `/concept/<name>` | GET | Concept view page |
| `/concept/<name>/query` | POST | Execute query and return visualization |
| `/concept/<name>/step/<n>` | GET | Get specific step (HTMX) |

---

## Error Handling

```python
# app/engine/errors.py
class QueryError(Exception):
    def __init__(self, message: str, suggestion: str = None,
                 line: int = None, column: int = None):
        self.message = message
        self.suggestion = suggestion  # "Did you mean...?"
        self.line = line
        self.column = column
```

Errors are caught in routes and passed to templates:

```python
try:
    result = executor.execute(query)
except QueryError as e:
    error = {'message': e.message, 'suggestion': e.suggestion}
```

---

## Development Tips

### Adding Data to Dataset

Edit `app/engine/dataset.py`:
1. Add/modify dataclass if needed
2. Add data to the appropriate list in `StaticDataset`
3. Update `TABLE_COLUMNS` in `query_executor.py` if columns changed

### Testing Queries

The query executor has basic SQL support. Test complex queries manually:

```python
from app.engine.dataset import StaticDataset
from app.engine.query_executor import QueryExecutor

dataset = StaticDataset()
executor = QueryExecutor(dataset)
result = executor.execute("SELECT * FROM employees WHERE salary > 50000")
print(result.rows)
```

### Common Issues

1. **Import Error on startup**: Check class names match between concept file and `__init__.py`
2. **Template not found**: Ensure template name matches `concept.name` (e.g., `my-concept.html`)
3. **Step missing highlight**: All `Step` objects require a `highlight` dict parameter
4. **Query fails**: Check `AVAILABLE_TABLES` and `TABLE_COLUMNS` in query_executor.py

---

## Deployment

### Local Development

```bash
python run.py
# or
flask run --debug
```

### Production (Example with Gunicorn)

```bash
pip install gunicorn
gunicorn "app:create_app()" -b 0.0.0.0:8000
```

### Docker (Example)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt gunicorn
COPY . .
EXPOSE 8000
CMD ["gunicorn", "app:create_app()", "-b", "0.0.0.0:8000"]
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| SECRET_KEY | dev-secret-key | Flask secret key (change in prod!) |
| FLASK_DEBUG | 0 | Enable debug mode |

---

## Future Enhancements

- [ ] Real database connection option
- [ ] User progress tracking
- [ ] Quiz/assessment mode
- [ ] More advanced query features (window functions, etc.)
- [ ] Export visualizations as images
