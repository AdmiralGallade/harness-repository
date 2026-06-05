# Harness Repository

Central repository for VS Code Harness Manager extension. Contains predefined harnesses and skills for project initialization.

## Structure

- **`/harnesses`** - Contains harness templates and configurations
- **`/skills`** - Contains skill definitions and implementations
- **`harnesses.json`** - Main manifest listing all available harnesses

## Harness Types

### Data Intensive
Optimized for large-scale data processing workflows. Includes caching strategies, batch processing templates, and performance monitoring.

### Migration
For migrating between systems or versions. Includes compatibility checks, data transformation utilities, and rollback procedures.

## Usage

The VS Code Harness Manager extension fetches this repository to provide users with available harness templates.

## Adding a New Harness

Use the `import-harness` skill in Claude Code for a guided import:

```
/import-harness
```

The skill will walk you through copying files, building the manifest entry, and adding attribution.

### Manual steps

1. Create a new folder in `/harnesses/<harness-name>/`
2. Copy source files preserving directory structure
3. Add an attribution block to the harness `README.md` (see below)
4. Update `harnesses.json` with the new harness entry

### Attribution

Harnesses sourced from external repositories must include an attribution block at the top of their `README.md`:

```markdown
> **Attribution:** This harness is sourced from [owner/repo](https://github.com/owner/repo) by [@owner](https://github.com/owner), used under the MIT License. No modifications have been made to the original files.
```

The `author` field in `harnesses.json` should follow the format: `owner (https://github.com/owner/repo)`.
