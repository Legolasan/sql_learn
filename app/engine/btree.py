"""
B-Tree simulation for MySQL index visualization.
Implements a simplified B+ tree that tracks traversal for visualization.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BTreeNode:
    """A node in the B-tree."""
    keys: list[Any] = field(default_factory=list)
    values: list[Any] = field(default_factory=list)  # Only in leaf nodes
    children: list['BTreeNode'] = field(default_factory=list)
    is_leaf: bool = True
    node_id: int = 0

    def to_dict(self) -> dict:
        """Convert node to dict for visualization."""
        return {
            'id': self.node_id,
            'keys': self.keys,
            'values': self.values if self.is_leaf else [],
            'is_leaf': self.is_leaf,
            'children': [c.node_id for c in self.children]
        }


@dataclass
class TraversalStep:
    """A single step in B-tree traversal."""
    node_id: int
    keys_checked: list[Any]
    comparison: str  # e.g., "50000 < 75000, go left"
    action: str  # "compare", "descend", "found", "not_found"


class BTree:
    """B+ Tree implementation for visualization."""

    def __init__(self, order: int = 4):
        self.order = order  # Max keys per node
        self.root = BTreeNode(node_id=0)
        self._node_counter = 1
        self._all_nodes: dict[int, BTreeNode] = {0: self.root}

    def _new_node(self, is_leaf: bool = True) -> BTreeNode:
        """Create a new node with unique ID."""
        node = BTreeNode(node_id=self._node_counter, is_leaf=is_leaf)
        self._all_nodes[self._node_counter] = node
        self._node_counter += 1
        return node

    def insert(self, key: Any, value: Any):
        """Insert a key-value pair into the tree."""
        root = self.root

        if len(root.keys) == self.order - 1:
            # Root is full, need to split
            new_root = self._new_node(is_leaf=False)
            new_root.children.append(self.root)
            self._split_child(new_root, 0)
            self.root = new_root
            self._all_nodes[new_root.node_id] = new_root

        self._insert_non_full(self.root, key, value)

    def _insert_non_full(self, node: BTreeNode, key: Any, value: Any):
        """Insert into a non-full node."""
        i = len(node.keys) - 1

        if node.is_leaf:
            # Find position and insert
            node.keys.append(None)
            node.values.append(None)
            while i >= 0 and key < node.keys[i]:
                node.keys[i + 1] = node.keys[i]
                node.values[i + 1] = node.values[i]
                i -= 1
            node.keys[i + 1] = key
            node.values[i + 1] = value
        else:
            # Find child to descend to
            while i >= 0 and key < node.keys[i]:
                i -= 1
            i += 1

            if len(node.children[i].keys) == self.order - 1:
                self._split_child(node, i)
                if key > node.keys[i]:
                    i += 1

            self._insert_non_full(node.children[i], key, value)

    def _split_child(self, parent: BTreeNode, index: int):
        """Split a full child node."""
        full_node = parent.children[index]
        mid = (self.order - 1) // 2

        new_node = self._new_node(is_leaf=full_node.is_leaf)

        # Move half the keys to new node
        new_node.keys = full_node.keys[mid + 1:]
        if full_node.is_leaf:
            new_node.values = full_node.values[mid + 1:]
            full_node.values = full_node.values[:mid + 1]
        else:
            new_node.children = full_node.children[mid + 1:]
            full_node.children = full_node.children[:mid + 1]

        # Move middle key up to parent
        parent.keys.insert(index, full_node.keys[mid])
        parent.children.insert(index + 1, new_node)

        full_node.keys = full_node.keys[:mid]

    def search(self, key: Any) -> tuple[Any | None, list[TraversalStep]]:
        """
        Search for a key and return value + traversal path.

        Returns:
            Tuple of (value or None, list of traversal steps)
        """
        steps = []
        node = self.root

        while True:
            # Record the comparison step
            step = TraversalStep(
                node_id=node.node_id,
                keys_checked=node.keys.copy(),
                comparison="",
                action="compare"
            )

            # Find position
            i = 0
            comparisons = []
            while i < len(node.keys) and key > node.keys[i]:
                comparisons.append(f"{key} > {node.keys[i]}")
                i += 1

            if i < len(node.keys) and key == node.keys[i]:
                comparisons.append(f"{key} = {node.keys[i]}")
                step.comparison = ", ".join(comparisons) if comparisons else f"Found {key}"
                step.action = "found"
                steps.append(step)
                if node.is_leaf:
                    return node.values[i], steps
                return key, steps

            step.comparison = ", ".join(comparisons) if comparisons else f"{key} < {node.keys[0] if node.keys else 'empty'}"

            if node.is_leaf:
                step.action = "not_found"
                steps.append(step)
                return None, steps

            step.action = "descend"
            step.comparison += f" -> descend to child {i}"
            steps.append(step)
            node = node.children[i]

    def range_search(self, min_val: Any, max_val: Any) -> tuple[list[tuple[Any, Any]], list[TraversalStep]]:
        """
        Search for all values in a range.

        Returns:
            Tuple of (list of (key, value) pairs, traversal steps)
        """
        steps = []
        results = []

        # Find starting point
        node = self.root
        while not node.is_leaf:
            step = TraversalStep(
                node_id=node.node_id,
                keys_checked=node.keys.copy(),
                comparison=f"Finding start >= {min_val}",
                action="descend"
            )
            steps.append(step)

            i = 0
            while i < len(node.keys) and min_val > node.keys[i]:
                i += 1
            node = node.children[i]

        # Scan leaf nodes
        step = TraversalStep(
            node_id=node.node_id,
            keys_checked=node.keys.copy(),
            comparison=f"Scanning leaf for values in [{min_val}, {max_val}]",
            action="scan"
        )
        steps.append(step)

        for i, key in enumerate(node.keys):
            if min_val <= key <= max_val:
                results.append((key, node.values[i]))

        return results, steps

    def get_all_nodes(self) -> list[dict]:
        """Get all nodes for visualization."""
        return [node.to_dict() for node in self._all_nodes.values()]

    def get_tree_structure(self) -> dict:
        """Get tree structure for SVG visualization."""

        def build_structure(node: BTreeNode, level: int = 0, position: int = 0) -> dict:
            children = []
            for i, child in enumerate(node.children):
                children.append(build_structure(child, level + 1, i))

            return {
                'id': node.node_id,
                'keys': node.keys,
                'is_leaf': node.is_leaf,
                'level': level,
                'position': position,
                'children': children
            }

        return build_structure(self.root)


def build_btree_from_column(values: list[tuple[Any, Any]], order: int = 4) -> BTree:
    """
    Build a B-tree from a list of (key, row_id) tuples.
    Used to simulate an index on a column.
    """
    tree = BTree(order=order)
    for key, row_id in sorted(values):
        tree.insert(key, row_id)
    return tree
