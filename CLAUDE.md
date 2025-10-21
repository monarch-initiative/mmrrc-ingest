# Claude Code Instructions for MMRRC Ingest

This is a **Monarch Initiative data ingest project** using Koza for data transformations.

## Project Structure

- `src/mmrrc-ingest/download.yaml` - Defines data sources to download
- `src/mmrrc-ingest/transform.yaml` - Koza transformation configuration
- `src/mmrrc-ingest/metadata.yaml` - Project metadata 
- `src/mmrrc-ingest/transform.py` - Python transformation logic
- `src/mmrrc-ingest/cli.py` - Command-line interface

## Key Commands

```bash
# Setup project
just setup

# Download data
just download  # or: uv run mmrrc-ingest download

# Run transformation  
just transform  # or: uv run mmrrc-ingest transform

# Run tests
just test

# Check configuration files
just check-config
```

## Development Workflow

1. **Data Sources**: Update `download.yaml` with your data source URLs and metadata
2. **Transformations**:
   - Configure `transform.yaml` for your transformation pipeline (uses Koza 2.x nested format)
   - Implement transformation logic in `transform.py`
3. **Testing**: Add tests in `tests/` directory
4. **Documentation**: Update `README.md` with project-specific details

## Koza Transform Patterns (Important!)

### Configuration Structure (Koza 2.x)
Use the nested `reader`/`transform`/`writer` structure in YAML configs:

```yaml
name: "my_transform"

reader:
  format: "csv"
  files: ["data.csv"]
  delimiter: ","

transform:
  code: "./transform.py"

writer:
  node_properties: [...]
  min_node_count: 100
```

### Transform Functions Must Return Lists
**CRITICAL**: All transform functions MUST return a list, never None or bare entities:

```python
@koza.transform_record()
def transform_record(koza_transform: KozaTransform, row: dict[str, Any]) -> list[Entity]:
    if not row.get('required_field'):
        return []  # Return empty list, NOT None

    entity = Entity(...)
    return [entity]  # Return list, NOT bare entity
```

### Type Annotations
Add proper type hints to transform functions:

```python
from typing import Any
from koza import KozaTransform

@koza.transform_record()
def transform_record(koza_transform: KozaTransform, row: dict[str, Any]) -> list[Entity]:
    ...
```

### Multiple Transforms
For projects with multiple transforms:
- Create separate YAML files (e.g., `genotype.yaml`, `phenotype.yaml`)
- Each needs its own transform code file
- Update justfile to run all transforms

## AI Assistant Guidelines

When helping with this project:

- **Understand the ingest context**: This processes biological/biomedical data into knowledge graphs
- **Koza 2.x patterns**: Use nested config structure (reader/transform/writer) and list returns
- **Type annotations**: Always include proper type hints for mypy compatibility
- **Data validation**: Run `just check-config` which validates with Pydantic models
- **Testing**: Run `just test` after modifications
- **Dependencies**: Use uv for package management, maintain compatibility with existing Koza/KGX ecosystem

## File Editing Priorities

1. **High priority**: `download.yaml`, `transform.yaml`, `transform.py` - core ingest logic
2. **Medium priority**: `metadata.yaml`, CLI commands, tests
3. **Low priority**: Documentation, GitHub workflows (unless specifically requested)

## Common Tasks

- Adding new data sources → Update `download.yaml`
- Changing transformation logic → Update `transform.py` and `transform.yaml`  
- Adding CLI commands → Extend `cli.py`
- Pipeline debugging → Check Koza logs, validate YAML syntax

Remember: This project transforms raw biological data into standardized knowledge graph formats (Biolink Model).