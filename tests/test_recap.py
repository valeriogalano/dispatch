import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import recap


class SignatureTests(unittest.TestCase):
    def test_nothing_is_signed_and_the_model_is_disclosed_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            digest = out / "digest-2026-07-24.md"
            digest.write_text("# Dev Updates\n\n- qualcosa\n", encoding="utf-8")

            with patch.object(recap, "call_ai", return_value=("gemini-3.8-flash", "Testo del recap.")):
                recap.generate_recap(digest, out, ["telegram", "blog"])

            # Telegram has no template: the disclosure closes the post
            text = (out / "recap-telegram-2026-07-24.md").read_text(encoding="utf-8")
            lines = [line for line in text.splitlines() if line.strip()]
            self.assertEqual("_Generato con gemini-3.8-flash_", lines[-1])
            self.assertNotIn("generato con", text.split("Testo del recap.")[0])

            # the site's template shows the model from the frontmatter: none in the body
            blog = (out / "recap-blog-2026-07-24.md").read_text(encoding="utf-8")
            frontmatter, body = blog.split("---\n\n", 1)
            self.assertIn("curated_by: Engram\n", frontmatter)
            self.assertIn("generated_with: gemini-3.8-flash\n", frontmatter)
            self.assertEqual("Testo del recap.\n", body)

            # The channel shows the author line and the site shows the author box:
            # signing again is noise.
            for name in ("recap-telegram-2026-07-24.md", "recap-blog-2026-07-24.md"):
                self.assertNotIn("— Engram", (out / name).read_text(encoding="utf-8"), name)

            blog = (out / "recap-blog-2026-07-24.md").read_text(encoding="utf-8")
            self.assertIn("author: Engram", blog)


    def test_a_trailer_written_by_the_model_is_replaced_by_the_real_one(self):
        # The skill asks Engram to disclose, but it cannot know which model is
        # running it: it invents the name. Only the code's version stays, whether the
        # model used the old signed wording or the current one.
        for written in (
            "Testo del recap.\n\n— Engram\n\n_Questo testo è stato generato con gpt-4o_",
            "Testo del recap.\n\n_Generato con gpt-4o_",
        ):
            with self.subTest(written=written):
                self._assert_only_the_real_trailer_stays(written)

    def _assert_only_the_real_trailer_stays(self, written):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            digest = out / "digest-2026-07-24.md"
            digest.write_text("# Dev Updates\n\n- qualcosa\n", encoding="utf-8")

            with patch.object(recap, "call_ai", return_value=("gemini-3.8-flash", written)):
                recap.generate_recap(digest, out, ["telegram", "blog"])

            for name in ("recap-telegram-2026-07-24.md", "recap-blog-2026-07-24.md"):
                text = (out / name).read_text(encoding="utf-8")
                self.assertNotIn("gpt-4o", text, name)
                self.assertNotIn("— Engram", text, name)

            telegram = (out / "recap-telegram-2026-07-24.md").read_text(encoding="utf-8")
            self.assertEqual(1, telegram.lower().count("generato con"))
            blog = (out / "recap-blog-2026-07-24.md").read_text(encoding="utf-8")
            self.assertNotIn("generato con", blog.lower())


