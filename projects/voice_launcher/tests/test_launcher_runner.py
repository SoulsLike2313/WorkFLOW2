from voice_launcher_app.actions.launcher_runner import LauncherRunnerDeps, run_launcher_play


class FakeWindow:
    def __init__(self, title: str, handle: int):
        self._title = title
        self.handle = handle

    def window_text(self):
        return self._title


class FakeDesktop:
    def __init__(self, windows):
        self._windows = windows

    def windows(self):
        return list(self._windows)


def test_launcher_runner_happy_path(tmp_path):
    exe = tmp_path / "launcher.exe"
    exe.write_text("ok", encoding="utf-8")

    logs = []
    statuses = []
    actions = []
    launched = []
    fake_window = FakeWindow("War Thunder Launcher", 77)

    deps = LauncherRunnerDeps(
        desktop_factory=lambda: FakeDesktop([fake_window]),
        process_resolver=lambda hwnd: ("launcher.exe", str(exe)) if hwnd == 77 else ("", ""),
        find_running_process=lambda _entry: "",
        launch_target=lambda path: launched.append(path),
        find_play_control=lambda _win, _btn: (object(), "Играть", "Button", 0.95),
        is_control_enabled=lambda _ctrl: True,
        click_play_control=lambda _ctrl, _win: (True, "invoke"),
        play_control_is_ready=lambda _win, _text: False,
        activate_window=lambda _win: True,
        build_window_hints=lambda _path, _title: ["war thunder"],
        normalize_phrase=lambda t: " ".join(str(t).strip().lower().split()),
        logger=lambda text: logs.append(text),
        runtime_logger=lambda text: logs.append(text),
        set_status=lambda text: statuses.append(text),
        set_last_action=lambda text: actions.append(text),
    )
    report = run_launcher_play(
        entry={
            "mode": "launcher_play",
            "path": str(exe),
            "play_text": "Играть",
            "window_title": "War Thunder",
            "wait_timeout": 30,
            "launcher_dry_run": False,
            "launcher_highlight": False,
            "min_window_confidence": 0.88,
        },
        deps=deps,
    )
    assert report.ok is True
    assert report.clicked is True
    assert launched == [str(exe)]
    assert any("безопасный клик" in status.lower() for status in statuses)
