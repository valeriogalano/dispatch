import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import article

SCRIPT = '''text: "

## Il tema

###### Nox
Benvenuto Valerio, parliamo di \\"Runtime by Night\\".

Buon ascolto.

Sigla.

###### Valerio
Grazie Nox, ne parlo volentieri insieme a Edoardo.

## Conclusione

Grazie a tutti, ci sentiamo alla prossima puntata.
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
            "## Il tema\n\n"
            '**Nox:** Benvenuto Valerio, parliamo di "Runtime by Night".\n\n'
            "**Valerio:** Grazie Nox, ne parlo volentieri insieme a Edoardo.\n\n"
            "## Conclusione\n\n"
            "Grazie a tutti, ci sentiamo alla prossima puntata.",
            script,
        )


class CheckTests(unittest.TestCase):
    sentence = "Ho parlato con Edoardo di Runtime by Night. "
    script = sentence * 10
    # the role keeps everything that is not listening-only: about the whole script
    faithful = sentence * 10

    def test_a_faithful_article_passes(self):
        self.assertEqual([], article.check(self.faithful, self.script, self.script))

    def test_the_listening_sections_do_not_count_towards_the_length(self):
        # 148 words of script, 40 of them in sections the role drops whole
        script = "## Introduzione\n" + "ciao " * 20 + "\n## Tema\n" + "parlo " * 18 + "\n## Conclusione\n" + "grazie " * 20
        self.assertEqual(20, len(article.without_listening_sections(script).split()))
        self.assertEqual([], article.check("parlo " * 18, script, script))

    def test_each_check_blocks_on_its_own(self):
        for text in (self.sentence * 4, self.sentence * 12):
            with self.subTest(words=len(text.split())):
                self.assertIn("length", article.check(text, self.script, self.script)[0])

        invented = self.faithful + "Ne ho parlato anche con Marco."
        self.assertEqual(["names not in the script: Marco"], article.check(invented, self.script, self.script))

        # 2026-10-20, episode 148: "anni '60" in the script, "anni Sessanta" in the article
        decades = self.faithful + "Succedeva negli anni Sessanta e nel Novecento."
        self.assertEqual([], article.check(decades, self.script, self.script))

        linked = self.faithful + "Vedi https://invented.example/x per altro."
        self.assertEqual(["URLs not in the sources: https://invented.example/x"],
                         article.check(linked, self.script, self.script))


class GenerateTests(unittest.TestCase):
    body = (
        "## Il tema\n\n"
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
                "curated_by: Engram\ngenerated_with: claude-sonnet-5-5\n---\n\n## Il tema"
            ))
            # the site's template looks the episode page up by number: a quoted
            # "150" finds nothing and the link under the title disappears
            self.assertEqual(150, article.yaml.safe_load(text.split("---\n")[1])["episode"])
            self.assertIn("[Runtime by Night](https://runtimeradio.com/podcast/runtime-by-night)", text)
            self.assertNotIn("gpt-4o", text)
            # the site links the episode from the disclosure under the title
            self.assertTrue(text.endswith("ne parlo volentieri insieme a Edoardo.\n"))

            # an article is paid for once
            self.assertEqual([], article.missing_episodes(Path(tmp) / "website", out, since=0))

    def test_a_truncated_answer_is_rejected_even_within_the_length_bounds(self):
        # 2026-10-20: episode 149 stopped mid-word at 0.89 of the script, inside
        # the length bounds, and was published as complete
        cut = article.Truncated(self.body.split("_Generato")[0].rstrip() + " del doppia", "claude-sonnet-5-5")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "output"
            out.mkdir()
            with patch.object(article, "call_ai", side_effect=cut):
                self.assertFalse(article.generate_article(website(tmp), 150, out))

            self.assertFalse((out / "article-150.md").exists())
            rejected = (out / "article-150.rejected.md").read_text(encoding="utf-8")
            self.assertIn("output limit", rejected)
            self.assertIn("del doppia", rejected)

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


class ExportImportTests(unittest.TestCase):
    # the backlog is written in a Claude Code session, not through the API: the
    # session gets exactly the messages call_ai would send, and its text goes
    # through exactly what a model answer goes through
    def test_the_exported_prompt_is_what_call_ai_receives(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, out = website(tmp), Path(tmp) / "prompt"
            article.export_prompt(root, 150, out)

            with patch.object(article, "call_ai", return_value=("m", GenerateTests.body)) as call:
                article.generate_article(root, 150, Path(tmp))

            system, user = call.call_args.args
            self.assertEqual(system.encode("utf-8"), (out / "system.md").read_bytes())
            self.assertEqual(user.encode("utf-8"), (out / "user.md").read_bytes())

    def test_an_imported_text_is_checked_and_saved_like_a_model_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, out = website(tmp), Path(tmp) / "output"
            out.mkdir()
            text = Path(tmp) / "body.md"
            text.write_text(GenerateTests.body, encoding="utf-8")

            self.assertTrue(article.import_text(root, 150, text, "claude-sonnet-5-5 (Claude Code)", out))

            saved = (out / "article-150.md").read_text(encoding="utf-8")
            self.assertIn("generated_with: claude-sonnet-5-5 (Claude Code)\n", saved)
            self.assertNotIn("gpt-4o", saved)  # the trailer is stripped as for the API

            # a published article is never overwritten by a second import
            text.write_text("Corto.", encoding="utf-8")
            self.assertTrue(article.import_text(root, 150, text, "m", out))
            self.assertEqual(saved, (out / "article-150.md").read_text(encoding="utf-8"))

    def test_an_imported_text_too_short_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root, out = website(tmp), Path(tmp) / "output"
            out.mkdir()
            text = Path(tmp) / "body.md"
            text.write_text("**Nox:** Benvenuto Valerio.", encoding="utf-8")

            self.assertFalse(article.import_text(root, 150, text, "m", out))

            self.assertFalse((out / "article-150.md").exists())
            self.assertIn("length", (out / "article-150.rejected.md").read_text(encoding="utf-8"))
