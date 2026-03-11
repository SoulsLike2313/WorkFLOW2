from voice_launcher_app.actions.launcher_safety import LauncherTarget, SafeLauncherAutomation


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


def test_safe_launcher_clicks_only_when_verified(tmp_path):
    exe = tmp_path / "launcher.exe"
    exe.write_text("stub", encoding="utf-8")

    clicked = {"value": False}
    fake_windows = [FakeWindow("War Thunder Launcher", 101)]

    automation = SafeLauncherAutomation(desktop_factory=lambda: FakeDesktop(fake_windows))
    target = LauncherTarget(
        path=str(exe),
        button_text="Играть",
        title_patterns=["war thunder"],
        min_window_confidence=0.88,
        wait_timeout=5,
    )

    def process_resolver(hwnd):
        assert hwnd == 101
        return "launcher.exe", str(exe)

    def process_starter(path):
        assert path == str(exe)

    def button_finder(window_wrapper, button_text):
        assert button_text == "Играть"
        return {"window": window_wrapper}

    def button_clicker(control_payload, window_wrapper):
        clicked["value"] = True
        return True

    report = automation.run(
        target=target,
        process_resolver=process_resolver,
        process_starter=process_starter,
        button_finder=button_finder,
        button_clicker=button_clicker,
    )
    assert report.ok is True
    assert report.clicked is True
    assert clicked["value"] is True


def test_safe_launcher_refuses_low_confidence_window(tmp_path):
    exe = tmp_path / "launcher.exe"
    exe.write_text("stub", encoding="utf-8")

    fake_windows = [FakeWindow("Unknown Window", 202)]
    automation = SafeLauncherAutomation(desktop_factory=lambda: FakeDesktop(fake_windows))
    target = LauncherTarget(
        path=str(exe),
        button_text="Играть",
        title_patterns=["war thunder"],
        min_window_confidence=0.95,
        wait_timeout=1,
    )

    def process_resolver(_hwnd):
        return "other.exe", str(tmp_path / "other.exe")

    report = automation.run(
        target=target,
        process_resolver=process_resolver,
        process_starter=lambda _path: None,
        button_finder=lambda _win, _btn: None,
        button_clicker=lambda _ctrl, _win: False,
    )
    assert report.ok is False
    assert report.stage in {"verify_window", "wait_window"}


def test_safe_launcher_accepts_untitled_window_when_process_path_exact(tmp_path):
    exe = tmp_path / "launcher.exe"
    exe.write_text("stub", encoding="utf-8")

    fake_windows = [FakeWindow("", 303)]
    clicked = {"value": False}
    automation = SafeLauncherAutomation(desktop_factory=lambda: FakeDesktop(fake_windows))
    target = LauncherTarget(
        path=str(exe),
        button_text="Играть",
        title_patterns=["war thunder", "launcher"],
        min_window_confidence=0.90,
        wait_timeout=2,
    )

    def process_resolver(_hwnd):
        return "launcher.exe", str(exe)

    def button_finder(_win, _btn):
        return {"ok": True}

    def button_clicker(_ctrl, _win):
        clicked["value"] = True
        return True

    report = automation.run(
        target=target,
        process_resolver=process_resolver,
        process_starter=lambda _path: None,
        button_finder=button_finder,
        button_clicker=button_clicker,
    )
    assert report.ok is True
    assert clicked["value"] is True
