from voice_launcher_app.actions.target_launcher import TargetLauncher, TargetLauncherDeps, TargetLauncherState


class Clock:
    def __init__(self, value=0.0):
        self.value = float(value)

    def now(self):
        return self.value

    def advance(self, delta: float):
        self.value += float(delta)


def test_target_launcher_starts_process_and_updates_state():
    statuses = []
    actions = []
    logs = []
    started = []
    clock = Clock(10.0)

    launcher = TargetLauncher(
        deps=TargetLauncherDeps(
            path_exists=lambda path: path == "C:/app.exe",
            status=lambda text: statuses.append(text),
            last_action=lambda text: actions.append(text),
            runtime_log=lambda text: logs.append(text),
            time_now=clock.now,
            platform_name="posix",
            os_startfile=None,
            popen=lambda args: started.append(args),
        ),
        state=TargetLauncherState(),
    )
    ok = launcher.launch_target("C:/app.exe")
    assert ok is True
    assert launcher.state.last_path == "C:/app.exe"
    assert launcher.state.last_time == 10.0
    assert started == [["C:/app.exe"]]
    assert any("Запущено:" in text for text in statuses)


def test_target_launcher_duplicate_guard():
    statuses = []
    actions = []
    logs = []
    started = []
    clock = Clock(5.0)

    launcher = TargetLauncher(
        deps=TargetLauncherDeps(
            path_exists=lambda _path: True,
            status=lambda text: statuses.append(text),
            last_action=lambda text: actions.append(text),
            runtime_log=lambda text: logs.append(text),
            time_now=clock.now,
            platform_name="posix",
            os_startfile=None,
            popen=lambda args: started.append(args),
        ),
        state=TargetLauncherState(last_path="C:/app.exe", last_time=4.5),
    )
    ok = launcher.launch_target("C:/app.exe", duplicate_guard_seconds=1.0)
    assert ok is False
    assert started == []
    assert any("duplicate-guard" in line for line in logs)


def test_target_launcher_missing_path():
    statuses = []
    launcher = TargetLauncher(
        deps=TargetLauncherDeps(
            path_exists=lambda _path: False,
            status=lambda text: statuses.append(text),
            last_action=lambda _text: None,
            runtime_log=lambda _text: None,
        ),
        state=TargetLauncherState(),
    )
    ok = launcher.launch_target("C:/missing.exe")
    assert ok is False
    assert statuses == ["Файл не найден"]
