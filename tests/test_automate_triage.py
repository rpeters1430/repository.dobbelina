import subprocess

import pytest

from scripts.automate_triage import execute_triage_requests


def test_execute_triage_requests_handles_create(monkeypatch):
    gh_calls = []

    def mock_run_gh(args):
        gh_calls.append(args)
        class Res:
            returncode = 0
            stdout = "https://github.com/test/repo/issues/100"
            stderr = ""
        return Res()

    monkeypatch.setattr("scripts.automate_triage.run_gh", mock_run_gh)

    requests = [
        {
            "action": "CREATE_OR_REOPEN",
            "site": "pornhub",
            "title": "[Site Monitor] pornhub is broken",
            "body": "Issue body",
            "labels": ["site-monitor", "failure/broken"],
        }
    ]

    summary = execute_triage_requests(requests, repo="test/repo")
    assert summary == ["pornhub: CREATE"]
    assert any("issue" in call and "create" in call for call in gh_calls)


def test_execute_triage_requests_handles_close(monkeypatch):
    gh_calls = []

    def mock_run_gh(args):
        gh_calls.append(args)
        class Res:
            returncode = 0
            stdout = ""
            stderr = ""
        return Res()

    monkeypatch.setattr("scripts.automate_triage.run_gh", mock_run_gh)

    requests = [
        {
            "action": "CLOSE",
            "site": "pornhub",
            "issue_number": "42",
            "comment": "Closing issue after recovery pass 2",
        }
    ]

    summary = execute_triage_requests(requests, repo="test/repo")
    assert summary == ["pornhub: CLOSE #42"]
    assert any("issue" in call and "close" in call and "42" in call for call in gh_calls)


def test_execute_triage_requests_propagates_github_cli_failure(monkeypatch):
    def failed_run(*args, **kwargs):
        return subprocess.CompletedProcess(
            args=args,
            returncode=1,
            stdout="",
            stderr="GitHub API unavailable",
        )

    monkeypatch.setattr("scripts.automate_triage.subprocess.run", failed_run)

    with pytest.raises(subprocess.CalledProcessError, match="returned non-zero exit status 1"):
        execute_triage_requests(
            [{"action": "CLOSE", "site": "pornhub", "issue_number": "42"}],
            repo="test/repo",
        )
