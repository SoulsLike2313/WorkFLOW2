from __future__ import annotations


def test_context_builder_returns_structured_context(services, demo_project) -> None:
    pid = int(demo_project["id"])
    root = services.config.paths.fixtures_root
    services.scan(pid, root)
    services.extract(pid, root)

    entries = services.repo.list_entries(pid, limit=50)
    entry = entries[10]
    scene_index = services._build_scene_index(root)
    context = services.context_builder.build(
        project_id=pid,
        entry_id=int(entry["id"]),
        style_preset="dramatic",
        scene_index=scene_index,
    )

    assert context.line_type
    assert context.file_group
    assert context.style_preset == "dramatic"
    assert isinstance(context.neighboring_lines, list)
    assert isinstance(context.used(), bool)
