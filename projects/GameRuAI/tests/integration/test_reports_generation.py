from __future__ import annotations


def test_generate_project_summary_after_full_pipeline(services) -> None:
    root = services.config.paths.fixtures_root
    result = services.pipeline_end_to_end("Reports Integration Full", root)
    pid = int(result["project"]["id"])

    snapshot = services.reports_snapshot(pid)
    summary = snapshot.get("project_summary", {})
    assert summary
    assert summary["totals"]["entries"] >= 300
    assert "translation" in summary and "voice" in summary and "language" in summary

    diagnostics = services.diagnostics_snapshot(pid)
    assert diagnostics["backend_diagnostics"]
    assert diagnostics["quality_snapshots"]


def test_generate_translation_voice_language_reports(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    services.extract(pid, root)
    services.detect_languages(pid)
    services.translate(pid, backend_name="local_mock")
    services.voice_attempts(pid, root)
    services.run_qa(pid)
    services.generate_reports(pid)

    reports = services.reports_snapshot(pid)
    translation = reports["translation_report"]
    summary = reports["project_summary"]
    assert translation["translated_count"] >= 300
    assert summary["voice"]["attempts_total"] > 0
    assert summary["language"]["distribution"]
    assert reports["language_reports"]

