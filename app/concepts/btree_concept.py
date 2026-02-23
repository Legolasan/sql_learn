"""B-Tree visualization concept."""

from typing import Any

from app.concepts.base import BaseConcept, Step
from app.engine.btree import BTree, build_btree_from_column
from app.engine.query_parser import parse_query


class BTreeConcept(BaseConcept):
    name = "btree"
    display_name = "B-Tree Indexing"
    description = "See how MySQL uses B-trees to find data efficiently. Compare indexed lookups vs full table scans."
    difficulty = "beginner"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        parsed = parse_query(query)

        if not parsed.tables:
            return {'error': 'No table specified in query'}

        table_name = parsed.tables[0]
        table_data = dataset.get_table(table_name)

        if not table_data:
            return {'error': f'Table "{table_name}" not found'}

        # Determine which column to visualize
        search_column = None
        search_value = None
        search_op = '='

        for cond in parsed.where_conditions:
            search_column = cond.get('column')
            search_value = cond.get('value')
            search_op = cond.get('op', '=')
            break

        if not search_column:
            # Default to primary key visualization
            search_column = 'id'

        # Build B-tree for the column
        column_values = []
        for i, row in enumerate(table_data):
            val = getattr(row, search_column, None)
            if val is not None:
                column_values.append((val, row.id))

        btree = build_btree_from_column(column_values, order=4)

        # Perform search if we have a value
        traversal = []
        result = None
        if search_value is not None:
            if search_op in ('>', '>=', '<', '<='):
                # Range search
                if search_op == '>':
                    result, traversal = btree.range_search(search_value + 0.01, float('inf'))
                elif search_op == '>=':
                    result, traversal = btree.range_search(search_value, float('inf'))
                elif search_op == '<':
                    result, traversal = btree.range_search(float('-inf'), search_value - 0.01)
                elif search_op == '<=':
                    result, traversal = btree.range_search(float('-inf'), search_value)
            else:
                result, traversal = btree.search(search_value)

        # Calculate comparison stats
        full_scan_comparisons = len(table_data)
        btree_comparisons = len(traversal)

        return {
            'tree_structure': btree.get_tree_structure(),
            'all_nodes': btree.get_all_nodes(),
            'traversal': [{'node_id': t.node_id, 'comparison': t.comparison, 'action': t.action} for t in traversal],
            'search_column': search_column,
            'search_value': search_value,
            'search_op': search_op,
            'result': result,
            'stats': {
                'full_scan_comparisons': full_scan_comparisons,
                'btree_comparisons': btree_comparisons,
                'efficiency': f"{(1 - btree_comparisons/full_scan_comparisons)*100:.0f}% fewer comparisons" if full_scan_comparisons > 0 else "N/A"
            },
            'table_name': table_name,
            'total_rows': len(table_data)
        }

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        viz_data = self.get_visualization_data(query, dataset)

        if 'error' in viz_data:
            return [Step(
                title="Error",
                description=viz_data['error'],
                highlight={}
            )]

        steps = []

        # Initial state
        steps.append(Step(
            title="B-Tree Index Built",
            description=f"Index on '{viz_data['search_column']}' column with {viz_data['total_rows']} values",
            highlight={'node_ids': []}
        ))

        # Add traversal steps
        for i, t in enumerate(viz_data['traversal']):
            steps.append(Step(
                title=f"Step {i+1}: {t['action'].replace('_', ' ').title()}",
                description=t['comparison'],
                highlight={'node_ids': [t['node_id']], 'current': t['node_id']}
            ))

        # Result step
        if viz_data['result'] is not None:
            steps.append(Step(
                title="Result Found!",
                description=f"Found matching row(s). B-tree used {viz_data['stats']['btree_comparisons']} comparisons vs {viz_data['stats']['full_scan_comparisons']} for full scan.",
                highlight={'node_ids': [t['node_id'] for t in viz_data['traversal']], 'complete': True}
            ))
        else:
            steps.append(Step(
                title="Not Found",
                description=f"Value not in index after {viz_data['stats']['btree_comparisons']} comparisons",
                highlight={'complete': True}
            ))

        return steps

    def get_sample_queries(self) -> list[str]:
        return [
            "SELECT * FROM employees WHERE salary > 80000",
            "SELECT * FROM employees WHERE id = 5",
            "SELECT * FROM employees WHERE department_id = 1",
            "SELECT * FROM orders WHERE amount > 10000",
        ]
