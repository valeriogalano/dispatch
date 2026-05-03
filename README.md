# dev-updates

Automated weekly digest of GitHub activity across personal projects, saved as Markdown and browsable directly on GitHub.

## How it works

Every Friday at 18:00 UTC a GitHub Actions workflow runs `collect.py`, which:

1. Reads the repo list from `config.txt`
2. Fetches commits from the last N days via the GitHub API
3. Categorises them by [Conventional Commits](https://www.conventionalcommits.org/) prefix
4. Saves the digest to `output/digest-YYYY-MM-DD.md` and commits it back to the repository

## Setup

### 1. Add repos to `config.txt`

```
owner/repo-name | Human Readable Name | tag1, tag2
```

Lines starting with `#` and blank lines are ignored.

### 2. Add the GitHub secret

| Secret | Description |
|---|---|
| `GH_TOKEN` | GitHub personal access token with `repo` (read) scope |

### 3. Enable write permissions for Actions

In the repository settings go to **Settings → Actions → General → Workflow permissions** and enable *Read and write permissions* so the workflow can commit digest files.

## Local usage

```bash
# First time only: create the virtualenv
python -m venv .venv
source .venv/bin/activate
pip install requests

# Run and print digest to stdout (also saves to output/)
GH_TOKEN=ghp_... python collect.py

# Custom time window
GH_TOKEN=ghp_... python collect.py --days 14
```

## Digest categories

| Prefix | Category |
|---|---|
| `feat:` | Added |
| `fix:` | Fixed |
| `BREAKING CHANGE` / `!` | Breaking |
| anything else | Changed |
