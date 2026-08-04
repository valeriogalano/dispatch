import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import recap


class SignatureTests(unittest.TestCase):
    def test_only_the_blog_is_signed_and_the_disclosure_closes_both(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            digest = out / "digest-2026-07-24.md"
            digest.write_text("# Dev Updates\n\n- qualcosa\n", encoding="utf-8")

            with patch.object(recap, "call_ai", return_value=("gemini-3.5-flash", "Testo del recap.")):
                recap.generate_recap(digest, out, ["telegram", "blog"])

            for name in ("recap-telegram-2026-07-24.md", "recap-blog-2026-07-24.md"):
                text = (out / name).read_text(encoding="utf-8")
                lines = [line for line in text.splitlines() if line.strip()]
                self.assertEqual("_Questo testo è stato generato con gemini-3.5-flash_", lines[-1], name)
                self.assertNotIn("generato con", text.split("Testo del recap.")[0], name)

            # On Telegram the channel already shows Engram as the sender: signing again is noise.
            telegram = (out / "recap-telegram-2026-07-24.md").read_text(encoding="utf-8")
            self.assertNotIn("— Engram", telegram)

            blog = (out / "recap-blog-2026-07-24.md").read_text(encoding="utf-8")
            self.assertEqual("— Engram", [l for l in blog.splitlines() if l.strip()][-2])
            self.assertIn("author: Engram", blog)


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
