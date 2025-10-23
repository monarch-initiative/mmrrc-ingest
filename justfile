# ============ Hint for for Windows Users ============

# On Windows the "sh" shell that comes with Git for Windows should be used.
# If it is not on path, provide the path to the executable in the following line.
#set windows-shell := ["C:/Program Files/Git/usr/bin/sh", "-cu"]

# ============ Variables used in recipes ============

# Set shebang line for cross-platform Python recipes (assumes presence of launcher on Windows)
shebang := if os() == 'windows' {
  'py'
} else {
  '/usr/bin/env python3'
}

# ============== Project recipes ==============

# List all commands as default command. The prefix "_" hides the command.
_default: _status
    @just --list

# Initialize a new project (use this for projects not yet under version control)
[group('project management')]
setup: _git-init _ai-instructions install _git-add
  git commit -m "Initialise git with minimal project" -a

# Install project dependencies
[group('project management')]
install:
  uv sync --group dev

# Update project template
[group('project management')]
update:
  uvx --with jinja2-time copier update --trust --skip-answered

# Run all tests
[group('ingest development')]
test: pytest mypy lint

test-full: test pytest-integration

pytest:
  uv run pytest

# include integration tests
pytest-integration:
	uv run pytest -m ""

doctest:
  uv run pytest --doctest-modules src

mypy:
  uv run mypy src tests

# Check code for issues (report only)
lint:
	uv run ruff check .

# Auto-fix code formatting and style issues
format:
	uv run ruff format .
	uv run ruff check --fix .

# Download data for ingest
[group('ingest operations')]
download:
  uv run mmrrc-ingest download

# Run ingest transformation
[group('ingest operations')]
transform: download
  uv run mmrrc-ingest transform
  uv run python scripts/generate-report.py

# Generate documentation
[group('documentation')]
docs-build:
  uv run mkdocs build

docs-serve:
  uv run mkdocs serve

# ============== Hidden internal recipes ==============

_status:
  @echo "OK"

# Run documentation server
_serve:
  uv run mkdocs serve

# Initialize git repository
_git-init:
  git init

# Add files to git
_git-add:
  git add .

# Commit files to git
_git-commit:
  git commit -m 'chore: just setup was run' -a

# Show git status
_git-status:
  git status

goosehints:
  [ -f .goosehints ] || ln -s CLAUDE.md .goosehints

copilot-instructions:
  [ -f .github/copilot-instructions.md ] || cd .github && ln -s ../CLAUDE.md copilot-instructions.md

_ai-instructions: goosehints copilot-instructions

gh-add-topics:
  gh repo edit --add-topic "mmrrc-ingest,monarchinitiative,dataingest,koza"

gh-add-secrets:
  gh secret set PAT_FOR_PR --body "$PAT_FOR_PR"
  gh secret set ANTHROPIC_API_KEY --body "$ANTHROPIC_API_KEY"
  gh secret set OPENAI_API_KEY --body "$OPENAI_API_KEY"
  gh secret set CBORG_API_KEY --body "$CBORG_API_KEY"
  gh secret set CLAUDE_CODE_OATH_TOKEN --body "$CLAUDE_CODE_OATH_TOKEN"

gh-invite-the-dragon:
  gh api repos/monarch-initiative/mmrrc-ingest/collaborators/dragon-ai-agent -X PUT -f permission=push

# Migration helper for cruft users
_migrate_from_cruft:
  #!/usr/bin/env bash
  set -euo pipefail
  
  echo "🚀 Migrating from cruft to copier..."
  
  # Remove cruft configuration
  if [ -f .cruft.json ]; then
    echo "✅ Removing .cruft.json"
    rm .cruft.json
  fi
  
  # Check for old Makefile
  if [ -f Makefile ]; then
    echo "ℹ️  Found old Makefile - consider reviewing custom rules"
    echo "   Add custom rules to project.justfile instead"
  fi
  
  # Inform about command changes
  echo ""
  echo "📝 Command Changes:"
  echo "   make install  → just install"
  echo "   make test     → just test" 
  echo "   make download → just download"
  echo "   make run      → just transform"
  echo "   cruft update  → copier update"
  echo ""
  echo "✨ Migration complete!"
  echo "   Try: just install && just test"
  echo "   See MIGRATION_FROM_CRUFT.md for details"

# ============== Include project-specific recipes ==============

import? "project.justfile"