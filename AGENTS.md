# AGENTS.md

Repository-specific instructions for AI agents working on Dispatch. They override the
global rules where they conflict — see *Branching* below.

## Branching: commit straight to `main`

The maintainer works **directly on `main`** in this repository: no feature branches, no
pull requests. Commit and push without asking.

This is a deliberate exception to the global `git-workflow` rule that forbids working on
protected branches. It exists because this is a single-author project where a branch adds
ceremony without adding review, and because most commits are automated digest output
pushed by CI.

The two pull requests in the history (#5, #6, 2026-08-04) were one-offs, not a change of
policy. Do not treat them as precedent, and do not propose a branch "just for this one".

External contributions are a different matter: those arrive as pull requests and follow the
normal review flow. The rule above is about the maintainer's own work.

## Language

English — commit messages, PR text, code comments, docstrings and documentation. It matches
the existing README and history. Conversation with the maintainer stays in Italian.

## This repository is not self-contained

The pipeline ends by publishing into **`pensieriincodice-website`**, cloned at
`~/PhpstormProjects/pensieriincodice-website` — note `PhpstormProjects`, not
`PycharmProjects` where Dispatch itself lives.

A bug that looks like a Dispatch bug can therefore have its cause and its fix in the other
repository. This happened on 2026-07-25 with a truncated RSS feed. Before changing anything
here, check whether what is broken is actually produced by the site: posts, feed, Hugo
templates. Tasks about the site belong to the `pensieriincodice-website` Todoist project,
not to this one.

## The `skills/` directory is a submodule

`skills/` is a git submodule pointing at `valeriogalano/agent-skills` and tracking its
`main` branch. **Do not edit anything under `skills/` from here.** Those files belong to the
`agent-skills` repository, which is their single source of truth; editing them through the
submodule creates a detached-HEAD change that is easy to lose.

To change a skill: edit it in `~/PycharmProjects/agent-skills`, commit and push there, then
update the submodule pointer here if the pipeline needs the new version immediately.

Engram's prompt is composed from the skill rather than from a local copy, so a change to
the `engram` skill changes what this pipeline writes.

## History

This project was called **`dev-updates`** until 2026-07-28 (`chore: rename the project to
Dispatch`). GitHub still redirects the old name. References to `dev-updates` in older notes,
tasks or memories mean this repository.
