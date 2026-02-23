"""
Custom exceptions for query execution with helpful error messages.
"""

from difflib import get_close_matches


class QueryError(Exception):
    """Base exception for query errors."""

    def __init__(self, message: str, suggestion: str = None,
                 error_type: str = "error", context: dict = None):
        self.message = message
        self.suggestion = suggestion
        self.error_type = error_type  # error, warning, info
        self.context = context or {}
        super().__init__(message)


class SyntaxError(QueryError):
    """Invalid SQL syntax."""

    def __init__(self, message: str, near: str = None):
        suggestion = None
        if near:
            # Common typos
            typo_fixes = {
                'selec': 'SELECT',
                'slect': 'SELECT',
                'form': 'FROM',
                'fom': 'FROM',
                'whre': 'WHERE',
                'wher': 'WHERE',
                'oder': 'ORDER',
                'ordr': 'ORDER',
                'gorup': 'GROUP',
                'gruop': 'GROUP',
            }
            near_lower = near.lower()
            if near_lower in typo_fixes:
                suggestion = f"Did you mean: {typo_fixes[near_lower]}?"

        super().__init__(
            message=message,
            suggestion=suggestion,
            error_type="error",
            context={'near': near}
        )


class UnknownTableError(QueryError):
    """Table doesn't exist in dataset."""

    def __init__(self, table_name: str, available_tables: list[str]):
        # Find close matches
        matches = get_close_matches(table_name.lower(),
                                     [t.lower() for t in available_tables],
                                     n=1, cutoff=0.6)
        suggestion = None
        if matches:
            suggestion = f"Did you mean: {matches[0]}?"
        else:
            suggestion = f"Available tables: {', '.join(available_tables)}"

        super().__init__(
            message=f"Unknown table: '{table_name}'",
            suggestion=suggestion,
            error_type="error",
            context={'table': table_name, 'available': available_tables}
        )


class UnknownColumnError(QueryError):
    """Column doesn't exist in table."""

    def __init__(self, column_name: str, table_name: str, available_columns: list[str]):
        # Find close matches
        matches = get_close_matches(column_name.lower(),
                                     [c.lower() for c in available_columns],
                                     n=1, cutoff=0.6)
        if matches:
            suggestion = f"Did you mean: {matches[0]}?"
        else:
            suggestion = f"Available columns in {table_name}: {', '.join(available_columns)}"

        super().__init__(
            message=f"Unknown column: '{column_name}' in table '{table_name}'",
            suggestion=suggestion,
            error_type="error",
            context={'column': column_name, 'table': table_name, 'available': available_columns}
        )


class TypeMismatchError(QueryError):
    """Type mismatch in comparison."""

    def __init__(self, column: str, expected_type: str, got_type: str):
        super().__init__(
            message=f"Type mismatch: column '{column}' is {expected_type}, but compared with {got_type}",
            suggestion=f"Use a {expected_type} value for comparison",
            error_type="error",
            context={'column': column, 'expected': expected_type, 'got': got_type}
        )


class UnsupportedFeatureError(QueryError):
    """Valid SQL but not supported in this demo."""

    def __init__(self, feature: str, alternative: str = None):
        super().__init__(
            message=f"Unsupported feature: {feature}",
            suggestion=alternative or "This feature is not available in the demo",
            error_type="warning",
            context={'feature': feature}
        )


class EmptyQueryError(QueryError):
    """Empty or whitespace-only query."""

    def __init__(self):
        super().__init__(
            message="Empty query",
            suggestion="Enter a SQL query like: SELECT * FROM employees",
            error_type="info"
        )


class NoTablesError(QueryError):
    """Query doesn't specify a table."""

    def __init__(self):
        super().__init__(
            message="No table specified in query",
            suggestion="Add a FROM clause: SELECT * FROM employees",
            error_type="error"
        )
