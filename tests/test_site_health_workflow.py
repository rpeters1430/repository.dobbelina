from pathlib import Path


WORKFLOW = Path(".github/workflows/site-health.yml")


def test_site_health_workflow_passes_existing_issues_to_triage_generator():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "gh issue list --state all" in workflow
    assert "--json number,title,body,state" in workflow
    assert "> results/existing_site_monitor_issues.json" in workflow
    assert "--existing-issues results/existing_site_monitor_issues.json" in workflow


def test_broad_smoke_reports_are_discovered_recursively():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "merge_smoke_reports.py --reports-dir all-results" in workflow
    assert "all-results/*/live_smoke_*.json" not in workflow
