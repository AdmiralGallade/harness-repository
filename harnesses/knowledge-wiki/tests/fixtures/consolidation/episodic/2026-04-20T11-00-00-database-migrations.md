---
timestamp: 2026-04-20T11:00:00Z
worker: qwen-local
task_id: research-migrations-001
tags: [architecture]
wiki: test-consolidation
---

# Database Migration Patterns Research

Zero-downtime database migrations require careful planning to avoid service disruption during schema changes. The fundamental principle is that the application must be compatible with both the old and new schema simultaneously during the migration window. This means destructive changes (dropping columns, renaming tables) must be split into multiple deployment phases: first deploy code that no longer uses the old column, then drop the column in a subsequent migration after verifying no queries reference it.

The expand-contract pattern formalizes this approach into two phases. During the expand phase, new columns or tables are added alongside existing ones, and the application writes to both old and new structures. During the contract phase, once all reads have been migrated to the new structure and the old data is no longer needed, the old columns or tables are removed. This pattern naturally supports rolling deployments where old and new application versions coexist.

Blue-green deployments for database schemas extend the blue-green concept to data layers. Two parallel schema versions are maintained, with a migration process copying and transforming data between them. Traffic is switched atomically from the blue schema to the green schema once migration is verified complete. This approach works well for major schema overhauls but requires careful handling of writes during the migration window to avoid data loss — typically accomplished through dual-write or change data capture (CDC) mechanisms.

Backward-compatible migrations are the safest default approach. Every migration should be reversible, and rollback scripts should be tested as part of the migration process. Column additions with default values, index creation with CONCURRENTLY (in PostgreSQL), and nullable new columns are all backward-compatible operations. Migration frameworks like Flyway and Liquibase track applied migrations and support dry-run validation before execution.
