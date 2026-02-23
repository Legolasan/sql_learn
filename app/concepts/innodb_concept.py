"""
InnoDB Internals Concept - Understanding how MySQL's InnoDB storage engine works.
Covers buffer pool, redo/undo logs, change buffer, doublewrite buffer, and crash recovery.
"""

from typing import Any

from app.concepts.base import BaseConcept, Step


class InnoDBConcept(BaseConcept):
    """InnoDB storage engine internals with visual animations."""

    name = "innodb-internals"
    display_name = "InnoDB Internals"
    description = "Understand buffer pool, redo/undo logs, change buffer, and crash recovery mechanisms"
    difficulty = "advanced"

    def get_visualization_data(self, query: str, dataset: Any) -> dict:
        """Generate visualization data for InnoDB internals."""
        return {
            "overview": self._get_overview(),
            "buffer_pool": self._get_buffer_pool(),
            "redo_log": self._get_redo_log(),
            "undo_log": self._get_undo_log(),
            "change_buffer": self._get_change_buffer(),
            "doublewrite": self._get_doublewrite_buffer(),
            "crash_recovery": self._get_crash_recovery(),
            "performance_tuning": self._get_performance_tuning(),
        }

    def get_steps(self, query: str, dataset: Any) -> list[Step]:
        return [
            Step(
                title="InnoDB Architecture Overview",
                description="InnoDB is MySQL's default storage engine, designed for reliability and performance with ACID compliance.",
                highlight={'section': 'overview'}
            ),
            Step(
                title="Buffer Pool",
                description="The buffer pool is InnoDB's cache for data and indexes. Most operations happen in memory for speed.",
                highlight={'section': 'buffer_pool'}
            ),
            Step(
                title="Redo Log (Write-Ahead Logging)",
                description="Changes are written to the redo log BEFORE updating data pages. This ensures durability even on crash.",
                highlight={'section': 'redo_log'}
            ),
            Step(
                title="Undo Log",
                description="Undo logs enable transaction rollback and MVCC (Multi-Version Concurrency Control) for consistent reads.",
                highlight={'section': 'undo_log'}
            ),
            Step(
                title="Change Buffer",
                description="Delays secondary index updates to reduce random I/O. Changes are merged later during reads or background flush.",
                highlight={'section': 'change_buffer'}
            ),
            Step(
                title="Doublewrite Buffer",
                description="Protects against partial page writes during crash. Pages are written twice for safety.",
                highlight={'section': 'doublewrite'}
            ),
            Step(
                title="Crash Recovery",
                description="On restart after crash, InnoDB replays redo logs and rolls back uncommitted transactions.",
                highlight={'section': 'crash_recovery'}
            ),
        ]

    def get_sample_queries(self) -> list[str]:
        return [
            "SHOW ENGINE INNODB STATUS",
            "SELECT * FROM information_schema.INNODB_BUFFER_POOL_STATS",
            "SHOW VARIABLES LIKE 'innodb_buffer_pool%'",
            "SHOW VARIABLES LIKE 'innodb_log%'",
        ]

    def _get_overview(self) -> dict:
        return {
            "title": "InnoDB Storage Engine Architecture",
            "description": "InnoDB is MySQL's default transactional storage engine, designed for high reliability and performance.",
            "key_features": [
                "ACID compliant transactions",
                "Row-level locking (high concurrency)",
                "Foreign key constraints",
                "Crash recovery",
                "MVCC for consistent reads",
                "Clustered index organization",
            ],
            "architecture_layers": [
                {
                    "name": "In-Memory Structures",
                    "components": ["Buffer Pool", "Change Buffer", "Adaptive Hash Index", "Log Buffer"],
                    "color": "blue",
                },
                {
                    "name": "Background Threads",
                    "components": ["Master Thread", "IO Threads", "Purge Threads", "Page Cleaner"],
                    "color": "green",
                },
                {
                    "name": "On-Disk Structures",
                    "components": ["System Tablespace", "Redo Logs", "Undo Logs", "Table Data Files"],
                    "color": "orange",
                },
            ],
            "data_flow": "Query → Buffer Pool (memory) → Redo Log (disk) → Data Files (disk)",
        }

    def _get_buffer_pool(self) -> dict:
        return {
            "title": "Buffer Pool: InnoDB's Memory Cache",
            "description": "The buffer pool caches data pages and index pages in memory. Most reads/writes happen here.",
            "why_important": "Disk I/O is slow. Keeping frequently used data in memory is 100-1000x faster.",
            "structure": {
                "pages": {
                    "description": "Data is organized into 16KB pages",
                    "types": ["Data Pages", "Index Pages", "Undo Pages", "Insert Buffer Pages"],
                },
                "lists": {
                    "lru_list": "Recently used pages (hot data stays in memory)",
                    "free_list": "Empty pages available for new data",
                    "flush_list": "Dirty pages that need to be written to disk",
                },
            },
            "lru_algorithm": {
                "title": "LRU (Least Recently Used) with Midpoint",
                "description": "InnoDB uses a modified LRU to prevent full table scans from evicting hot data",
                "how_it_works": [
                    "New pages enter at the midpoint (3/8 from the head), not the head",
                    "Pages that are accessed again move to the head (young sublist)",
                    "Pages that aren't accessed drift to the tail (old sublist)",
                    "Tail pages are evicted when space is needed",
                ],
                "young_sublist": "Hot data - frequently accessed pages",
                "old_sublist": "Cold data - recently loaded but not re-accessed",
            },
            "demo_pages": [
                {"id": 1, "table": "employees", "type": "data", "status": "young", "dirty": False},
                {"id": 2, "table": "employees", "type": "index", "status": "young", "dirty": True},
                {"id": 3, "table": "orders", "type": "data", "status": "young", "dirty": False},
                {"id": 4, "table": "departments", "type": "data", "status": "old", "dirty": False},
                {"id": 5, "table": "products", "type": "data", "status": "old", "dirty": True},
                {"id": 6, "table": "orders", "type": "index", "status": "old", "dirty": False},
            ],
            "sizing": {
                "recommendation": "Set buffer pool to 50-75% of available RAM on dedicated DB server",
                "variable": "innodb_buffer_pool_size",
                "check_hit_rate": "SELECT (1 - (Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests)) * 100 AS hit_rate",
                "target_hit_rate": "99%+ is ideal",
            },
        }

    def _get_redo_log(self) -> dict:
        return {
            "title": "Redo Log: Write-Ahead Logging (WAL)",
            "description": "The redo log records all changes BEFORE they're applied to data pages. This is the key to durability.",
            "why_wal": {
                "problem": "Random writes to data files are slow",
                "solution": "Write changes sequentially to redo log (fast), update data pages later",
                "benefit": "Even if crash occurs before data pages are updated, changes can be recovered from redo log",
            },
            "structure": {
                "description": "Circular log files that are continuously overwritten",
                "files": "Typically 2+ files (ib_logfile0, ib_logfile1)",
                "size": "innodb_log_file_size (default 48MB per file)",
                "circular": "When log fills up, it wraps around and overwrites old entries (after checkpoint)",
            },
            "write_flow": [
                {"step": 1, "action": "Transaction modifies row", "location": "Buffer Pool"},
                {"step": 2, "action": "Change recorded in log buffer", "location": "Memory"},
                {"step": 3, "action": "Log buffer flushed to redo log", "location": "Disk", "timing": "On COMMIT"},
                {"step": 4, "action": "Dirty page written to data file", "location": "Disk", "timing": "Later (checkpoint)"},
            ],
            "commit_durability": {
                "title": "innodb_flush_log_at_trx_commit",
                "options": [
                    {"value": "1", "behavior": "Flush to disk on every commit", "durability": "Highest", "performance": "Slowest"},
                    {"value": "2", "behavior": "Write to OS cache on commit, flush every second", "durability": "Medium", "performance": "Faster"},
                    {"value": "0", "behavior": "Flush every second regardless of commits", "durability": "Lowest", "performance": "Fastest"},
                ],
                "recommendation": "Use 1 for critical data, 2 for better performance with acceptable risk",
            },
            "checkpoint": {
                "description": "Periodically, dirty pages are flushed and the redo log position is advanced",
                "purpose": "Allows old log entries to be overwritten and speeds up crash recovery",
                "sharp_checkpoint": "Flush all dirty pages (rarely used)",
                "fuzzy_checkpoint": "Flush some dirty pages continuously (normal operation)",
            },
        }

    def _get_undo_log(self) -> dict:
        return {
            "title": "Undo Log: Rollback and MVCC",
            "description": "Undo logs store previous versions of rows, enabling transaction rollback and consistent reads.",
            "two_purposes": {
                "rollback": {
                    "description": "If transaction fails or is rolled back, undo log restores original data",
                    "example": "UPDATE salary SET amount = 100 → undo stores old amount to restore on ROLLBACK",
                },
                "mvcc": {
                    "description": "Multi-Version Concurrency Control - readers see consistent snapshot without blocking writers",
                    "example": "Transaction A reads row while Transaction B updates it - A sees the old version from undo log",
                },
            },
            "how_it_works": [
                {"step": 1, "description": "Transaction begins modifying a row"},
                {"step": 2, "description": "Original row data copied to undo log"},
                {"step": 3, "description": "Row is updated in buffer pool with pointer to undo record"},
                {"step": 4, "description": "Other transactions can follow pointer chain to see older versions"},
            ],
            "rollback_segment": {
                "description": "Undo logs are organized in rollback segments",
                "default_count": "128 rollback segments by default",
                "location": "System tablespace or separate undo tablespaces",
            },
            "purge": {
                "description": "Old undo records are cleaned up when no transaction needs them",
                "thread": "Purge thread runs in background",
                "history_list": "Tracks undo records waiting to be purged",
            },
            "demo_versions": [
                {"version": "Current", "salary": 90000, "trx_id": 105, "note": "Latest version"},
                {"version": "Undo 1", "salary": 85000, "trx_id": 102, "note": "Previous update"},
                {"version": "Undo 2", "salary": 80000, "trx_id": 98, "note": "Original insert"},
            ],
        }

    def _get_change_buffer(self) -> dict:
        return {
            "title": "Change Buffer: Deferred Secondary Index Updates",
            "description": "Caches changes to secondary index pages when those pages aren't in the buffer pool.",
            "problem": {
                "description": "Secondary index updates often require random disk I/O to load index pages",
                "example": "INSERT into table with 5 secondary indexes = potentially 5 random reads",
            },
            "solution": {
                "description": "Buffer the changes in memory, merge them later",
                "when_merge": [
                    "When the index page is read for another operation",
                    "During background merge by InnoDB",
                    "During crash recovery",
                ],
            },
            "what_is_buffered": [
                {"operation": "INSERT", "buffered": True},
                {"operation": "DELETE marking", "buffered": True},
                {"operation": "UPDATE (delete + insert)", "buffered": True},
                {"operation": "Primary key changes", "buffered": False, "reason": "Primary key = clustered index"},
                {"operation": "Unique index changes", "buffered": "Configurable", "reason": "May need uniqueness check"},
            ],
            "benefits": {
                "reduces_random_io": "Changes are written sequentially, merged in batches",
                "speeds_up_writes": "Don't need to load index pages immediately",
            },
            "configuration": {
                "variable": "innodb_change_buffering",
                "options": ["none", "inserts", "deletes", "changes", "purges", "all"],
                "default": "all",
            },
            "when_less_useful": [
                "SSD storage (random I/O is fast)",
                "Small database that fits in buffer pool",
                "Mostly read workload",
            ],
        }

    def _get_doublewrite_buffer(self) -> dict:
        return {
            "title": "Doublewrite Buffer: Partial Write Protection",
            "description": "Prevents data corruption from partial page writes during crash.",
            "problem": {
                "description": "InnoDB pages are 16KB. OS/disk typically writes 4KB at a time.",
                "scenario": "If crash occurs mid-write, page could be half-old/half-new = corrupted",
                "torn_page": "A page that was only partially written is called a 'torn page'",
            },
            "solution": {
                "step1": "Before writing dirty pages to data files, write them to doublewrite buffer",
                "step2": "Doublewrite buffer is a contiguous area on disk (sequential write = fast)",
                "step3": "After doublewrite completes, write pages to their actual locations",
                "step4": "On crash, check if page is torn. If so, restore from doublewrite buffer.",
            },
            "write_flow": [
                {"step": 1, "action": "Dirty pages selected for flush"},
                {"step": 2, "action": "Pages written to doublewrite buffer (sequential)", "location": "System tablespace"},
                {"step": 3, "action": "fsync() to ensure doublewrite is on disk"},
                {"step": 4, "action": "Pages written to actual data file locations (random)"},
                {"step": 5, "action": "fsync() to ensure data files are updated"},
            ],
            "recovery": {
                "description": "On startup, InnoDB checks each page's checksum",
                "if_valid": "Page is fine, no action needed",
                "if_torn": "Page is corrupted - restore from doublewrite buffer",
            },
            "performance": {
                "overhead": "Roughly 2x write amplification",
                "when_disable": "Some SSDs have atomic 16KB writes - doublewrite may be disabled",
                "variable": "innodb_doublewrite = ON/OFF",
            },
        }

    def _get_crash_recovery(self) -> dict:
        return {
            "title": "Crash Recovery: What Happens on Restart",
            "description": "InnoDB automatically recovers to a consistent state after an unexpected shutdown.",
            "timeline": {
                "title": "Recovery Timeline Story",
                "events": [
                    {
                        "time": "T1",
                        "event": "Transaction 100 commits (UPDATE salary = 90000)",
                        "redo": "Written to redo log",
                        "data": "Page marked dirty but not yet flushed",
                    },
                    {
                        "time": "T2",
                        "event": "Transaction 101 starts (UPDATE salary = 95000)",
                        "redo": "Written to redo log",
                        "data": "Page modified in buffer pool",
                    },
                    {
                        "time": "T3",
                        "event": "CRASH! Power failure",
                        "state": "Trx 100 committed (must be preserved), Trx 101 uncommitted (must be rolled back)",
                    },
                    {
                        "time": "T4",
                        "event": "Server restarts",
                        "action": "Begin crash recovery",
                    },
                    {
                        "time": "T5",
                        "event": "Redo phase: replay redo log from last checkpoint",
                        "action": "Re-apply all changes, including uncommitted",
                    },
                    {
                        "time": "T6",
                        "event": "Undo phase: rollback uncommitted transactions",
                        "action": "Use undo log to reverse Transaction 101's changes",
                    },
                    {
                        "time": "T7",
                        "event": "Recovery complete",
                        "result": "Database consistent: salary = 90000 (Trx 100's committed value)",
                    },
                ],
            },
            "phases": {
                "redo": {
                    "name": "Redo Phase (Roll Forward)",
                    "description": "Replay all changes from redo log since last checkpoint",
                    "purpose": "Bring data pages up to the state at crash time",
                    "includes": "Both committed and uncommitted transactions",
                },
                "undo": {
                    "name": "Undo Phase (Roll Back)",
                    "description": "Rollback any transactions that weren't committed",
                    "purpose": "Remove changes from uncommitted transactions",
                    "uses": "Undo log records to reverse changes",
                },
            },
            "checksum": {
                "description": "Every page has a checksum to detect corruption",
                "torn_page_detection": "If checksum fails, page is corrupt - restore from doublewrite buffer",
            },
            "speed_factors": [
                "Size of redo log to replay",
                "Number of uncommitted transactions to rollback",
                "I/O speed of storage",
                "innodb_log_file_size setting",
            ],
        }

    def _get_performance_tuning(self) -> list:
        return [
            {
                "setting": "innodb_buffer_pool_size",
                "description": "Total memory for buffer pool",
                "recommendation": "50-75% of RAM on dedicated server",
                "default": "128MB (too small for production!)",
            },
            {
                "setting": "innodb_log_file_size",
                "description": "Size of each redo log file",
                "recommendation": "Large enough for 1-2 hours of writes",
                "tradeoff": "Larger = better write performance, but longer recovery",
            },
            {
                "setting": "innodb_flush_log_at_trx_commit",
                "description": "When to flush redo log to disk",
                "recommendation": "1 for safety, 2 for performance with some risk",
            },
            {
                "setting": "innodb_flush_method",
                "description": "How InnoDB flushes data and logs",
                "recommendation": "O_DIRECT on Linux to bypass OS cache",
            },
            {
                "setting": "innodb_io_capacity",
                "description": "I/O operations per second for background tasks",
                "recommendation": "Match your storage capability (200 for HDD, 2000+ for SSD)",
            },
            {
                "setting": "innodb_buffer_pool_instances",
                "description": "Split buffer pool into multiple instances",
                "recommendation": "1 per GB of buffer pool (reduces contention)",
            },
        ]
