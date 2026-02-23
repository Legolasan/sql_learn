"""Transaction and locking visualization concept."""

from typing import Any

from app.concepts.base import BaseConcept, Step


class TransactionsConcept(BaseConcept):
    name = "transactions"
    display_name = "Transactions & Locking"
    description = "Understand ACID properties, isolation levels, and how MySQL handles concurrent access."
    difficulty = "advanced"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        # ACID properties
        acid = [
            {
                'letter': 'A',
                'name': 'Atomicity',
                'description': 'All or nothing. Either all operations in a transaction succeed, or none do.',
                'example': 'Transfer $100: Debit account A AND credit account B. Both happen or neither.',
                'mysql': 'ROLLBACK undoes all changes if any operation fails.'
            },
            {
                'letter': 'C',
                'name': 'Consistency',
                'description': 'Database moves from one valid state to another. All rules/constraints are satisfied.',
                'example': 'Foreign key constraints, CHECK constraints, triggers all enforced.',
                'mysql': 'Constraints checked at statement or transaction end.'
            },
            {
                'letter': 'I',
                'name': 'Isolation',
                'description': 'Concurrent transactions don\'t interfere with each other.',
                'example': 'Two users updating same row - one waits for the other to commit.',
                'mysql': 'Controlled by isolation level (READ COMMITTED, REPEATABLE READ, etc.)'
            },
            {
                'letter': 'D',
                'name': 'Durability',
                'description': 'Once committed, changes survive system crashes.',
                'example': 'After COMMIT, data is safely written to disk (redo log).',
                'mysql': 'InnoDB uses write-ahead logging (WAL) for durability.'
            }
        ]

        # Isolation levels with scenarios
        isolation_levels = [
            {
                'level': 'READ UNCOMMITTED',
                'description': 'Can see uncommitted changes from other transactions.',
                'problems': ['Dirty reads', 'Non-repeatable reads', 'Phantom reads'],
                'scenario': {
                    'title': 'Dirty Read Example',
                    'timeline': [
                        {'t': 'T1', 'action': 'UPDATE balance = 100', 'state': 'uncommitted'},
                        {'t': 'T2', 'action': 'SELECT balance → sees 100', 'state': 'reads dirty data'},
                        {'t': 'T1', 'action': 'ROLLBACK', 'state': 'change undone'},
                        {'t': 'T2', 'action': 'T2 used invalid data!', 'state': 'problem!'}
                    ]
                },
                'use_case': 'Almost never. Maybe read-only analytics where accuracy isn\'t critical.'
            },
            {
                'level': 'READ COMMITTED',
                'description': 'Can only see committed changes. Each read gets fresh snapshot.',
                'problems': ['Non-repeatable reads', 'Phantom reads'],
                'scenario': {
                    'title': 'Non-Repeatable Read Example',
                    'timeline': [
                        {'t': 'T1', 'action': 'SELECT balance → 100', 'state': 'first read'},
                        {'t': 'T2', 'action': 'UPDATE balance = 200; COMMIT', 'state': 'committed'},
                        {'t': 'T1', 'action': 'SELECT balance → 200', 'state': 'different value!'},
                        {'t': 'T1', 'action': 'Same query, different result', 'state': 'problem?'}
                    ]
                },
                'use_case': 'Default in PostgreSQL, Oracle. Good for most OLTP.'
            },
            {
                'level': 'REPEATABLE READ',
                'description': 'Same query returns same results within a transaction. MySQL default.',
                'problems': ['Phantom reads (partially solved in InnoDB)'],
                'scenario': {
                    'title': 'Consistent Reads',
                    'timeline': [
                        {'t': 'T1', 'action': 'SELECT balance → 100', 'state': 'snapshot taken'},
                        {'t': 'T2', 'action': 'UPDATE balance = 200; COMMIT', 'state': 'committed'},
                        {'t': 'T1', 'action': 'SELECT balance → 100', 'state': 'same value!'},
                        {'t': 'T1', 'action': 'Consistent view of data', 'state': 'good!'}
                    ]
                },
                'use_case': 'MySQL/InnoDB default. Good balance of consistency and performance.'
            },
            {
                'level': 'SERIALIZABLE',
                'description': 'Transactions execute as if serial. Maximum isolation.',
                'problems': ['Performance (lots of locking)'],
                'scenario': {
                    'title': 'Full Serialization',
                    'timeline': [
                        {'t': 'T1', 'action': 'SELECT * FROM accounts', 'state': 'locks range'},
                        {'t': 'T2', 'action': 'INSERT INTO accounts...', 'state': 'blocked!'},
                        {'t': 'T1', 'action': 'COMMIT', 'state': 'releases lock'},
                        {'t': 'T2', 'action': 'INSERT proceeds', 'state': 'now allowed'}
                    ]
                },
                'use_case': 'When absolute correctness required. Financial transactions.'
            }
        ]

        # Lock types
        lock_types = [
            {
                'name': 'Shared Lock (S)',
                'aka': 'Read lock',
                'description': 'Multiple transactions can hold S lock on same row',
                'sql': 'SELECT ... LOCK IN SHARE MODE',
                'compatible_with': ['S'],
                'blocks': ['X']
            },
            {
                'name': 'Exclusive Lock (X)',
                'aka': 'Write lock',
                'description': 'Only one transaction can hold X lock on a row',
                'sql': 'SELECT ... FOR UPDATE',
                'compatible_with': [],
                'blocks': ['S', 'X']
            },
            {
                'name': 'Intention Locks',
                'aka': 'IS, IX',
                'description': 'Table-level hints that row locks will be acquired',
                'sql': 'Automatically acquired',
                'compatible_with': ['IS', 'IX (sometimes)'],
                'blocks': ['Table-level S/X']
            },
            {
                'name': 'Gap Lock',
                'aka': 'Range lock',
                'description': 'Locks gap between index records (prevents phantoms)',
                'sql': 'Implicit in REPEATABLE READ',
                'compatible_with': ['Gap locks'],
                'blocks': ['Inserts into gap']
            }
        ]

        # Deadlock example
        deadlock_example = {
            'title': 'Deadlock Scenario',
            'transactions': [
                {'t': 'T1', 'step': 1, 'action': 'UPDATE accounts SET balance=100 WHERE id=1', 'lock': 'X lock on id=1'},
                {'t': 'T2', 'step': 2, 'action': 'UPDATE accounts SET balance=200 WHERE id=2', 'lock': 'X lock on id=2'},
                {'t': 'T1', 'step': 3, 'action': 'UPDATE accounts SET balance=150 WHERE id=2', 'lock': 'Waits for T2...'},
                {'t': 'T2', 'step': 4, 'action': 'UPDATE accounts SET balance=250 WHERE id=1', 'lock': 'Waits for T1... DEADLOCK!'},
            ],
            'resolution': 'MySQL detects deadlock and rolls back one transaction (victim)',
            'prevention': [
                'Access tables/rows in consistent order',
                'Keep transactions short',
                'Use appropriate isolation level',
                'Add proper indexes to reduce lock scope'
            ]
        }

        return {
            'query': query,
            'acid': acid,
            'isolation_levels': isolation_levels,
            'lock_types': lock_types,
            'deadlock_example': deadlock_example,
            'current_level': 'REPEATABLE READ (MySQL default)'
        }

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        steps = [
            Step(
                title="ACID Properties",
                description="Transactions guarantee Atomicity, Consistency, Isolation, Durability",
                highlight={'acid': True}
            ),
            Step(
                title="Isolation Levels",
                description="Control how much transactions 'see' each other's changes",
                highlight={'isolation': True}
            ),
            Step(
                title="MySQL Default: REPEATABLE READ",
                description="Same query returns same results within a transaction",
                highlight={'level': 'REPEATABLE READ'}
            ),
            Step(
                title="Lock Types",
                description="Shared (read) and Exclusive (write) locks control access",
                highlight={'locks': True}
            ),
            Step(
                title="Deadlock Prevention",
                description="Access rows in consistent order, keep transactions short",
                highlight={'deadlock': True}
            )
        ]
        return steps

    def get_sample_queries(self) -> list[str]:
        return [
            "START TRANSACTION; UPDATE accounts SET balance = balance - 100 WHERE id = 1;",
            "SELECT * FROM accounts WHERE id = 1 FOR UPDATE;",
            "SELECT * FROM accounts WHERE id = 1 LOCK IN SHARE MODE;",
            "SET TRANSACTION ISOLATION LEVEL READ COMMITTED;",
        ]
