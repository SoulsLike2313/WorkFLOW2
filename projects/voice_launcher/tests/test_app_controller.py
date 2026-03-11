from __future__ import annotations

from dataclasses import dataclass

from voice_launcher_app.app.controller import AppController, ListenerDeps


class Flag:
    def __init__(self, value: bool = False):
        self._value = bool(value)

    def is_set(self) -> bool:
        return self._value

    def set(self) -> None:
        self._value = True

    def clear(self) -> None:
        self._value = False


class DummyMic:
    def __init__(self, device_index=None):
        self.device_index = device_index

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeRecognizer:
    def __init__(self, audios):
        self._audios = list(audios)
        self.adjust_called = 0

    def adjust_for_ambient_noise(self, _source, duration=0.35):
        self.adjust_called += 1

    def listen(self, _source, timeout=1.8, phrase_time_limit=5.0):
        if self._audios:
            return self._audios.pop(0)
        raise RuntimeError("no audio")


@dataclass
class Clock:
    value: float = 0.0

    def now(self) -> float:
        current = self.value
        self.value += 0.2
        return current


def make_deps(*, recognizer, match_payload, stop_event, statuses, phrases, launches, asr_logs, runtime_logs, clock):
    return ListenerDeps(
        stop_event=stop_event,
        pause_listen_event=Flag(False),
        monitor_active_event=Flag(False),
        restart_listen_event=Flag(False),
        build_recognizer=lambda: recognizer,
        get_selected_mic_index=lambda: 0,
        microphone_factory=DummyMic,
        settings_provider=lambda: {
            "dynamic_energy": True,
            "listen_timeout": 1.8,
            "listen_phrase_limit": 5.0,
        },
        recognize_candidates=lambda _r, _a: ["танки"],
        match_command=lambda _c: match_payload,
        launch_command=lambda target: launches.append(target),
        set_status=lambda text: statuses.append(text),
        set_last_phrase=lambda text: phrases.append(text),
        log_runtime=lambda text: runtime_logs.append(text),
        log_asr=lambda text: asr_logs.append(text),
        wait_timeout_error=TimeoutError,
        sleep=lambda _s: None,
        now=clock.now,
    )


def test_controller_suppresses_duplicate_phrase():
    statuses = []
    phrases = []
    launches = []
    asr_logs = []
    runtime_logs = []
    stop_event = Flag(False)
    recognizer = FakeRecognizer(audios=["a1", "a2"])
    clock = Clock(0.0)
    match_payload = ("танки", {"mode": "normal", "path": "x"}, 0.9, "танки", 0.5)

    deps = make_deps(
        recognizer=recognizer,
        match_payload=match_payload,
        stop_event=stop_event,
        statuses=statuses,
        phrases=phrases,
        launches=launches,
        asr_logs=asr_logs,
        runtime_logs=runtime_logs,
        clock=clock,
    )
    controller = AppController(deps=deps)
    controller.run_listen_loop(max_iterations=1)
    controller.run_listen_loop(max_iterations=1)

    assert len(launches) == 1
    assert any("Антидубль фразы" in text for text in statuses)
    assert phrases and phrases[0] == "танки"


def test_controller_handles_no_match_with_heard_phrase():
    statuses = []
    phrases = []
    launches = []
    asr_logs = []
    runtime_logs = []
    stop_event = Flag(False)
    recognizer = FakeRecognizer(audios=["a1"])
    clock = Clock(0.0)
    match_payload = (None, None, 0.0, "тан", 0.0)

    deps = make_deps(
        recognizer=recognizer,
        match_payload=match_payload,
        stop_event=stop_event,
        statuses=statuses,
        phrases=phrases,
        launches=launches,
        asr_logs=asr_logs,
        runtime_logs=runtime_logs,
        clock=clock,
    )
    controller = AppController(deps=deps)
    controller.run_listen_loop(max_iterations=1)

    assert launches == []
    assert any("не совпали" in text for text in statuses)
    assert phrases == ["тан"]
    assert any("no-match" in text for text in asr_logs)
