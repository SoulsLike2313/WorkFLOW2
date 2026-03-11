from voice_launcher_app.diagnostics.history import EventHistory


def test_event_history_keeps_tail_by_limit():
    history = EventHistory(limit=3)
    history.add_heard("первый")
    history.add_heard("второй")
    history.add_heard("третий")
    history.add_heard("четвертый")

    history.add_action("a1")
    history.add_action("a2")
    history.add_action("a3")
    history.add_action("a4")

    snap = history.snapshot(tail=3)
    assert snap["heard"] == ["второй", "третий", "четвертый"]
    assert snap["actions"] == ["a2", "a3", "a4"]


def test_event_history_ignores_empty_values():
    history = EventHistory(limit=5)
    history.add_heard("")
    history.add_heard("   ")
    history.add_action(None)  # type: ignore[arg-type]
    assert history.snapshot() == {"heard": [], "actions": []}
