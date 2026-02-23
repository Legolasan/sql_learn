# Project Vision

## Mission

**SQL Learn exists to help people understand MySQL through visual, interactive learning.**

Every feature, every line of code should answer the question: *"Does this help someone learn?"*

---

## Core Principles

### 1. Education First
Every feature must teach something. We're not building a database client - we're building a learning tool.

### 2. Visual Understanding
Show, don't just tell. Animations, diagrams, and step-by-step visualizations are our primary teaching method.

### 3. Progressive Difficulty
Start simple, build complexity. Beginners should feel welcome; advanced users should find depth.

### 4. Safe Experimentation
Users should be able to try queries without fear. The built-in dataset means you can't break anything.

---

## What SQL Learn IS

- A visual MySQL learning platform
- A place to understand concepts through interactive demos
- Beginner-friendly with paths to advanced topics
- Open to real database connections (for educational purposes)
- A tool that makes SQL concepts click

## What SQL Learn is NOT

- A production database management tool
- A MySQL IDE for day-to-day work
- A data analytics or BI platform
- A replacement for official MySQL documentation

---

## Decision Framework

When evaluating new features or contributions, ask:

1. **Does it teach?** If a feature doesn't help someone learn MySQL, it doesn't belong here.

2. **Is it visual?** Can we show this concept with an animation, diagram, or interactive demo?

3. **Does it fit the learning path?** Does it connect to existing concepts or open doors to new ones?

4. **Is it accessible to learners?** Would a beginner understand why this exists?

If the answer to question 1 is "no," the feature is out of scope - regardless of how useful it might be in other contexts.

---

## Examples

### In Scope
- New concept explaining query optimization with EXPLAIN visualization
- Adding real MySQL connection to test queries on user's database (educational)
- Interactive quiz system to test understanding
- Comparison view: "Your query vs. optimized query"

### Out of Scope
- Database backup/restore functionality
- User authentication system for multi-tenant use
- Export data to CSV/Excel
- Connection pooling for production workloads
- Schema migration tools

---

## Maintainer Commitment

As maintainers, we commit to:
- Evaluating all contributions against this vision
- Providing clear feedback when something is out of scope
- Being open to expanding scope if it serves education
- Keeping the project focused and learner-friendly
