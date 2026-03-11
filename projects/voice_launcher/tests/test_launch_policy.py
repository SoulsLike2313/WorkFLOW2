from dataclasses import dataclass

from voice_launcher_app.core.launch_policy import (
    LaunchGate,
    ProcessScanner,
    command_launch_key,
    find_running_process_for_entry,
    get_entry_process_names,
)


@dataclass
class RunnerResult:
    returncode: int
    stdout: str


class Clock:
    def __init__(self, value=0.0):
        self.value = float(value)

    def now(self):
        return self.value

    def advance(self, delta: float):
        self.value += float(delta)


def test_get_entry_process_names_supports_launcher_heuristic():
    entry = {"path": "E:/WarThunder/launcher.exe"}
    names = get_entry_process_names(entry)
    assert "launcher.exe" in names
    assert "warthunder.exe" in names


def test_find_running_process_for_entry():
    entry = {"path": "E:/WarThunder/launcher.exe"}
    name = find_running_process_for_entry(entry, {"explorer.exe", "launcher.exe"})
    assert name == "launcher.exe"


def test_process_scanner_uses_cache():
    calls = []

    def runner(_args):
        calls.append(1)
        return RunnerResult(0, '"launcher.exe","123","Console","1","10 K"\n')

    clock = Clock(0.0)
    scanner = ProcessScanner(runner=runner, now=clock.now, cache_ttl=1.0, platform_name="nt")
    first = scanner.get_running_process_names()
    second = scanner.get_running_process_names()
    assert "launcher.exe" in first
    assert first == second
    assert len(calls) == 1

    clock.advance(2.0)
    scanner.get_running_process_names()
    assert len(calls) == 2


def test_launch_gate_cooldown_and_single_instance():
    clock = Clock(10.0)
    gate = LaunchGate(now=clock.now)
    entry = {"mode": "normal", "path": "C:/app.exe", "debounce_seconds": 2.0, "single_instance": True}

    first = gate.can_launch_entry(entry, find_running_process=lambda _e: "")
    assert first.can_launch is True
    assert first.reason == "ok"

    second = gate.can_launch_entry(entry, find_running_process=lambda _e: "")
    assert second.can_launch is False
    assert second.reason == "cooldown"

    clock.advance(3.0)
    third = gate.can_launch_entry(entry, find_running_process=lambda _e: "app.exe")
    assert third.can_launch is False
    assert third.reason == "already_running"


def test_command_launch_key():
    key = command_launch_key({"mode": "LAUNCHER_PLAY", "path": "E:/WarThunder/launcher.exe"})
    assert key == "launcher_play|e:/warthunder/launcher.exe"


def test_launch_gate_inflight_and_finish_cooldown():
    clock = Clock(100.0)
    gate = LaunchGate(now=clock.now)
    entry = {"mode": "launcher_play", "path": "E:/WarThunder/launcher.exe", "wait_timeout": 200}

    hold = gate.mark_launch_started(entry)
    assert hold >= 35.0

    blocked_inflight = gate.can_launch_entry(entry, find_running_process=lambda _e: "")
    assert blocked_inflight.can_launch is False
    assert blocked_inflight.reason == "inflight"

    cooldown = gate.mark_launch_finished(entry, ok=True)
    assert cooldown >= 100.0

    blocked_cooldown = gate.can_launch_entry(entry, find_running_process=lambda _e: "")
    assert blocked_cooldown.can_launch is False
    assert blocked_cooldown.reason == "cooldown"


def test_launch_gate_respects_custom_post_launch_cooldown():
    clock = Clock(5.0)
    gate = LaunchGate(now=clock.now)
    entry = {
        "mode": "launcher_play",
        "path": "E:/WarThunder/launcher.exe",
        "post_launch_cooldown": 15,
    }

    gate.mark_launch_started(entry, hold_seconds=2.0)
    gate.mark_launch_finished(entry, ok=True)

    clock.advance(10.0)
    blocked = gate.can_launch_entry(entry, find_running_process=lambda _e: "")
    assert blocked.can_launch is False
    assert blocked.reason == "cooldown"

    clock.advance(6.0)
    allowed = gate.can_launch_entry(entry, find_running_process=lambda _e: "")
    assert allowed.can_launch is True
    assert allowed.reason == "ok"
