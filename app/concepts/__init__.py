from app.concepts.base import BaseConcept, Step

# Concept registry
_concepts: dict[str, BaseConcept] = {}


def register_concept(concept: BaseConcept):
    """Register a concept in the global registry."""
    _concepts[concept.name] = concept


def get_concept(name: str) -> BaseConcept | None:
    """Get a concept by name."""
    return _concepts.get(name)


def get_all_concepts() -> list[BaseConcept]:
    """Get all registered concepts sorted by difficulty."""
    difficulty_order = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
    return sorted(_concepts.values(), key=lambda c: difficulty_order.get(c.difficulty, 1))


# Import and register all concepts
from app.concepts.btree_concept import BTreeConcept
from app.concepts.explain_concept import ExplainConcept
from app.concepts.exec_order_concept import ExecOrderConcept
from app.concepts.joins_concept import JoinsConcept
from app.concepts.where_vs_having_concept import WhereVsHavingConcept
from app.concepts.index_types_concept import IndexTypesConcept
from app.concepts.subquery_concept import SubqueryConcept
from app.concepts.optimization_concept import OptimizationConcept
from app.concepts.transactions_concept import TransactionsConcept
from app.concepts.normalization_concept import NormalizationConcept
from app.concepts.cte_concept import CTEConcept
from app.concepts.sql_basics_concept import SQLBasicsConcept
from app.concepts.data_types_concept import DataTypesNullsConcept
from app.concepts.join_types_concept import JoinTypesConcept
from app.concepts.cardinality_concept import CardinalityConcept
from app.concepts.window_functions_concept import WindowFunctionsConcept
from app.concepts.innodb_concept import InnoDBConcept
from app.concepts.data_layout_concept import DataLayoutConcept
from app.concepts.mysql_intro_concept import MySQLIntroConcept

register_concept(MySQLIntroConcept())
register_concept(SQLBasicsConcept())
register_concept(DataTypesNullsConcept())
register_concept(JoinTypesConcept())
register_concept(CardinalityConcept())
register_concept(BTreeConcept())
register_concept(ExplainConcept())
register_concept(ExecOrderConcept())
register_concept(JoinsConcept())
register_concept(WhereVsHavingConcept())
register_concept(IndexTypesConcept())
register_concept(SubqueryConcept())
register_concept(OptimizationConcept())
register_concept(TransactionsConcept())
register_concept(NormalizationConcept())
register_concept(CTEConcept())
register_concept(WindowFunctionsConcept())
register_concept(InnoDBConcept())
register_concept(DataLayoutConcept())
