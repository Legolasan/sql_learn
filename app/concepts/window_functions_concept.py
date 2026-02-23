"""
Window Functions Concept - Visual education for ROW_NUMBER, RANK, DENSE_RANK,
LEAD/LAG, running totals, and window frames.

Uses pre-computed demo results since the query executor doesn't support window functions.
"""

from typing import Any

from app.concepts.base import BaseConcept, Step


class WindowFunctionsConcept(BaseConcept):
    """Comprehensive window functions education with visual demonstrations."""

    name = "window-functions"
    display_name = "Window Functions"
    description = "Master ROW_NUMBER, RANK, LEAD/LAG, running totals, and window frames with animated visualizations"
    difficulty = "advanced"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        """Generate visualization data for window functions."""
        return {
            "overview": self._get_overview(),
            "ranking_functions": self._get_ranking_functions(),
            "offset_functions": self._get_offset_functions(),
            "aggregate_windows": self._get_aggregate_windows(),
            "window_frames": self._get_window_frames(),
            "top_n_per_group": self._get_top_n_demo(),
            "quizzes": self._get_quizzes(),
            "syntax_reference": self._get_syntax_reference(),
            "common_mistakes": self._get_common_mistakes(),
            "performance_tips": self._get_performance_tips(),
        }

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        return [
            Step(
                title="What Are Window Functions?",
                description="Window functions perform calculations across a set of rows related to the current row, without collapsing them like GROUP BY.",
                highlight={'section': 'overview'}
            ),
            Step(
                title="ROW_NUMBER, RANK, DENSE_RANK",
                description="Ranking functions assign numbers to rows. ROW_NUMBER is always unique, RANK has gaps, DENSE_RANK has no gaps.",
                highlight={'section': 'ranking'}
            ),
            Step(
                title="LEAD and LAG",
                description="Access data from rows ahead (LEAD) or behind (LAG) the current row. Perfect for comparing consecutive values.",
                highlight={'section': 'offset'}
            ),
            Step(
                title="Running Totals with SUM() OVER",
                description="Aggregate functions with OVER create running calculations. SUM() OVER gives cumulative totals.",
                highlight={'section': 'aggregates'}
            ),
            Step(
                title="Window Frames",
                description="ROWS BETWEEN and RANGE BETWEEN define exactly which rows are included in the window calculation.",
                highlight={'section': 'frames'}
            ),
            Step(
                title="Top N Per Group Pattern",
                description="A powerful pattern using ROW_NUMBER to get top records within each group - much better than correlated subqueries!",
                highlight={'section': 'top_n'}
            ),
        ]

    def get_sample_queries(self) -> list[str]:
        """Sample queries - note these won't actually execute but show syntax."""
        return [
            "SELECT name, salary, ROW_NUMBER() OVER (ORDER BY salary DESC) as rank FROM employees",
            "SELECT name, department_id, salary, RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_rank FROM employees",
            "SELECT name, salary, SUM(salary) OVER (ORDER BY hire_date) as running_total FROM employees",
            "SELECT name, salary, LAG(salary, 1) OVER (ORDER BY hire_date) as prev_salary FROM employees",
            "SELECT * FROM (SELECT name, department_id, salary, ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary DESC) as rn FROM employees) t WHERE rn <= 3",
        ]

    def _get_overview(self) -> dict:
        return {
            "title": "Window Functions: Calculations Across Rows",
            "key_concept": "Unlike GROUP BY which collapses rows, window functions keep all rows and add computed values.",
            "anatomy": {
                "function": "ROW_NUMBER(), RANK(), SUM(), etc.",
                "over_clause": "OVER (...) - defines the window",
                "partition_by": "PARTITION BY col - like GROUP BY but keeps rows",
                "order_by": "ORDER BY col - ordering within the window",
                "frame": "ROWS BETWEEN ... - which rows to include",
            },
            "syntax": "function() OVER (PARTITION BY col ORDER BY col ROWS BETWEEN ...)",
            "comparison": {
                "group_by": {
                    "query": "SELECT dept, AVG(salary) FROM employees GROUP BY dept",
                    "result_rows": "One row per department",
                    "use_case": "Summarize/aggregate data",
                },
                "window": {
                    "query": "SELECT name, dept, AVG(salary) OVER (PARTITION BY dept) FROM employees",
                    "result_rows": "All employee rows, each with dept average",
                    "use_case": "Add context to each row",
                },
            },
        }

    def _get_ranking_functions(self) -> dict:
        """Pre-computed ranking function demonstrations."""
        # Sample data for demos
        source_data = [
            {"name": "Alice", "dept": "Engineering", "salary": 90000},
            {"name": "Bob", "dept": "Engineering", "salary": 85000},
            {"name": "Carol", "dept": "Engineering", "salary": 85000},
            {"name": "Dave", "dept": "Engineering", "salary": 75000},
            {"name": "Eve", "dept": "Sales", "salary": 70000},
            {"name": "Frank", "dept": "Sales", "salary": 65000},
        ]

        return {
            "title": "Ranking Functions",
            "source_data": source_data,
            "functions": [
                {
                    "name": "ROW_NUMBER()",
                    "description": "Assigns unique sequential numbers. No ties, no gaps.",
                    "syntax": "ROW_NUMBER() OVER (ORDER BY salary DESC)",
                    "result": [
                        {"name": "Alice", "salary": 90000, "row_num": 1},
                        {"name": "Bob", "salary": 85000, "row_num": 2},
                        {"name": "Carol", "salary": 85000, "row_num": 3},
                        {"name": "Dave", "salary": 75000, "row_num": 4},
                        {"name": "Eve", "salary": 70000, "row_num": 5},
                        {"name": "Frank", "salary": 65000, "row_num": 6},
                    ],
                    "note": "Bob and Carol have same salary but different row numbers (arbitrary order for ties)",
                },
                {
                    "name": "RANK()",
                    "description": "Same values get same rank. Next rank skips (gaps).",
                    "syntax": "RANK() OVER (ORDER BY salary DESC)",
                    "result": [
                        {"name": "Alice", "salary": 90000, "rank": 1},
                        {"name": "Bob", "salary": 85000, "rank": 2},
                        {"name": "Carol", "salary": 85000, "rank": 2},
                        {"name": "Dave", "salary": 75000, "rank": 4},  # Gap! Skipped 3
                        {"name": "Eve", "salary": 70000, "rank": 5},
                        {"name": "Frank", "salary": 65000, "rank": 6},
                    ],
                    "note": "Bob and Carol both rank 2, Dave is rank 4 (rank 3 skipped)",
                },
                {
                    "name": "DENSE_RANK()",
                    "description": "Same values get same rank. No gaps in numbering.",
                    "syntax": "DENSE_RANK() OVER (ORDER BY salary DESC)",
                    "result": [
                        {"name": "Alice", "salary": 90000, "dense_rank": 1},
                        {"name": "Bob", "salary": 85000, "dense_rank": 2},
                        {"name": "Carol", "salary": 85000, "dense_rank": 2},
                        {"name": "Dave", "salary": 75000, "dense_rank": 3},  # No gap
                        {"name": "Eve", "salary": 70000, "dense_rank": 4},
                        {"name": "Frank", "salary": 65000, "dense_rank": 5},
                    ],
                    "note": "Bob and Carol both rank 2, Dave is rank 3 (no gap)",
                },
            ],
            "with_partition": {
                "title": "With PARTITION BY (ranking within groups)",
                "syntax": "ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)",
                "result": [
                    {"name": "Alice", "dept": "Engineering", "salary": 90000, "dept_rank": 1},
                    {"name": "Bob", "dept": "Engineering", "salary": 85000, "dept_rank": 2},
                    {"name": "Carol", "dept": "Engineering", "salary": 85000, "dept_rank": 3},
                    {"name": "Dave", "dept": "Engineering", "salary": 75000, "dept_rank": 4},
                    {"name": "Eve", "dept": "Sales", "salary": 70000, "dept_rank": 1},  # Resets!
                    {"name": "Frank", "dept": "Sales", "salary": 65000, "dept_rank": 2},
                ],
                "note": "Numbering restarts for each department",
            },
        }

    def _get_offset_functions(self) -> dict:
        """LEAD and LAG demonstrations."""
        source_data = [
            {"month": "Jan", "sales": 100},
            {"month": "Feb", "sales": 120},
            {"month": "Mar", "sales": 90},
            {"month": "Apr", "sales": 150},
            {"month": "May", "sales": 130},
        ]

        return {
            "title": "Offset Functions: LEAD and LAG",
            "source_data": source_data,
            "functions": [
                {
                    "name": "LAG()",
                    "description": "Access value from previous row(s)",
                    "syntax": "LAG(sales, 1) OVER (ORDER BY month)",
                    "result": [
                        {"month": "Jan", "sales": 100, "prev_sales": None, "note": "No previous row"},
                        {"month": "Feb", "sales": 120, "prev_sales": 100, "note": ""},
                        {"month": "Mar", "sales": 90, "prev_sales": 120, "note": ""},
                        {"month": "Apr", "sales": 150, "prev_sales": 90, "note": ""},
                        {"month": "May", "sales": 130, "prev_sales": 150, "note": ""},
                    ],
                    "use_cases": [
                        "Month-over-month comparison",
                        "Calculate change from previous period",
                        "Detect trend changes",
                    ],
                },
                {
                    "name": "LEAD()",
                    "description": "Access value from next row(s)",
                    "syntax": "LEAD(sales, 1) OVER (ORDER BY month)",
                    "result": [
                        {"month": "Jan", "sales": 100, "next_sales": 120, "note": ""},
                        {"month": "Feb", "sales": 120, "next_sales": 90, "note": ""},
                        {"month": "Mar", "sales": 90, "next_sales": 150, "note": ""},
                        {"month": "Apr", "sales": 150, "next_sales": 130, "note": ""},
                        {"month": "May", "sales": 130, "next_sales": None, "note": "No next row"},
                    ],
                    "use_cases": [
                        "Look-ahead calculations",
                        "Compare with future periods",
                        "Forecast validation",
                    ],
                },
            ],
            "with_offset": {
                "title": "LAG with offset > 1",
                "syntax": "LAG(sales, 2) OVER (ORDER BY month)",
                "explanation": "Look back 2 rows instead of 1",
            },
            "with_default": {
                "title": "LAG with default value",
                "syntax": "LAG(sales, 1, 0) OVER (ORDER BY month)",
                "explanation": "Use 0 instead of NULL when no previous row exists",
            },
            "change_calculation": {
                "title": "Practical: Calculate Month-over-Month Change",
                "query": """SELECT month, sales,
       LAG(sales) OVER (ORDER BY month) as prev_sales,
       sales - LAG(sales) OVER (ORDER BY month) as change,
       ROUND(100.0 * (sales - LAG(sales) OVER (ORDER BY month)) / LAG(sales) OVER (ORDER BY month), 1) as pct_change
FROM monthly_sales""",
                "result": [
                    {"month": "Jan", "sales": 100, "prev_sales": None, "change": None, "pct_change": None},
                    {"month": "Feb", "sales": 120, "prev_sales": 100, "change": 20, "pct_change": 20.0},
                    {"month": "Mar", "sales": 90, "prev_sales": 120, "change": -30, "pct_change": -25.0},
                    {"month": "Apr", "sales": 150, "prev_sales": 90, "change": 60, "pct_change": 66.7},
                    {"month": "May", "sales": 130, "prev_sales": 150, "change": -20, "pct_change": -13.3},
                ],
            },
        }

    def _get_aggregate_windows(self) -> dict:
        """Running totals and aggregate window functions."""
        source_data = [
            {"day": "Mon", "sales": 100},
            {"day": "Tue", "sales": 150},
            {"day": "Wed", "sales": 80},
            {"day": "Thu", "sales": 200},
            {"day": "Fri", "sales": 175},
        ]

        return {
            "title": "Aggregate Window Functions",
            "source_data": source_data,
            "running_total": {
                "name": "Running Total (SUM OVER)",
                "syntax": "SUM(sales) OVER (ORDER BY day)",
                "result": [
                    {"day": "Mon", "sales": 100, "running_total": 100},
                    {"day": "Tue", "sales": 150, "running_total": 250},
                    {"day": "Wed", "sales": 80, "running_total": 330},
                    {"day": "Thu", "sales": 200, "running_total": 530},
                    {"day": "Fri", "sales": 175, "running_total": 705},
                ],
                "animation_steps": [
                    {"row": 0, "calculation": "100", "total": 100},
                    {"row": 1, "calculation": "100 + 150", "total": 250},
                    {"row": 2, "calculation": "250 + 80", "total": 330},
                    {"row": 3, "calculation": "330 + 200", "total": 530},
                    {"row": 4, "calculation": "530 + 175", "total": 705},
                ],
            },
            "running_avg": {
                "name": "Running Average (AVG OVER)",
                "syntax": "AVG(sales) OVER (ORDER BY day)",
                "result": [
                    {"day": "Mon", "sales": 100, "running_avg": 100.0},
                    {"day": "Tue", "sales": 150, "running_avg": 125.0},
                    {"day": "Wed", "sales": 80, "running_avg": 110.0},
                    {"day": "Thu", "sales": 200, "running_avg": 132.5},
                    {"day": "Fri", "sales": 175, "running_avg": 141.0},
                ],
            },
            "partition_aggregate": {
                "name": "Aggregate per Partition",
                "description": "Calculate totals within groups without collapsing rows",
                "syntax": "SUM(sales) OVER (PARTITION BY category)",
                "source": [
                    {"product": "A", "category": "Electronics", "sales": 100},
                    {"product": "B", "category": "Electronics", "sales": 150},
                    {"product": "C", "category": "Clothing", "sales": 80},
                    {"product": "D", "category": "Clothing", "sales": 120},
                ],
                "result": [
                    {"product": "A", "category": "Electronics", "sales": 100, "category_total": 250},
                    {"product": "B", "category": "Electronics", "sales": 150, "category_total": 250},
                    {"product": "C", "category": "Clothing", "sales": 80, "category_total": 200},
                    {"product": "D", "category": "Clothing", "sales": 120, "category_total": 200},
                ],
                "note": "Each row shows its category's total - useful for % of category calculations",
            },
            "percent_of_total": {
                "title": "Practical: Percent of Total",
                "query": """SELECT product, sales,
       SUM(sales) OVER () as total_sales,
       ROUND(100.0 * sales / SUM(sales) OVER (), 1) as pct_of_total
FROM products""",
                "explanation": "OVER () with no arguments = entire result set as window",
            },
        }

    def _get_window_frames(self) -> dict:
        """Window frame specifications."""
        source_data = [
            {"day": 1, "temp": 68},
            {"day": 2, "temp": 72},
            {"day": 3, "temp": 75},
            {"day": 4, "temp": 71},
            {"day": 5, "temp": 69},
            {"day": 6, "temp": 73},
            {"day": 7, "temp": 76},
        ]

        return {
            "title": "Window Frames: ROWS BETWEEN",
            "source_data": source_data,
            "key_concept": "Frame defines exactly which rows are included in each calculation",
            "frame_types": [
                {
                    "name": "UNBOUNDED PRECEDING to CURRENT ROW",
                    "description": "All rows from start to current (default for ORDER BY)",
                    "syntax": "ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW",
                    "visual": "[=====current].....",
                },
                {
                    "name": "N PRECEDING to CURRENT ROW",
                    "description": "Last N rows plus current (sliding window)",
                    "syntax": "ROWS BETWEEN 2 PRECEDING AND CURRENT ROW",
                    "visual": "...[--current].....",
                },
                {
                    "name": "N PRECEDING to N FOLLOWING",
                    "description": "Centered window around current row",
                    "syntax": "ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING",
                    "visual": "...[-current-].....",
                },
                {
                    "name": "CURRENT ROW to UNBOUNDED FOLLOWING",
                    "description": "Current row to end",
                    "syntax": "ROWS BETWEEN CURRENT ROW AND UNBOUNDED FOLLOWING",
                    "visual": ".....[current=====]",
                },
            ],
            "moving_average": {
                "title": "3-Day Moving Average",
                "syntax": "AVG(temp) OVER (ORDER BY day ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING)",
                "result": [
                    {"day": 1, "temp": 68, "window": "[68,72]", "moving_avg": 70.0, "note": "No preceding row"},
                    {"day": 2, "temp": 72, "window": "[68,72,75]", "moving_avg": 71.7},
                    {"day": 3, "temp": 75, "window": "[72,75,71]", "moving_avg": 72.7},
                    {"day": 4, "temp": 71, "window": "[75,71,69]", "moving_avg": 71.7},
                    {"day": 5, "temp": 69, "window": "[71,69,73]", "moving_avg": 71.0},
                    {"day": 6, "temp": 73, "window": "[69,73,76]", "moving_avg": 72.7},
                    {"day": 7, "temp": 76, "window": "[73,76]", "moving_avg": 74.5, "note": "No following row"},
                ],
            },
            "rows_vs_range": {
                "title": "ROWS vs RANGE",
                "rows": "Physical row count - exactly N rows before/after",
                "range": "Logical value range - all rows with values within range",
                "example": "With duplicate dates, RANGE includes all duplicates, ROWS counts individual rows",
            },
        }

    def _get_top_n_demo(self) -> dict:
        """Top N per group demonstration."""
        source_data = [
            {"name": "Alice", "dept": "Engineering", "salary": 95000},
            {"name": "Bob", "dept": "Engineering", "salary": 90000},
            {"name": "Carol", "dept": "Engineering", "salary": 85000},
            {"name": "Dave", "dept": "Engineering", "salary": 80000},
            {"name": "Eve", "dept": "Sales", "salary": 75000},
            {"name": "Frank", "dept": "Sales", "salary": 70000},
            {"name": "Grace", "dept": "Sales", "salary": 65000},
            {"name": "Henry", "dept": "HR", "salary": 60000},
            {"name": "Ivy", "dept": "HR", "salary": 55000},
        ]

        return {
            "title": "Top N Per Group Pattern",
            "description": "Get the top 2 highest paid employees in each department",
            "source_data": source_data,
            "window_solution": {
                "query": """SELECT * FROM (
    SELECT name, dept, salary,
           ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC) as rn
    FROM employees
) ranked
WHERE rn <= 2""",
                "step1_result": [
                    {"name": "Alice", "dept": "Engineering", "salary": 95000, "rn": 1},
                    {"name": "Bob", "dept": "Engineering", "salary": 90000, "rn": 2},
                    {"name": "Carol", "dept": "Engineering", "salary": 85000, "rn": 3},
                    {"name": "Dave", "dept": "Engineering", "salary": 80000, "rn": 4},
                    {"name": "Eve", "dept": "Sales", "salary": 75000, "rn": 1},
                    {"name": "Frank", "dept": "Sales", "salary": 70000, "rn": 2},
                    {"name": "Grace", "dept": "Sales", "salary": 65000, "rn": 3},
                    {"name": "Henry", "dept": "HR", "salary": 60000, "rn": 1},
                    {"name": "Ivy", "dept": "HR", "salary": 55000, "rn": 2},
                ],
                "final_result": [
                    {"name": "Alice", "dept": "Engineering", "salary": 95000, "rn": 1},
                    {"name": "Bob", "dept": "Engineering", "salary": 90000, "rn": 2},
                    {"name": "Eve", "dept": "Sales", "salary": 75000, "rn": 1},
                    {"name": "Frank", "dept": "Sales", "salary": 70000, "rn": 2},
                    {"name": "Henry", "dept": "HR", "salary": 60000, "rn": 1},
                    {"name": "Ivy", "dept": "HR", "salary": 55000, "rn": 2},
                ],
            },
            "correlated_subquery": {
                "title": "Without Window Functions (Correlated Subquery)",
                "query": """SELECT e1.name, e1.dept, e1.salary
FROM employees e1
WHERE (
    SELECT COUNT(*) FROM employees e2
    WHERE e2.dept = e1.dept AND e2.salary > e1.salary
) < 2""",
                "problems": [
                    "Runs subquery for EACH row in outer query",
                    "O(n*m) complexity where m is group size",
                    "Harder to read and maintain",
                    "Doesn't handle ties as predictably",
                ],
            },
            "comparison": {
                "window_function": {
                    "complexity": "O(n log n) - single pass with sorting",
                    "readability": "Clear intent: number rows, filter by number",
                    "flexibility": "Easy to change to Top 3, 5, etc.",
                },
                "correlated_subquery": {
                    "complexity": "O(n * m) - subquery per row",
                    "readability": "Complex logic to understand",
                    "flexibility": "Requires rewriting for different N",
                },
                "winner": "Window function is faster, clearer, and more flexible!",
            },
        }

    def _get_quizzes(self) -> list:
        """Interactive quizzes for window functions."""
        return [
            {
                "id": "rank_vs_dense",
                "question": "Given salaries [100, 100, 80], what does DENSE_RANK() return for salary 80?",
                "options": ["1", "2", "3", "4"],
                "correct": "2",
                "explanation": "100s both get rank 1, 80 gets rank 2 (no gap with DENSE_RANK)",
            },
            {
                "id": "row_number_partition",
                "question": "With PARTITION BY dept, when does ROW_NUMBER reset to 1?",
                "options": [
                    "Never - always increments",
                    "At the start of each new department",
                    "Every 10 rows",
                    "When salary changes",
                ],
                "correct": "At the start of each new department",
                "explanation": "PARTITION BY creates separate windows; numbering restarts for each partition",
            },
            {
                "id": "lag_null",
                "question": "What does LAG(value) return for the FIRST row?",
                "options": ["0", "NULL", "The current value", "Error"],
                "correct": "NULL",
                "explanation": "LAG returns NULL when there's no previous row (unless you specify a default)",
            },
            {
                "id": "running_total_frame",
                "question": "For a running total, what's the default frame with ORDER BY?",
                "options": [
                    "ROWS BETWEEN 1 PRECEDING AND CURRENT ROW",
                    "UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING",
                    "UNBOUNDED PRECEDING AND CURRENT ROW",
                    "CURRENT ROW only",
                ],
                "correct": "UNBOUNDED PRECEDING AND CURRENT ROW",
                "explanation": "With ORDER BY, the default frame includes all rows from start to current row",
            },
        ]

    def _get_syntax_reference(self) -> dict:
        """Quick syntax reference."""
        return {
            "title": "Window Function Syntax Reference",
            "general_syntax": "function() OVER ([PARTITION BY cols] [ORDER BY cols] [frame_clause])",
            "ranking_functions": [
                {"name": "ROW_NUMBER()", "description": "Unique sequential number"},
                {"name": "RANK()", "description": "Rank with gaps for ties"},
                {"name": "DENSE_RANK()", "description": "Rank without gaps"},
                {"name": "NTILE(n)", "description": "Divide into n buckets"},
                {"name": "PERCENT_RANK()", "description": "Relative rank (0 to 1)"},
            ],
            "offset_functions": [
                {"name": "LAG(col, n, default)", "description": "Value from n rows before"},
                {"name": "LEAD(col, n, default)", "description": "Value from n rows after"},
                {"name": "FIRST_VALUE(col)", "description": "First value in window"},
                {"name": "LAST_VALUE(col)", "description": "Last value in window"},
                {"name": "NTH_VALUE(col, n)", "description": "Nth value in window"},
            ],
            "aggregate_functions": [
                {"name": "SUM(col) OVER", "description": "Sum within window"},
                {"name": "AVG(col) OVER", "description": "Average within window"},
                {"name": "COUNT(col) OVER", "description": "Count within window"},
                {"name": "MIN(col) OVER", "description": "Minimum within window"},
                {"name": "MAX(col) OVER", "description": "Maximum within window"},
            ],
            "frame_bounds": [
                "UNBOUNDED PRECEDING - Start of partition",
                "n PRECEDING - n rows before current",
                "CURRENT ROW - Current row",
                "n FOLLOWING - n rows after current",
                "UNBOUNDED FOLLOWING - End of partition",
            ],
        }

    def _get_common_mistakes(self) -> list:
        """Common window function mistakes."""
        return [
            {
                "mistake": "Using window function in WHERE clause",
                "wrong": "SELECT * FROM emp WHERE ROW_NUMBER() OVER (...) <= 3",
                "why_wrong": "Window functions execute AFTER WHERE clause",
                "correct": "SELECT * FROM (SELECT *, ROW_NUMBER() OVER (...) as rn FROM emp) t WHERE rn <= 3",
            },
            {
                "mistake": "Forgetting ORDER BY for ranking",
                "wrong": "ROW_NUMBER() OVER (PARTITION BY dept)",
                "why_wrong": "Without ORDER BY, row order is undefined/random",
                "correct": "ROW_NUMBER() OVER (PARTITION BY dept ORDER BY salary DESC)",
            },
            {
                "mistake": "LAST_VALUE returning wrong value",
                "wrong": "LAST_VALUE(price) OVER (ORDER BY date)",
                "why_wrong": "Default frame is UNBOUNDED PRECEDING to CURRENT ROW",
                "correct": "LAST_VALUE(price) OVER (ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)",
            },
            {
                "mistake": "Confusing ROWS and RANGE",
                "wrong": "ROWS BETWEEN with dates expecting date range",
                "why_wrong": "ROWS counts physical rows, RANGE uses logical values",
                "correct": "Use ROWS for physical row count, RANGE for value-based windows",
            },
        ]

    def _get_performance_tips(self) -> list:
        """Performance tips for window functions."""
        return [
            {
                "tip": "Index your ORDER BY columns",
                "why": "Window functions need sorted data; index avoids sort operation",
            },
            {
                "tip": "Minimize PARTITION BY columns",
                "why": "More partitions = more memory for tracking separate windows",
            },
            {
                "tip": "Use specific frame when possible",
                "why": "Smaller frames = less data to process per row",
            },
            {
                "tip": "Combine multiple window functions with same OVER",
                "why": "MySQL can share the sort/partition work",
                "example": "SELECT ROW_NUMBER() OVER w, SUM(x) OVER w FROM t WINDOW w AS (PARTITION BY a ORDER BY b)",
            },
            {
                "tip": "Consider materialized view for expensive window calculations",
                "why": "Pre-compute if data doesn't change frequently",
            },
        ]
