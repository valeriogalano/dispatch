# dev-updates

Automated weekly digest of GitHub activity across personal projects, saved as Markdown and browsable directly on GitHub.
After the digest is collected, two AI-generated recaps are produced via Gemini: one for Telegram and one for the Pensieri in codice blog.

## Features

- **Automated Collection**: Fetches commits from multiple repositories using the GitHub API and links each public project section to the repository page.
- **Smart Categorization**: Groups commits by [Conventional Commits](https://www.conventionalcommits.org/) prefixes (feat, fix, etc.).
- **AI-Powered Summaries**: Uses Google Gemini (`gemini-3-flash-preview`) to generate:
  - **Telegram Posts**: Schematic, emoji-rich updates tailored for technical channels.
  - **Blog Articles**: Narrative, SEO-friendly posts with Hugo frontmatter.
- **Multi-Platform Publishing**:
  - Automatically opens and merges PRs on a Hugo website.
  - Sends formatted messages to Telegram via Bot API.
- **Contributor Attribution**: Recognizes and credits external human contributors in both the digest and the recaps.
- **Workflow Automation**: Fully integrated GitHub Actions chain with retry logic for API stability.

## How it works

### Weekly digest (`weekly-digest.yml`)

Every Friday at 18:00 UTC:

1. `collect.py` reads `config.txt`, fetches commits from the last N days via the GitHub API, categorises them by [Conventional Commits](https://www.conventionalcommits.org/) prefix, links public project sections to the repository page, appends any manual note from `manual/` falling in the window, and saves `output/digest-YYYY-MM-DD.md`. If the period is empty it writes no file at all, and the chain stops without failing
2. `recap.py` reads the digest and calls Gemini to produce:
   - `output/recap-telegram-YYYY-MM-DD.md` — schematic post ready to publish to Telegram
   - `output/recap-blog-YYYY-MM-DD.md` — narrative post with Hugo frontmatter for the Pensieri in codice blog

All files are committed back to the repository automatically.

The chain runs again every hour between 19:00 and 22:00 UTC on Friday, to recover from a failed run without a manual re-run. Every stage is a no-op once it went through: the recap workflows skip the AI call when the file for that date exists, the website publication reuses the open PR, and `publish_telegram.py` records a marker in `output/sent/` and refuses to send the same recap twice.

### Manual updates (`manual/`)

Things done outside git — a podcast episode, an article, a release — go in `manual/YYYY-MM-DD.md`, named with the date they happened. Notes falling inside the digest window are appended to the digest as raw material and interpreted by the AI together with the commits. See `manual/README.md`.

### Workflow Chain

The project uses a chain of workflows to automate the entire process:
1. **Weekly Dev Digest**: Collects commits and saves the digest.
2. **Generate Recap for Blog**: Triggered after the digest is created.
3. **Generate Recap for Telegram**: Triggered after the blog recap is ready (so it can include the blog post URL).
4. **Publish Recap to Website**: Triggered after the blog recap is generated. Copies the file to the website repo, opens and merges a PR.
5. **Publish Recap to Telegram**: Triggered after the Telegram recap is generated. Sends the message via bot.

### Manual Triggers

All workflows can be triggered manually via the "Actions" tab:

- **Generate Recap for Telegram**: Accepts an optional comma-separated list of digest dates (e.g. `2026-05-03,2026-05-08`); if empty, processes the latest digest.
- **Generate Recap for Blog**: Same input as above.
- **Publish to Telegram**: Reads the recap Telegram file for the given date and sends it to the configured Telegram chat.
- **Publish to website**: Copies the recap blog file for the given date to `pensieriincodice-website` and merges it into `main`.

## Setup

### 1. Add repos to `config.txt`

```
owner/repo-name | Human Readable Name
codeberg:owner/repo-name | Human Readable Name
```

The optional `host:` prefix supports `codeberg` (public repos only, no token needed); the default is GitHub. Lines starting with `#` and blank lines are ignored.

### 2. Add secrets and variables to the repository

| Secret/Variable | Type | Description |
|---|---|---|
| `GH_TOKEN` | Secret | GitHub personal access token with `repo` scope (read for digest, write for website PR) |
| `GEMINI_API_KEY` | Secret | Google Gemini API key |
| `TELEGRAM_BOT_TOKEN` | Secret | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Variable | Telegram chat/channel ID where the recap is published |

### 3. Enable write permissions for Actions

In the repository settings go to **Settings → Actions → General → Workflow permissions** and enable *Read and write permissions* so the workflow can commit digest files.

## Local usage

Copy `.env` and fill in your keys:

```bash
cp .env.example .env  # fill in the values
```

```bash
# First time only: create the virtualenv
python -m venv .venv
source .venv/bin/activate
pip install requests google-genai
```

```bash
# Load env vars and run the full pipeline
export $(cat .env | xargs)

# Collect commits (saves output/digest-YYYY-MM-DD.md)
python collect.py --days 7

# Generate recaps from the latest digest (saves recap-telegram-* and recap-blog-*)
python recap.py --format telegram --format blog
```

Naming convention in `output/`:

- `digest-YYYY-MM-DD.md`
- `recap-blog-YYYY-MM-DD.md`
- `recap-telegram-YYYY-MM-DD.md`

### Individual options

```bash
# Custom time window for collect.py
python collect.py --days 14 --until 2026-05-20

# Custom output directory
python collect.py --output-dir ./my-digests
python collect.py --manual-dir ./my-notes
python recap.py --output-dir ./my-digests

# Generate only Telegram recap with a specific blog URL
python recap.py --format telegram --blog-url https://example.com/post
```

## Digest categories

| Prefix | Category |
|---|---|
| `feat:` | Added |
| `fix:` | Fixed |
| `BREAKING CHANGE` / `!` | Breaking |
| anything else | Changed |
