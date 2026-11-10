import importlib.util
import json
import pathlib
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("sync_project", pathlib.Path(__file__).with_name("sync-project.py"))
sync_project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync_project)


class SyncProjectTest(unittest.TestCase):
    def test_adds_only_missing_open_issues_from_eligible_repositories(self):
        repo = {"owner": {"login": "ccamel"}, "fork": False, "archived": False, "has_issues": True, "full_name": "ccamel/repo"}
        project = [{"data": {"user": {"projectV2": {"id": "project-id", "items": {"nodes": [{"content": {"id": "existing"}}, {"content": None}]}}}}}]
        issues = [[
            {"node_id": "existing", "html_url": "https://example.com/existing"},
            {"node_id": "new", "html_url": "https://example.com/new"},
            {"node_id": "pr", "html_url": "https://example.com/pr", "pull_request": {}},
        ]]
        calls = []

        def fake_gh(*args):
            calls.append(args)
            if args[:2] == ("api", "graphql"):
                return "{}" if any(arg.startswith("query=mutation") for arg in args) else json.dumps(project)
            if args[-1].startswith("/user/repos?"):
                return json.dumps([[repo, dict(repo, fork=True), dict(repo, archived=True), dict(repo, has_issues=False)]])
            if args[-1].startswith("/repos/"):
                return json.dumps(issues)
            return ""

        with patch.object(sync_project, "gh", side_effect=fake_gh):
            sync_project.sync()
        additions = [call for call in calls if any(arg.startswith("query=mutation") for arg in call)]
        self.assertEqual(len(additions), 1)
        self.assertIn("projectId=project-id", additions[0])
        self.assertIn("contentId=new", additions[0])

    def test_failure_identifies_operation_without_leaking_private_data(self):
        failure = unittest.mock.Mock(returncode=1, stdout="", stderr="HTTP 403: private-owner/private-repo")
        with patch.object(sync_project.subprocess, "run", return_value=failure):
            with self.assertRaises(RuntimeError) as error:
                sync_project.gh("api", "graphql", "-f", "query=mutation { addProjectV2ItemById }")
        self.assertIn("adding issue", str(error.exception))
        self.assertIn("HTTP 403", str(error.exception))
        self.assertNotIn("private", str(error.exception))


if __name__ == "__main__":
    unittest.main()
