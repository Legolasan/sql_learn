# SQL Learn

An interactive visual learning platform for mastering MySQL concepts. Learn SQL through hands-on experimentation with real-time query visualization, step-by-step explanations, and animated demonstrations.

## Features

- **Interactive Query Executor** - Write and execute SQL queries with instant visual feedback
- **18 Learning Concepts** - From beginner basics to advanced internals
- **Visual Animations** - See how B-Trees work, watch InnoDB crash recovery, animate window functions
- **Step-by-Step Explanations** - Understand query execution order, index lookups, and more
- **No Database Required** - Built-in in-memory dataset for safe experimentation

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Legolasan/sql_learn.git
cd sql_learn

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python run.py
```

Open http://localhost:5000 in your browser.

## Concepts Covered

### Beginner
| Concept | Description |
|---------|-------------|
| SQL Basics | SELECT, FROM, WHERE fundamentals |
| Data Types & NULLs | Understanding MySQL data types and NULL handling |
| B-Tree Indexes | Visual B-Tree structure and search operations |
| Execution Order | How MySQL processes queries (FROM → WHERE → SELECT) |
| Joins | Visual JOIN operations with Venn diagrams |

### Intermediate
| Concept | Description |
|---------|-------------|
| Join Types | INNER, LEFT, RIGHT, CROSS, SELF joins with patterns |
| Cardinality & Keys | Primary keys, foreign keys, and relationships |
| EXPLAIN Plans | Reading and understanding query execution plans |
| WHERE vs HAVING | When to filter with WHERE vs HAVING |
| Index Types | B-Tree, Hash, Full-text, and composite indexes |
| Normalization | 1NF, 2NF, 3NF, BCNF with constraints and generated columns |
| Data Layout | Clustered indexes, secondary indexes, covering indexes |

### Advanced
| Concept | Description |
|---------|-------------|
| Subqueries | Correlated subqueries, EXISTS, IN patterns |
| Query Optimization | Index strategies and query tuning |
| Transactions | ACID properties, isolation levels, locking |
| CTEs | Common Table Expressions and recursive queries |
| Window Functions | ROW_NUMBER, RANK, LEAD/LAG, running totals |
| InnoDB Internals | Buffer pool, redo/undo logs, crash recovery |

## Project Structure

```
sql_learn/
├── app/
│   ├── concepts/           # Learning concept modules
│   │   ├── base.py         # BaseConcept class
│   │   ├── btree_concept.py
│   │   ├── window_functions_concept.py
│   │   ├── innodb_concept.py
│   │   └── ...
│   ├── engine/             # Query processing
│   │   ├── query_executor.py
│   │   ├── query_parser.py
│   │   ├── dataset.py      # In-memory sample data
│   │   └── btree.py        # B-Tree visualization
│   ├── routes/             # Flask routes
│   ├── templates/          # Jinja2 templates
│   │   ├── concepts/       # Concept-specific templates
│   │   └── components/     # Reusable components
│   └── __init__.py         # Flask app factory
├── requirements.txt
├── run.py
└── README.md
```

## Sample Dataset

The app includes a pre-built dataset with 6 related tables:

| Table | Description |
|-------|-------------|
| `employees` | 20 employees with salary, department, manager |
| `departments` | 5 departments with budget info |
| `projects` | 8 projects with status and deadlines |
| `employee_projects` | Many-to-many assignments |
| `salaries` | Historical salary records |
| `orders` | Sample order data |

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTMX + Alpine.js + Tailwind CSS
- **Templates**: Jinja2
- **Query Engine**: Custom SQL parser (supports SELECT, JOIN, WHERE, GROUP BY, ORDER BY, LIMIT)

## Adding New Concepts

1. Create a new concept file in `app/concepts/`:

```python
from app.concepts.base import BaseConcept, Step

class MyConcept(BaseConcept):
    name = "my-concept"
    display_name = "My Concept"
    description = "Learn about..."
    difficulty = "intermediate"  # beginner, intermediate, advanced

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        return {"key": "value"}

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        return [
            Step(title="Step 1", description="...", highlight={'section': 'intro'})
        ]

    def get_sample_queries(self) -> list[str]:
        return ["SELECT * FROM employees"]
```

2. Create a template in `app/templates/concepts/my-concept.html`

3. Register in `app/concepts/__init__.py`:

```python
from app.concepts.my_concept import MyConcept
register_concept(MyConcept())
```

## Screenshots

*Coming soon*

## Contributing

Contributions are welcome! Feel free to:

- Add new learning concepts
- Improve visualizations
- Fix bugs
- Enhance the query executor

## License

MIT License - feel free to use this for learning and teaching!

---

Built with Claude Code
