import importlib.util
import json
import pathlib
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("sync_project", pathlib.Path(__file__).with_name("sync-project.py"))
sync_project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_project)


class SyncProjectTest(unittest.TestCase):
    def test_adds_issues_and_dependabot_prs_without_duplicates(self):
        repo = {"owner": {"login": "ccamel"}, "fork": False, "archived": False, "has_issues": True, "full_name": "ccamel/repo"}
        no_issues = dict(repo, has_issues=False, full_name="ccamel/no-issues")
        project = [{"data": {"user": {"projectV2": {"id": "project-id", "items": {"nodes": [
            {"content": {"id": "existing-issue"}}, {"content": {"id": "existing-pr"}}, {"content": None}
        ]}}}}}]
        calls = []

        def fake_gh(*args):
            calls.append(args)
            if args[:2] == ("api", "graphql"):
                return "{}" if any(arg.startswith("query=mutation") for arg in args) else json.dumps(project)
            if args[-1].startswith("/user/repos?"):
                return json.dumps([[repo, no_issues, dict(repo, fork=True), dict(repo, archived=True)]])
            if "/repo/issues?" in args[-1]:
                return json.dumps([[{"node_id": "existing-issue"}, {"node_id": "new-issue"},
                                    {"node_id": "pr-as-issue", "pull_request": {}}]])
            if "/repo/pulls?" in args[-1]:
                return json.dumps([[{"node_id": "existing-pr"}, {"node_id": "dependabot-pr",
                                    "user": {"login": "dependabot[bot]"}}]])
            if "/no-issues/pulls?" in args[-1]:
                return json.dumps([[{"node_id": "pr-no-issues"}]])
            raise AssertionError("Unexpected GitHub command")

        with patch.object(sync_project, "gh", side_effect=fake_gh):
            sync_project.sync()
        additions = [call for call in calls if any(arg.startswith("query=mutation") for arg in call)]
        self.assertEqual({arg for call in additions for arg in call if arg.startswith("contentId=")},
                         {"contentId=new-issue", "contentId=dependabot-pr", "contentId=pr-no-issues"})
        self.assertEqual(len(additions), 3)
        for call in additions:
            self.assertIn("projectId=project-id", call)

    def test_failure_identifies_operation_without_leaking_private_data(self):
        failure = unittest.mock.Mock(returncode=1, stdout="", stderr="HTTP 403: private-owner/private-repo")
        with patch.object(sync_project.subprocess, "run", return_value=failure):
            with self.assertRaises(RuntimeError) as error:
                sync_project.gh("api", "graphql", "-f", "query=mutation { addProjectV2ItemById }")
        self.assertIn("adding item", str(error.exception))
        self.assertIn("HTTP 403", str(error.exception))
        self.assertNotIn("private", str(error.exception))


if __name__ == "__main__":
    unittest.main()
