# Koza Ingest

This is a Koza ingest repository for transforming biological/biomedical data into Biolink model format.

## Project Structure

- `download.yaml` - Configuration for downloading source data
- `src/` - Transform code and configuration
  - `*.py` / `*.yaml` pairs - Transform code and koza config for each ingest
- `scripts/` - Preprocessing scripts
  - `preprocess.py` - DuckDB-based normalization of MMRRC catalog data
- `tests/` - Unit tests for transforms
- `output/` - Generated nodes and edges (gitignored)
- `data/` - Downloaded source data (gitignored)

## Key Commands

- `just download` - Download source data
- `just preprocess` - Preprocess raw data into normalized CSVs
- `just transform-all` - Run all transforms
- `just transform <name>` - Run specific transform
- `just test` - Run tests

## Adding New Ingests

When adding a new ingest:
1. Add download configuration to `download.yaml`
2. Create `src/<ingest_name>.py` with transform code
3. Create `src/<ingest_name>.yaml` with koza configuration
4. Add `<ingest_name>` to TRANSFORMS list in justfile
5. Create tests in `tests/test_<ingest_name>.py`

## Skills

- `.claude/skills/create-koza-ingest.md` - Create new koza ingests
- `.claude/skills/update-template.md` - Update to latest template version