class TitleTests(unittest.TestCase):
    def test_the_blog_title_spells_the_date_in_italian(self):
        self.assertEqual("Diario di Engram – 9 ottobre 2026", recap.diary_title("2026-10-09"))
        self.assertEqual("Diario di Engram – 1 gennaio 2027", recap.diary_title("2027-01-01"))

    def test_the_file_name_keeps_the_iso_date(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            digest = out / "digest-2026-12-04.md"
            digest.write_text("# Dev Updates\n\n- qualcosa\n", encoding="utf-8")
            with patch.object(recap, "call_ai", return_value=("m", "Testo.")):
                recap.generate_recap(digest, out, ["blog"])

            blog = (out / "recap-blog-2026-12-04.md").read_text(encoding="utf-8")
            self.assertIn('title: "Diario di Engram – 4 dicembre 2026"\n', blog)


def _claude_client(message):
    from unittest.mock import MagicMock
    client = MagicMock()
    client.messages.stream.return_value.__enter__.return_value.get_final_message.return_value = message
    return client


class ClaudeResponseTests(unittest.TestCase):
    def test_a_leading_thinking_block_is_skipped(self):
        # claude-sonnet-5-5 answers with a thinking block first, which has no text:
        # reading content[0].text crashed every attempt.
        from types import SimpleNamespace

        message = SimpleNamespace(stop_reason="end_turn", content=[
            SimpleNamespace(type="thinking"),
            SimpleNamespace(type="text", text=" Testo del recap. "),
        ])
        with patch("anthropic.Anthropic", return_value=_claude_client(message)):
            self.assertEqual("Testo del recap.", recap._call_claude("key", "system", "user"))


class TruncationTests(unittest.TestCase):
    # 2026-10-20: the episode 149 article stopped mid-word at max_tokens, thinking
    # included, and was saved as if complete.
    def test_claude_stopping_at_max_tokens_is_an_error(self):
        from types import SimpleNamespace

        message = SimpleNamespace(stop_reason="max_tokens", content=[
            SimpleNamespace(type="text", text="del panorama del doppia"),
        ])
        with patch("anthropic.Anthropic", return_value=_claude_client(message)):
            with self.assertRaises(recap.Truncated) as cm:
                recap._call_claude("key", "system", "user")
        self.assertEqual("del panorama del doppia", cm.exception.text)

    def test_gemini_stopping_at_max_tokens_is_an_error(self):
        from types import SimpleNamespace
        from unittest.mock import MagicMock

        client = MagicMock()
        client.models.generate_content.return_value = SimpleNamespace(
            text="del panorama del doppia",
            candidates=[SimpleNamespace(finish_reason="MAX_TOKENS")],
        )
        with patch("google.genai.Client", return_value=client):
            with self.assertRaises(recap.Truncated):
                recap._call_gemini("key", "system", "user")

    def test_a_truncated_answer_is_not_retried_nor_failed_over(self):
        # the same request stops at the same place: paying again buys nothing
        calls = []

        def cut(key, system, user):
            calls.append(key)
            raise recap.Truncated("testo a metà")

        env = {"AI_PROVIDER": "anthropic,google", "ANTHROPIC_API_KEY": "k", "GEMINI_API_KEY": "g"}
        with patch.dict("os.environ", env, clear=True), \
                patch.dict(recap._PROVIDERS, {"anthropic": ("ANTHROPIC_API_KEY", "claude-x", cut),
                                              "google": ("GEMINI_API_KEY", "gemini-x", cut)}), \
                patch.object(recap.time, "sleep", side_effect=AssertionError("must not sleep")):
            with self.assertRaises(recap.Truncated) as cm:
                recap.call_ai("system", "user")
        self.assertEqual(["k"], calls)
        self.assertEqual("claude-x", cm.exception.model)


class LinkTests(unittest.TestCase):
    def test_a_link_missing_from_the_digest_is_reduced_to_its_text(self):
        # 2026-09-26: a private repo, listed without a link, got a GitHub URL
        # rebuilt from its name. Only links the digest carries survive.
        written = (
            "[Dispatch](https://github.com/valeriogalano/dispatch) e "
            "[Book Highlighter](https://github.com/valeriogalano/book-highlighter). "
            '[Titolo](https://invented.example "Titolo") ![logo](https://img.example/x.png) '

            "[Articolo](https://pensieriincodice.it/blog/2026-09-26-recap/)"
        )
        digest_text = "## Dispatch\n<https://github.com/valeriogalano/dispatch>\n\n## Book Highlighter\n\n- x\n"

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            digest = out / "digest-2026-09-26.md"
            digest.write_text(digest_text, encoding="utf-8")

            with patch.object(recap, "call_ai", return_value=("gemini-3.8-flash", written)):
                recap.generate_recap(
                    digest, out, ["telegram", "blog"],
                    blog_url="https://pensieriincodice.it/blog/2026-09-26-recap/",
                )

            telegram = (out / "recap-telegram-2026-09-26.md").read_text(encoding="utf-8")
            self.assertIn("[Dispatch](https://github.com/valeriogalano/dispatch)", telegram)
            self.assertIn(" e Book Highlighter.", telegram)
            self.assertNotIn("invented.example", telegram)
            # images are left alone: stripping one would leave a stray "!"
            self.assertIn("![logo](https://img.example/x.png)", telegram)
            self.assertIn("[Articolo](https://pensieriincodice.it/blog/2026-09-26-recap/)", telegram)

            # the blog post links to itself nowhere: blog_url is Telegram's only
            blog = (out / "recap-blog-2026-09-26.md").read_text(encoding="utf-8")
            self.assertNotIn("book-highlighter", blog)
            self.assertIn(" Articolo", blog)


class PromptTests(unittest.TestCase):
    def test_the_prompt_is_composed_from_the_skill_files(self):
        # The voice lives in the skill submodule: a missing checkout must not
        # silently produce a recap written by nobody in particular. Asserted
        # against the files rather than their wording, since the submodule
        # follows agent-skills main and the wording there is free to change.
        for name in ("engram-identita.md", "engram-prosa.md", "roles/recap-settimanale.md"):
            self.assertIn((recap._SKILL / name).read_text(encoding="utf-8"), recap.SYSTEM, name)

    def test_the_prompt_forbids_claims_about_the_past(self):
        # Engram only ever sees one digest: continuity would be invented. This
        # one is deliberately coupled to the skill's wording — dropping the
        # constraint there should turn this red rather than pass unnoticed.
        self.assertIn("fingere di saperlo", recap.SYSTEM)

    def test_an_unknown_role_fails_loudly(self):
        with self.assertRaises(FileNotFoundError):
            recap.engram_system("non-esiste")


class ProviderFailoverTests(unittest.TestCase):
    def test_a_provider_without_its_key_is_skipped_without_retrying(self):
        # a missing key will not appear on the third attempt: no sleeping on it
        calls = []

        def fake_claude(key, system, user):
            calls.append(key)
            return "risposta"

        env = {"AI_PROVIDER": "google,anthropic", "ANTHROPIC_API_KEY": "k"}
        with patch.dict("os.environ", env, clear=True), \
                patch.dict(recap._PROVIDERS, {"anthropic": ("ANTHROPIC_API_KEY", recap.CLAUDE_MODEL, fake_claude)}), \
                patch.object(recap.time, "sleep", side_effect=AssertionError("must not sleep")):
            model, text = recap.call_ai("system", "user")

        self.assertEqual(recap.CLAUDE_MODEL, model)
        self.assertEqual("risposta", text)
        self.assertEqual(["k"], calls)

    def test_all_providers_unusable_raises(self):
        with patch.dict("os.environ", {"AI_PROVIDER": "google"}, clear=True):
            with self.assertRaises(RuntimeError):
                recap.call_ai("system", "user")


if __name__ == "__main__":
    unittest.main()
