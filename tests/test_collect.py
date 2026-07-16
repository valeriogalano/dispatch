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


if __name__ == "__main__":
    unittest.main()
