# Contributing to SQL Learn

Thanks for your interest in contributing! This project helps people learn MySQL through visual, interactive education.

Before contributing, please read our [Vision](VISION.md) to understand what this project is (and isn't).

---

## Quick Start

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/sql_learn.git
cd sql_learn

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run
python run.py
```

---

## What We Welcome

### New Learning Concepts
The heart of this project! Each concept should:
- Teach a specific MySQL topic
- Include visual/interactive elements
- Have clear step-by-step explanations
- Fit into beginner/intermediate/advanced difficulty

See [Adding New Concepts](#adding-new-concepts) below.

### Visual Improvements
- Better animations
- Clearer diagrams
- Improved step-through visualizations
- Mobile responsiveness

### Educational Features
- Quiz systems
- Progress tracking
- Real database connections (for learning purposes)
- Query comparison tools

### Bug Fixes & Documentation
Always welcome!

### Accessibility
- Screen reader improvements
- Keyboard navigation
- Color contrast fixes

### Translations
Help make SQL learning accessible in more languages.

---

## What's Out of Scope

This is an **educational tool**, not a production database client. We don't accept:

- Production/enterprise features (connection pooling, auth systems, role management)
- Non-educational utilities (data export, backup tools, schema migration)
- Features that don't teach MySQL concepts
- Integrations with BI/analytics tools

If you're unsure, open an issue to discuss before building!

---

## Adding New Concepts

### 1. Create the Concept Class

```python
# app/concepts/my_concept.py
from app.concepts.base import BaseConcept, Step

class MyConcept(BaseConcept):
    name = "my-concept"           # URL slug
    display_name = "My Concept"   # Display title
    description = "Learn about..."
    difficulty = "intermediate"   # beginner, intermediate, advanced

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        return {
            "demo_data": [...],
            "explanation": "..."
        }

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        return [
            Step(
                title="Step 1",
                description="What happens first",
                highlight={'section': 'intro'}
            ),
            # More steps...
        ]

    def get_sample_queries(self) -> list[str]:
        return ["SELECT * FROM employees"]
```

### 2. Create the Template

```html
<!-- app/templates/concepts/my-concept.html -->
<div class="space-y-6" x-data="myConceptDemo()">
    <!-- Your visualization here -->
    <!-- Use Alpine.js for interactivity -->
    <!-- Use Tailwind for styling -->
</div>

<script>
function myConceptDemo() {
    return {
        // Alpine.js state and methods
    }
}
</script>

{% include 'components/error_display.html' %}
{% include 'components/results_table.html' %}
```

### 3. Register the Concept

```python
# app/concepts/__init__.py
from app.concepts.my_concept import MyConcept
register_concept(MyConcept())
```

---

## Code Style

- Python: Follow PEP 8
- HTML/JS: Use existing patterns in templates
- Keep it simple - this is for learners to read too!

---

## Pull Request Process

1. **Fork** the repo and create your branch from `main`
2. **Test** your changes locally
3. **Fill out** the PR template completely
4. **Link** any related issues
5. **Wait** for review - we'll provide feedback!

### PR Checklist

- [ ] Does this teach something about MySQL?
- [ ] Is there a visual/interactive component?
- [ ] Have I tested on mobile?
- [ ] Does it follow existing code patterns?

---

## Questions?

Open an issue! We're happy to discuss ideas before you start coding.

---

## Code of Conduct

Please read our [Code of Conduct](CODE_OF_CONDUCT.md). We're building a welcoming community for learners.
