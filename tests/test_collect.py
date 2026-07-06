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


if __name__ == "__main__":
    unittest.main()
