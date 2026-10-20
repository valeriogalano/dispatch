# Dispatch

Where Engram, the voice of the generated texts of Pensieri in codice, writes for the blog and for Telegram.

- A **weekly digest** of GitHub activity across personal projects, saved as Markdown and browsable directly on GitHub, turned into two AI-generated recaps: one for Telegram and one for the blog.
- An **article for each podcast episode**, adapted from the episode script and published on the blog under Valerio's name.

## Features

- **Automated Collection**: Fetches commits from multiple repositories using the GitHub API and links each public project section to the repository page.
- **Smart Categorization**: Groups commits by [Conventional Commits](https://www.conventionalcommits.org/) prefixes (feat, fix, etc.).
- **AI-Powered Summaries**: Uses Google Gemini (`gemini-3.8-flash`), with Anthropic Claude (`claude-sonnet-5-5`) as fallback, to generate:
  - **Telegram Posts**: Schematic, emoji-rich updates tailored for technical channels.
  - **Blog Articles**: Narrative, SEO-friendly posts with Hugo frontmatter, which names the model in `generated_with` for the site to show; Telegram posts close with the disclosure instead.
- **Multi-Platform Publishing**:
  - Automatically opens and merges PRs on a Hugo website.
  - Sends formatted messages to Telegram via Bot API.
- **Pipeline Noise Filtered**: Commits made by CI bots and the merges of generated recap PRs are left out of the digest, so the recap never reports the pipeline's own output as work.
- **Contributor Attribution**: Recognizes and credits external human contributors in both the digest and the recaps.
- **Workflow Automation**: Fully integrated GitHub Actions chain with retry logic for API stability.

## How it works

### Weekly digest (`weekly-digest.yml`)

Every Friday at 18:00 UTC:

1. `collect.py` reads `config.txt`, fetches commits from the last N days via the GitHub API, categorises them by [Conventional Commits](https://www.conventionalcommits.org/) prefix, links public project sections to the repository page, appends any manual note from `manual/` falling in the window, and saves `output/digest-YYYY-MM-DD.md`. If the period is empty it writes no file at all, and the chain stops without failing
2. `recap.py` reads the digest and calls Gemini to produce:
   - `output/recap-telegram-YYYY-MM-DD.md` — schematic post ready to publish to Telegram
   - `output/recap-blog-YYYY-MM-DD.md` — narrative post with Hugo frontmatter for the Pensieri in codice blog

   Any markdown link whose URL is not in the digest is reduced to its text: the model tends to rebuild GitHub URLs from project names, private repositories included.

All files are committed back to the repository automatically.

The chain runs again every hour between 19:00 and 22:00 UTC on Friday, to recover from a failed run without a manual re-run. Every stage is a no-op once it went through: a scheduled run that finds a digest dated today or yesterday does not collect again (GitHub may start the last retry after midnight UTC, under Saturday's date), the recap workflows skip the AI call when the file for that date exists, the website publication reuses the open PR, and `publish_telegram.py` records a marker in `output/sent/` and refuses to send the same recap twice.

### Episode articles (`generate-article.yml`)

`article.py` adapts the script of an episode into a blog article. It reads `data/scripts/PICNNN.yml` and the frontmatter of `content/podcast/NNN.md` from a checkout of `pensieriincodice-website`, then:

1. cleans the script without the AI: cues like `Sigla.` and `Buon ascolto.` go, and each `###### Name` header becomes `**Name:**` opening that speaker's turn;
2. asks Engram, with the `articolo-episodio` role, to turn the spoken text into written prose, through the same providers as the recaps;
3. writes the frontmatter (title, date and tags of the episode, `author: Valerio Galano`, `episode`, `curated_by`, `generated_with`) and a closing link to the episode, and reduces any link whose URL is not in the script or the episode `sources` to its text.

Three checks block the article: its length must stay within 0.7-1.15 of the script, every proper noun must appear in the script, every URL must come from the script or the `sources`. A blocked article is saved as `output/article-NNN.rejected.md` with the reasons on top, the run goes red, and the episode is not retried until the file is removed or the episode is requested by number.

The workflow runs on a `repository_dispatch` of type `episode-script` from the website (`{"episode": NNN}`), by hand with a list of episode numbers, and every day at 03:00 UTC, before the website build, for the newest episode with a script and no article. The daily run only looks at episodes from 151 on (`FIRST_NEW_EPISODE`, overridable with `--since`): the older ones are a backfill, run by hand by listing their numbers. It commits the article and opens a PR on the website with `content/blog/episodio-NNN.md`; the PR is merged by hand. The provider order comes from the `ARTICLE_AI_PROVIDER` variable, falling back to `AI_PROVIDER`.

```bash
python article.py --website ~/PhpstormProjects/pensieriincodice-website 150
python article.py --website ~/PhpstormProjects/pensieriincodice-website --missing --limit 1
```

### Manual updates (`manual/`)

Things done outside git — a podcast episode, an article, a release — go in `manual/YYYY-MM-DD.md`, named with the date they happened. Notes falling inside the digest window are appended to the digest under `## Manual updates` as raw material, and interpreted by the AI together with the commits. See `manual/README.md`.

### Workflow Chain

The project uses a chain of workflows to automate the entire process:
1. **Weekly Dev Digest**: Collects commits and saves the digest.
2. **Generate Recap for Blog**: Triggered after the digest is created.
3. **Generate Recap for Telegram**: Triggered after the blog recap is ready (so it can include the blog post URL).
4. **Publish Recap to Website**: Triggered after the blog recap is generated. Copies the file to the website repo, opens and merges a PR.
5. **Publish Recap to Telegram**: Triggered after the Telegram recap is generated. Sends the message via bot.

Both recap workflows are thin callers of `_generate-recap.yml`, which holds the shared steps and takes the format as an input. **Tests** runs the unit tests on every push and pull request.

Digests, recaps and sent markers older than 52 weeks are pruned from `output/` by the weekly job; git history keeps them.

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
| `ANTHROPIC_API_KEY` | Secret | Anthropic API key, used as fallback when Gemini fails |
| `AI_PROVIDER` | Variable | Optional, comma-separated provider order (default `google,anthropic`) |
| `ARTICLE_AI_PROVIDER` | Variable | Optional, provider order for the episode articles only (default: `AI_PROVIDER`) |
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
# First time only: fetch the skills submodule and create the virtualenv
git submodule update --init --remote
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`recap.py` composes Engram's prompt from `skills/engram/` at import time, so the
submodule must be checked out or the script will not start. To change how Engram
writes, edit the skill — never the prompt in `recap.py`, which no longer holds
one.

The submodule follows `agent-skills` **main** rather than a pinned commit
(`--remote`): editing Engram changes how Engram writes everywhere, with nothing
to bump here. Run `git submodule update --remote` to pick up skill changes
locally. `agent-skills` is private, so a clone needs a token that can read it.

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
