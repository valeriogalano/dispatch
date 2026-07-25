import unittest

import publish_telegram


class MarkdownToTelegramHtmlTests(unittest.TestCase):
    def test_link_becomes_an_anchor(self):
        result = publish_telegram.markdown_to_telegram_html("Vedi [Dev updates](https://github.com/owner/repo)")
        self.assertEqual('Vedi <a href="https://github.com/owner/repo">Dev updates</a>', result)

    def test_query_string_ampersand_stays_escaped_inside_the_href(self):
        result = publish_telegram.markdown_to_telegram_html("[x](https://e.it/?a=1&b=2)")
        self.assertEqual('<a href="https://e.it/?a=1&amp;b=2">x</a>', result)

    def test_quote_in_url_cannot_break_out_of_the_attribute(self):
        result = publish_telegram.markdown_to_telegram_html('[x](https://e.it/a"onmouseover=1)')
        self.assertNotIn('"onmouseover', result)

    def test_other_formatting_still_works(self):
        result = publish_telegram.markdown_to_telegram_html("**bold** and `code`")
        self.assertEqual("<b>bold</b> and <code>code</code>", result)


class MarkdownToPlainTextTests(unittest.TestCase):
    def test_fallback_keeps_the_url(self):
        result = publish_telegram.markdown_to_plain_text("Vedi [Dev updates](https://github.com/owner/repo)")
        self.assertEqual("Vedi Dev updates: https://github.com/owner/repo", result)


class AlreadySentTests(unittest.TestCase):
    def test_second_run_does_not_send_again(self):
        import os
        import sys
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            recap = Path(tmp) / "recap-telegram-2026-07-24.md"
            recap.write_text("ciao")
            markers = Path(tmp) / "sent"
            argv = ["publish_telegram.py", str(recap), "--marker-dir", str(markers)]
            env = {"TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "c"}

            with patch.object(sys, "argv", argv), patch.dict(os.environ, env), \
                    patch("publish_telegram.send_message", return_value={"ok": True}) as send:
                self.assertEqual(0, publish_telegram.main())
                self.assertEqual(1, send.call_count)
                self.assertTrue((markers / "recap-telegram-2026-07-24.sent").exists())

                self.assertEqual(0, publish_telegram.main())
                self.assertEqual(1, send.call_count)

    def test_a_failed_send_leaves_no_marker(self):
        import os
        import sys
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as tmp:
            recap = Path(tmp) / "recap-telegram-2026-07-24.md"
            recap.write_text("ciao")
            markers = Path(tmp) / "sent"
            argv = ["publish_telegram.py", str(recap), "--marker-dir", str(markers)]
            env = {"TELEGRAM_BOT_TOKEN": "t", "TELEGRAM_CHAT_ID": "c"}

            with patch.object(sys, "argv", argv), patch.dict(os.environ, env), \
                    patch("publish_telegram.send_message", return_value={"ok": False, "error_code": 500}):
                self.assertEqual(1, publish_telegram.main())
            self.assertFalse((markers / "recap-telegram-2026-07-24.sent").exists())


if __name__ == "__main__":
    unittest.main()
