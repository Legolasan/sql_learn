from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class Step:
    """A single step in the visualization."""
    title: str
    description: str
    highlight: dict[str, Any]  # Data to highlight in visualization
    data_snapshot: Any = None  # Optional data state at this step


class BaseConcept(ABC):
    """Base class for all MySQL concepts."""

    name: str  # URL slug (e.g., "btree")
    display_name: str  # UI name (e.g., "B-Tree Indexing")
    description: str  # Short description
    difficulty: str  # "beginner" | "intermediate" | "advanced"
    icon: str = "database"  # Icon name for UI

    @abstractmethod
    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        """
        Return data needed for the visualization template.

        Args:
            query: The SQL query entered by the user
            dataset: The static dataset

        Returns:
            Dictionary with visualization-specific data
        """
        pass

    @abstractmethod
    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        """
        Return step-by-step breakdown for animation.

        Args:
            query: The SQL query entered by the user
            dataset: The static dataset

        Returns:
            List of Steps for step-through animation
        """
        pass

    @property
    def template_name(self) -> str:
        """Template path for this concept."""
        return f"concepts/{self.name}.html"

    def get_sample_queries(self) -> list[str]:
        """Return sample queries for this concept."""
        return []
