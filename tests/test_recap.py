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


class PromptTests(unittest.TestCase):
    def test_both_prompts_forbid_claims_about_the_past(self):
        # Engram only ever sees one digest: continuity would be invented.
        for prompt in (recap.TELEGRAM_SYSTEM, recap.BLOG_SYSTEM):
            self.assertIn("Sei Engram.", prompt)
            self.assertIn("non deve fingere di saperlo", prompt)


if __name__ == "__main__":
    unittest.main()
