# List available commands.
default:
    @just --list

# Run local lint checks.
lint: lint-python lint-nix lint-yaml lint-markdown lint-actions lint-skills

# Check Python files.
lint-python:
    git ls-files -z --cached --others --exclude-standard -- '*.py' | xargs -0 ruff check

# Check the flake and Nix files.
lint-nix:
    #!/usr/bin/env bash
    set -euo pipefail
    log=$(mktemp)
    trap 'rm -f "$log"' EXIT
    nix --option warn-dirty false flake check --all-systems --show-trace --print-build-logs 2>&1 | tee "$log"
    if grep -Ei '(^|[^[:alpha:]])warning:' "$log"; then
        echo 'Nix emitted one or more warnings' >&2
        exit 1
    fi
    git ls-files -z --cached --others --exclude-standard -- '*.nix' | xargs -0 nixfmt --check
    statix check .
    deadnix --fail .

# Check YAML files.
lint-yaml:
    git ls-files -z --cached --others --exclude-standard -- '*.yml' '*.yaml' | xargs -0 yamllint

# Check Markdown, excluding generated badges.
lint-markdown:
    git ls-files -z --cached --others --exclude-standard -- '*.md' ':!:my-badges/**' | xargs -0 markdownlint-cli2

# Check GitHub Actions workflows.
lint-actions:
    actionlint -color

# Validate agent skills with the same pinned tools as CI.
lint-skills:
    #!/usr/bin/env bash
    set -euo pipefail
    for dir in .agents/skills/*/; do
        uvx --from 'git+https://github.com/agentskills/agentskills.git@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref' skills-ref validate "$dir"
    done
    npx --yes skill-check@1.2.0 check --no-security-scan .agents/skills

# Run Python unit tests.
test:
    python3 -m unittest discover -s .github/scripts -p 'test_*.py'
