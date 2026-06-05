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

1. Create a new folder in `/harnesses/<harness-name>/`
2. Add `config.json` with metadata
3. Add template files (`.yaml`, `.json`, etc.)
4. Update `harnesses.json` with the new harness entry
