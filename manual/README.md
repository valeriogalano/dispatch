# Manual updates

This is where things that have no commit behind them go: a podcast episode, an
article, a release, anything done and not tracked in git.

One file per day, named with the date the thing happened:

```
manual/2026-07-24.md
```

Write freely, the way you would tell a person. The text does not reach the recap
as is: `collect.py` appends it to the digest under `## Manual updates` and the AI
interprets it together with the commits.

Only files whose date falls inside the digest window are collected. Notes stay
here after publication: they are the archive of what git does not know.

This README is ignored: its name is not a date.
