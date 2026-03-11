from __future__ import annotations


def test_qa_service_runs_and_persists_findings(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    services.extract(pid, root)
    services.detect_languages(pid)
    services.translate(pid, backend_name="dummy")
    services.voice_attempts(pid, root)

    summary = services.run_qa(pid)
    findings = services.repo.list_qa_findings(pid)
    assert summary["findings_total"] == len(findings)
    assert isinstance(findings, list)
