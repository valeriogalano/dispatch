import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import article

SCRIPT = '''text: "

## Introduzione

###### Nox
Benvenuto Valerio, parliamo di \\"Runtime by Night\\".

Buon ascolto.

Sigla.

###### Valerio
Grazie Nox, ne parlo volentieri insieme a Edoardo.
"
'''

EPISODE = '''---
authors: [ Valerio Galano ]
title: "Un episodio (con Nox)"
tags: [ podcasting, intelligenza artificiale ]
number: 150
date: 2026-06-21T04:00:00+02:00
url: /episodes/150-un-episodio
sources:
  - url: https://runtimeradio.com/podcast/runtime-by-night
    title: Runtime by Night
---

Descrizione.
'''


def website(tmp: str) -> Path:
    root = Path(tmp) / "website"
    (root / "data" / "scripts").mkdir(parents=True)
    (root / "content" / "podcast").mkdir(parents=True)
    (root / "data" / "scripts" / "PIC150.yml").write_text(SCRIPT, encoding="utf-8")
    (root / "content" / "podcast" / "150.md").write_text(EPISODE, encoding="utf-8")
    return root


class ScriptTests(unittest.TestCase):
    def test_spoken_cues_go_and_speakers_open_their_turn(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = article.clean_script(article.read_script(website(tmp) / "data" / "scripts" / "PIC150.yml"))

        self.assertEqual(
            "## Introduzione\n\n"
            '**Nox:** Benvenuto Valerio, parliamo di "Runtime by Night".\n\n'
            "**Valerio:** Grazie Nox, ne parlo volentieri insieme a Edoardo.",
            script,
        )


class CheckTests(unittest.TestCase):
    script = "Ho parlato con Edoardo di Runtime by Night. " * 10

    def test_a_faithful_article_passes(self):
        self.assertEqual([], article.check(self.script, self.script, self.script))

    def test_each_check_blocks_on_its_own(self):
        problems = article.check(self.script[:40], self.script, self.script)
        self.assertIn("length", problems[0])

        invented = self.script + "Ne ho parlato anche con Marco."
        self.assertEqual(["names not in the script: Marco"], article.check(invented, self.script, self.script))

        linked = self.script + "Vedi https://invented.example/x per altro."
        self.assertEqual(["URLs not in the sources: https://invented.example/x"],
                         article.check(linked, self.script, self.script))


class GenerateTests(unittest.TestCase):
    body = (
        "## Introduzione\n\n"
        "**Nox:** Benvenuto Valerio, parliamo di [Runtime by Night](https://runtimeradio.com/podcast/runtime-by-night).\n\n"
        "**Valerio:** Grazie Nox, ne parlo volentieri insieme a Edoardo.\n\n"
        "_Generato con gpt-4o_"
    )

    def test_the_article_carries_the_episode_and_the_model(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "output"
            out.mkdir()
            with patch.object(article, "call_ai", return_value=("claude-sonnet-5-5", self.body)):
                self.assertTrue(article.generate_article(website(tmp), 150, out))

            text = (out / "article-150.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith(
                '---\ntitle: "Un episodio (con Nox)"\n'
                "date: 2026-06-21T04:00:00+02:00\n"
                'tags: ["podcasting", "intelligenza artificiale"]\n'
                "type: blog\nauthor: Valerio Galano\nepisode: 150\n"
                "curated_by: Engram\ngenerated_with: claude-sonnet-5-5\n---\n\n## Introduzione"
            ))
            self.assertIn("[Runtime by Night](https://runtimeradio.com/podcast/runtime-by-night)", text)
            self.assertNotIn("gpt-4o", text)
            self.assertTrue(text.endswith("[episodio 150 di Pensieri in codice](/episodes/150-un-episodio).\n"))

            # an article is paid for once
            self.assertEqual([], article.missing_episodes(Path(tmp) / "website", out, since=0))

    def test_a_failed_check_keeps_the_text_aside_and_publishes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "output"
            out.mkdir()
            with patch.object(article, "call_ai", return_value=("m", self.body + "\n\nCiao da Marco.")):
                self.assertFalse(article.generate_article(website(tmp), 150, out))

            self.assertFalse((out / "article-150.md").exists())
            self.assertIn("Marco", (out / "article-150.rejected.md").read_text(encoding="utf-8"))
            self.assertEqual([], article.missing_episodes(Path(tmp) / "website", out, since=0))


class MissingTests(unittest.TestCase):
    def test_the_nightly_run_leaves_the_backlog_alone(self):
        # the 82 older episodes are a backfill run by hand: only new ones count
        with tempfile.TemporaryDirectory() as tmp:
            root = website(tmp)
            for n in (149, 151, 152):
                (root / "data" / "scripts" / f"PIC{n}.yml").write_text(SCRIPT, encoding="utf-8")
                (root / "content" / "podcast" / f"{n}.md").write_text(EPISODE, encoding="utf-8")
            out = Path(tmp) / "output"
            out.mkdir()

            self.assertEqual([152, 151], article.missing_episodes(root, out))
            self.assertEqual([152, 151, 150, 149], article.missing_episodes(root, out, since=0))
