from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Sequence, Tuple


@dataclass
class ListenerDeps:
    stop_event: Any
    pause_listen_event: Any
    monitor_active_event: Any
    restart_listen_event: Any
    build_recognizer: Callable[[], Any]
    get_selected_mic_index: Callable[[], Optional[int]]
    microphone_factory: Callable[..., Any]
    settings_provider: Callable[[], Dict[str, Any]]
    recognize_candidates: Callable[[Any, Any], Sequence[str]]
    match_command: Callable[[Sequence[str]], Tuple[Optional[str], Optional[dict], float, str, float]]
    launch_command: Callable[[dict], None]
    set_status: Callable[[str], None]
    set_last_phrase: Callable[[str], None]
    log_runtime: Callable[[str], None]
    log_asr: Callable[[str], None]
    wait_timeout_error: type[BaseException]
    sleep: Callable[[float], None] = time.sleep
    now: Callable[[], float] = time.time


class AppController:
    def __init__(self, deps: ListenerDeps, last_voice_trigger: Optional[Dict[str, Any]] = None):
        self.deps = deps
        self.recognizer = None
        self.last_adjust_ts = 0.0
        self.last_voice_trigger = dict(last_voice_trigger or {"phrase": "", "ts": 0.0})
        self.last_unmatched_heard = {"text": "", "ts": 0.0}

    @staticmethod
    def trigger_guard_seconds(mode: str) -> float:
        mode = str(mode or "normal").strip().lower()
        if mode == "launcher_play":
            return 18.0
        if mode == "admin_task":
            return 6.0
        return 2.8

    def _should_suppress_trigger(self, matched_phrase: str, now: float, trigger_guard: float) -> bool:
        return (
            matched_phrase == self.last_voice_trigger.get("phrase", "")
            and now - float(self.last_voice_trigger.get("ts", 0.0)) < trigger_guard
        )

    def _should_publish_unmatched(self, heard: str, score: float, margin: float, now: float) -> bool:
        text = str(heard or "").strip()
        if not text:
            return False

        # Фильтр шумовых "галлюцинаций" при тишине/фоне.
        if float(score) < 0.58:
            return False
        if len(text) >= 48 and float(score) < 0.72:
            return False
        if len(text) <= 2 and float(score) < 0.80:
            return False
        if float(margin) < 0.02 and float(score) < 0.75:
            return False

        last_text = str(self.last_unmatched_heard.get("text", "") or "")
        last_ts = float(self.last_unmatched_heard.get("ts", 0.0) or 0.0)
        if text == last_text and now - last_ts < 6.0:
            return False

        self.last_unmatched_heard = {"text": text, "ts": now}
        return True

    @staticmethod
    def friendly_audio_error(exc: Exception) -> str:
        raw = str(exc or "").strip()
        low = raw.lower()
        if "could not find pyaudio" in low:
            return "Микрофон недоступен: PyAudio не установлен. Установите пакет pyaudio."
        if "no default input device available" in low:
            return "Микрофон недоступен: в Windows не выбрано устройство ввода по умолчанию."
        if "invalid input device" in low:
            return "Микрофон недоступен: выбранное устройство ввода не найдено."
        if "unanticipated host error" in low or "device unavailable" in low:
            return "Микрофон временно недоступен. Проверьте, не занят ли он другим приложением."
        if raw:
            return f"Проблема микрофона: {raw}"
        return "Проблема микрофона: неизвестная ошибка."

    def run_listen_loop(self, max_iterations: Optional[int] = None) -> Dict[str, Any]:
        self.recognizer = self.deps.build_recognizer()
        self.deps.log_runtime("Listen loop started")
        iterations = 0

        while not self.deps.stop_event.is_set():
            if max_iterations is not None and iterations >= max_iterations:
                break
            iterations += 1

            if self.deps.pause_listen_event.is_set() or self.deps.monitor_active_event.is_set():
                self.deps.sleep(0.1)
                continue

            if self.deps.restart_listen_event.is_set():
                self.recognizer = self.deps.build_recognizer()
                self.deps.restart_listen_event.clear()

            mic_index = self.deps.get_selected_mic_index()
            settings = self.deps.settings_provider() or {}

            try:
                with self.deps.microphone_factory(device_index=mic_index) as source:
                    now = self.deps.now()
                    should_adjust = (now - self.last_adjust_ts) > 16 or bool(settings.get("dynamic_energy", True))
                    if should_adjust:
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.35)
                        self.last_adjust_ts = now

                    self.deps.set_status("Фоновое прослушивание активно")
                    audio = self.recognizer.listen(
                        source,
                        timeout=float(settings.get("listen_timeout", 1.8)),
                        phrase_time_limit=float(settings.get("listen_phrase_limit", 5.0)),
                    )

                candidates = list(self.deps.recognize_candidates(self.recognizer, audio) or [])
                matched_phrase, target, score, heard, margin = self.deps.match_command(candidates)

                if candidates:
                    preview = ", ".join(candidates[:3])
                    self.deps.log_asr(f"candidates=[{preview}]")

                if target:
                    now = self.deps.now()
                    mode = str(target.get("mode", "normal") or "normal").strip().lower()
                    if heard:
                        self.deps.set_last_phrase(heard)
                    trigger_guard = self.trigger_guard_seconds(mode)

                    if self._should_suppress_trigger(matched_phrase or "", now, trigger_guard):
                        self.deps.set_status(f"Антидубль фразы: '{matched_phrase}'")
                        self.deps.log_runtime(
                            f"Voice trigger suppressed: phrase='{matched_phrase}' guard={trigger_guard:.1f}s"
                        )
                        continue

                    self.last_voice_trigger = {"phrase": matched_phrase or "", "ts": now}
                    self.deps.launch_command(target)
                    self.deps.log_asr(
                        f"match heard='{heard}' -> '{matched_phrase}' "
                        f"score={score:.2f} margin={margin:.2f}"
                    )
                    if score < 1.0:
                        self.deps.set_status(
                            f"Слышу '{heard}' -> '{matched_phrase}' "
                            f"(score {score:.2f}, margin {margin:.2f})"
                        )
                elif heard:
                    now = self.deps.now()
                    if self._should_publish_unmatched(heard, score, margin, now):
                        self.deps.set_status(f"Слышу '{heard}', но команды не совпали")
                        self.deps.set_last_phrase(heard)
                        self.deps.log_asr(f"no-match heard='{heard}' score={score:.2f} margin={margin:.2f}")
                    else:
                        self.deps.log_asr(
                            f"no-match filtered heard='{heard}' score={score:.2f} margin={margin:.2f}"
                        )
            except self.deps.wait_timeout_error:
                continue
            except Exception as exc:
                self.deps.set_status(self.friendly_audio_error(exc))
                self.deps.log_runtime(f"Listen loop microphone error: {exc}")
                self.deps.sleep(0.5)

        return dict(self.last_voice_trigger)
