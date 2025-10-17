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
   - Configure `transform.yaml` for your transformation pipeline
   - Implement transformation logic in `transform.py`
3. **Testing**: Add tests in `tests/` directory
4. **Documentation**: Update `README.md` with project-specific details

## AI Assistant Guidelines

When helping with this project:

- **Understand the ingest context**: This processes biological/biomedical data into knowledge graphs
- **Koza expertise**: Familiar with Koza transformation patterns and YAML configuration
- **Data validation**: Always validate YAML config files after changes
- **Testing**: Run `just test` and `just check-config` after modifications
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