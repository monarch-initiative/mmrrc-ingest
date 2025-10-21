# Ingest-specific recipes

# Clean up build artifacts
clean:
  rm -f `find . -type f -name '*.py[co]' `
  rm -rf `find . -name __pycache__` \
    .venv .ruff_cache .pytest_cache **/.ipynb_checkpoints

# Clean up generated files
clobber: clean
  rm -rf output/
  rm -rf data/

# Run the full ingest pipeline
run: download transform

# Check ingest configuration files
check-config:
  uv run python -c "import yaml; yaml.safe_load(open('src/mmrrc_ingest/download.yaml')); print('download.yaml is valid')"
  uv run python -c "import yaml; yaml.safe_load(open('src/mmrrc_ingest/metadata.yaml')); print('metadata.yaml is valid')"
  uv run python -c "import yaml; from pydantic import TypeAdapter; from koza.model.koza import KozaConfig; TypeAdapter(KozaConfig).validate_python(yaml.safe_load(open('src/mmrrc_ingest/genotype.yaml'))); print('genotype.yaml is valid')"
  uv run python -c "import yaml; from pydantic import TypeAdapter; from koza.model.koza import KozaConfig; TypeAdapter(KozaConfig).validate_python(yaml.safe_load(open('src/mmrrc_ingest/genotype_to_phenotype.yaml'))); print('genotype_to_phenotype.yaml is valid')"
  uv run python -c "import yaml; from pydantic import TypeAdapter; from koza.model.koza import KozaConfig; TypeAdapter(KozaConfig).validate_python(yaml.safe_load(open('src/mmrrc_ingest/allele_to_genotype.yaml'))); print('allele_to_genotype.yaml is valid')"
