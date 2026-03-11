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


def _base_deps(exe_path: str, fake_window: FakeWindow):
    logs = []
    statuses = []
    actions = []
    launched = []

    deps = LauncherRunnerDeps(
        desktop_factory=lambda: FakeDesktop([fake_window]),
        process_resolver=lambda hwnd: ("launcher.exe", exe_path) if hwnd == fake_window.handle else ("", ""),
        find_running_process=lambda _entry: "",
        launch_target=lambda path: launched.append(path),
        find_play_control=lambda _win, _btn: (object(), "Play", "Button", 0.95),
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
        click_window_point=lambda _win, _x, _y: (True, "point_mouse_abs"),
    )
    return deps, logs, statuses, actions, launched


def test_launcher_runner_happy_path(tmp_path):
    exe = tmp_path / "launcher.exe"
    exe.write_text("ok", encoding="utf-8")

    fake_window = FakeWindow("War Thunder Launcher", 77)
    deps, logs, statuses, _actions, launched = _base_deps(str(exe), fake_window)

    report = run_launcher_play(
        entry={
            "mode": "launcher_play",
            "path": str(exe),
            "play_text": "Play",
            "window_title": "War Thunder",
            "wait_timeout": 30,
            "launcher_dry_run": False,
            "launcher_highlight": False,
            "min_window_confidence": 0.88,
            "point_mode": "off",
        },
        deps=deps,
    )

    assert report.ok is True
    assert report.clicked is True
    assert launched == [str(exe)]
    assert any("безопасный клик" in status.lower() for status in statuses)
    assert any("SAFE_CLICK" in item for item in logs)


def test_launcher_runner_warthunder_uses_point_click_mode(tmp_path):
    war_dir = tmp_path / "WarThunder"
    war_dir.mkdir(parents=True, exist_ok=True)
    exe = war_dir / "launcher.exe"
    exe.write_text("ok", encoding="utf-8")

    fake_window = FakeWindow("War Thunder Launcher", 91)
    deps, logs, _statuses, _actions, _launched = _base_deps(str(exe), fake_window)

    calls = {"find": 0, "ctrl_click": 0, "point_click": 0}

    def find_play_control(_win, _btn):
        calls["find"] += 1
        return (object(), "Play", "Button", 0.9)

    def click_play_control(_ctrl, _win):
        calls["ctrl_click"] += 1
        return True, "invoke"

    def click_window_point(_win, _x, _y):
        calls["point_click"] += 1
        return True, "point_mouse_abs"

    deps.find_play_control = find_play_control
    deps.click_play_control = click_play_control
    deps.click_window_point = click_window_point

    report = run_launcher_play(
        entry={
            "mode": "launcher_play",
            "path": str(exe),
            "play_text": "Play",
            "window_title": "War Thunder",
            "wait_timeout": 30,
            "launcher_dry_run": False,
            "launcher_highlight": False,
            "min_window_confidence": 0.88,
            "point_mode": "auto",
        },
        deps=deps,
    )

    assert report.ok is True
    assert report.clicked is True
    assert calls["find"] == 0
    assert calls["ctrl_click"] == 0
    assert calls["point_click"] == 1
    assert any("point-click mode active" in line for line in logs)


def test_launcher_runner_fallbacks_to_point_when_control_click_fails(tmp_path):
    war_dir = tmp_path / "WarThunder"
    war_dir.mkdir(parents=True, exist_ok=True)
    exe = war_dir / "launcher.exe"
    exe.write_text("ok", encoding="utf-8")

    fake_window = FakeWindow("War Thunder Launcher", 133)
    deps, logs, _statuses, _actions, _launched = _base_deps(str(exe), fake_window)

    calls = {"ctrl_click": 0, "point_click": 0}

    deps.find_play_control = lambda _win, _btn: (object(), "Play", "Button", 0.91)

    def click_play_control(_ctrl, _win):
        calls["ctrl_click"] += 1
        return False, "none"

    def click_window_point(_win, _x, _y):
        calls["point_click"] += 1
        return True, "point_mouse_abs"

    deps.click_play_control = click_play_control
    deps.click_window_point = click_window_point

    report = run_launcher_play(
        entry={
            "mode": "launcher_play",
            "path": str(exe),
            "play_text": "Play",
            "window_title": "War Thunder",
            "wait_timeout": 30,
            "launcher_dry_run": False,
            "launcher_highlight": False,
            "min_window_confidence": 0.88,
            "point_mode": "off",
        },
        deps=deps,
    )

    assert report.ok is False
    assert report.clicked is False
    assert calls["ctrl_click"] == 1
    assert calls["point_click"] == 0

    report = run_launcher_play(
        entry={
            "mode": "launcher_play",
            "path": str(exe),
            "play_text": "Play",
            "window_title": "War Thunder",
            "wait_timeout": 30,
            "launcher_dry_run": False,
            "launcher_highlight": False,
            "min_window_confidence": 0.88,
            "point_mode": "auto",
        },
        deps=deps,
    )

    assert report.ok is True
    assert report.clicked is True
    assert calls["ctrl_click"] == 1
    assert calls["point_click"] >= 1
    assert any("point-click mode active" in line for line in logs)


def test_launcher_runner_lowers_confidence_for_forced_point_mode(tmp_path):
    war_dir = tmp_path / "WarThunder"
    war_dir.mkdir(parents=True, exist_ok=True)
    exe = war_dir / "launcher.exe"
    exe.write_text("ok", encoding="utf-8")

    logs = []
    statuses = []
    actions = []
    launched = []
    fake_window = FakeWindow("War Thunder Launcher", 201)

    deps = LauncherRunnerDeps(
        desktop_factory=lambda: FakeDesktop([fake_window]),
        process_resolver=lambda hwnd: ("launcher.exe", "") if hwnd == 201 else ("", ""),
        find_running_process=lambda _entry: "",
        launch_target=lambda path: launched.append(path),
        find_play_control=lambda _win, _btn: (object(), "Play", "Button", 0.95),
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
        click_window_point=lambda _win, _x, _y: (True, "point_mouse_abs"),
    )

    report = run_launcher_play(
        entry={
            "mode": "launcher_play",
            "path": str(exe),
            "play_text": "Play",
            "window_title": "War Thunder",
            "wait_timeout": 30,
            "launcher_dry_run": False,
            "launcher_highlight": False,
            "min_window_confidence": 0.90,
            "point_mode": "auto",
        },
        deps=deps,
    )

    assert report.ok is True
    assert report.clicked is True
    assert any("lowering min_window_confidence" in line for line in logs)
