import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import collect


class BuildDigestTests(unittest.TestCase):
    @patch("collect.is_repo_public", return_value=True)
    @patch("collect.fetch_commits")
    def test_public_repo_section_links_to_project_page(self, fetch_commits, _is_repo_public):
        fetch_commits.return_value = [
            {
                "sha": "1234567",
                "subject": "feat: add recap links",
                "body": "",
                "url": "https://github.com/owner/project/commit/1234567",
                "category": "Added",
                "author": "",
            }
        ]

        digest = collect.build_digest(
            [{"slug": "owner/project", "name": "Project", "link": None}],
            token="token",
            since=datetime(2026, 7, 1, tzinfo=timezone.utc),
            until=datetime(2026, 7, 6, tzinfo=timezone.utc),
        )

        self.assertIn("<https://github.com/owner/project>", digest)
        self.assertNotIn("<https://github.com/owner/project/commits>", digest)
        self.assertIn("[`1234567`](https://github.com/owner/project/commit/1234567)", digest)

    @patch("collect.is_repo_public", return_value=True)
    @patch("collect.fetch_commits")
    def test_codeberg_repo_section_links_to_codeberg(self, fetch_commits, _is_repo_public):
        fetch_commits.return_value = [
            {
                "sha": "1234567",
                "subject": "feat: something",
                "body": "",
                "url": "https://codeberg.org/owner/project/commit/1234567",
                "category": "Added",
                "author": "",
            }
        ]

        digest = collect.build_digest(
            [{"slug": "owner/project", "name": "Project", "link": None, "host": "codeberg"}],
            token="token",
            since=datetime(2026, 7, 1, tzinfo=timezone.utc),
            until=datetime(2026, 7, 6, tzinfo=timezone.utc),
        )

        self.assertIn("<https://codeberg.org/owner/project>", digest)


class LoadConfigTests(unittest.TestCase):
    def test_host_prefix_parsing(self):
        import tempfile
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
            f.write("owner/gh-repo | GH Repo\ncodeberg:owner/cb-repo | CB Repo\nbadhost:owner/x | Bad\n")
            path = f.name
        repos = collect.load_config(path)
        self.assertEqual(len(repos), 2)
        self.assertEqual(repos[0]["host"], "github")
        self.assertEqual(repos[0]["slug"], "owner/gh-repo")
        self.assertEqual(repos[1]["host"], "codeberg")
        self.assertEqual(repos[1]["slug"], "owner/cb-repo")



class EmptyPeriodTests(unittest.TestCase):
    @patch("collect.is_repo_public", return_value=True)
    @patch("collect.fetch_commits", return_value=[])
    def test_no_digest_file_is_written_when_there_are_no_commits(self, _fetch_commits, _is_repo_public):
        import sys
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.txt"
            config.write_text("owner/project | Project\n")
            argv = ["collect.py", "--config", str(config), "--output-dir", tmp]
            with patch.object(sys, "argv", argv), patch.dict("os.environ", {"GH_TOKEN": "token"}):
                collect.main()
            self.assertEqual([], list(Path(tmp).glob("digest-*.md")))


class ManualEntriesTests(unittest.TestCase):
    @patch("collect.is_repo_public", return_value=True)
    @patch("collect.fetch_commits", return_value=[])
    def test_manual_note_in_the_window_makes_a_digest_even_without_commits(self, _commits, _public):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "2026-07-22.md").write_text("Pubblicato l'episodio 150 del podcast.")
            (Path(tmp) / "2026-01-01.md").write_text("Vecchia nota fuori finestra.")
            (Path(tmp) / "README.md").write_text("istruzioni, non una nota")

            digest = collect.build_digest(
                [{"slug": "owner/project", "name": "Project", "link": None}],
                token="token",
                since=datetime(2026, 7, 18, tzinfo=timezone.utc),
                until=datetime(2026, 7, 24, tzinfo=timezone.utc),
                manual_dir=tmp,
            )

        self.assertIn("Pubblicato l'episodio 150", digest)
        self.assertNotIn("Vecchia nota", digest)
        self.assertNotIn("istruzioni", digest)
        self.assertNotIn(collect.NO_COMMITS_MARKER, digest)


class RateLimitTests(unittest.TestCase):
    class FakeResponse:
        def __init__(self, status_code, headers):
            self.status_code = status_code
            self.headers = headers

    def test_forbidden_without_rate_limit_headers_is_not_a_wait(self):
        # a permission 403 retried forever would hang the job instead of failing it
        resp = self.FakeResponse(403, {})
        self.assertIsNone(collect.rate_limit_wait(resp))

    def test_exhausted_quota_waits_until_reset(self):
        import time
        resp = self.FakeResponse(403, {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": str(int(time.time()) + 30),
        })
        self.assertIn(collect.rate_limit_wait(resp), range(25, 31))

    def test_secondary_limit_honours_retry_after(self):
        resp = self.FakeResponse(429, {"Retry-After": "12"})
        self.assertEqual(12, collect.rate_limit_wait(resp))

    def test_wait_is_capped(self):
        resp = self.FakeResponse(429, {"Retry-After": "999999"})
        self.assertEqual(collect.MAX_RATE_LIMIT_SLEEP, collect.rate_limit_wait(resp))


class CategorizeTests(unittest.TestCase):
    def test_bang_outside_a_conventional_prefix_is_not_breaking(self):
        self.assertEqual("Changed", collect.categorize("fix crash on empty input!"))

    def test_bang_in_the_prefix_is_breaking(self):
        self.assertEqual("Breaking", collect.categorize("feat!: drop python 3.9"))

    def test_scoped_prefix_still_maps(self):
        self.assertEqual("Added", collect.categorize("feat(collect): add codeberg support"))


class ManualWindowTests(unittest.TestCase):
    def test_note_dated_on_since_belongs_to_the_previous_window(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "2026-07-18.md").write_text("nota del giorno di confine")
            entries = collect.load_manual_entries(
                tmp,
                since=datetime(2026, 7, 18, tzinfo=timezone.utc),
                until=datetime(2026, 7, 25, tzinfo=timezone.utc),
            )
        self.assertEqual([], entries)


if __name__ == "__main__":
    unittest.main()
