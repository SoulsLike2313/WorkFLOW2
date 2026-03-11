from __future__ import annotations


def test_translate_with_context(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    services.extract(pid, root)
    services.detect_languages(pid)
    summary = services.translate(pid, backend_name="local_mock", style="radio")

    assert summary["translated"] >= 300
    assert summary["context_used_count"] > 0
    rows = services.repo.list_translations(pid)
    assert any(row.get("context_used") for row in rows)


def test_translate_fallback_backend_path(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    services.extract(pid, root)
    services.detect_languages(pid)
    summary = services.translate(pid, backend_name="non_existing_backend", style="neutral")

    assert summary["translated"] >= 300
    assert summary["fallback_used_count"] > 0
    backend_runs = services.repo.list_translation_backend_runs(pid, limit=30)
    assert backend_runs
    assert any(run["fallback_used"] for run in backend_runs)
