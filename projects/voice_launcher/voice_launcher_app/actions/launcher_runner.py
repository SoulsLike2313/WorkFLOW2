from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Sequence

from .launcher_safety import LauncherReport, LauncherTarget, SafeLauncherAutomation


@dataclass
class LauncherRunnerDeps:
    desktop_factory: Callable[[], Any]
    process_resolver: Callable[[int], tuple[str, str]]
    find_running_process: Callable[[dict], str]
    launch_target: Callable[[str], None]
    find_play_control: Callable[[Any, str], Any]
    is_control_enabled: Callable[[Any], bool]
    click_play_control: Callable[[Any, Any], tuple[bool, str]]
    play_control_is_ready: Callable[[Any, str], bool]
    activate_window: Callable[[Any], bool]
    build_window_hints: Callable[[str, str], Sequence[str]]
    normalize_phrase: Callable[[str], str]
    logger: Callable[[str], None]
    runtime_logger: Callable[[str], None]
    set_status: Callable[[str], None]
    set_last_action: Callable[[str], None]


def run_launcher_play(entry: dict, deps: LauncherRunnerDeps) -> LauncherReport:
    path = str(entry.get("path", "") or "").strip()
    play_text = str(entry.get("play_text", "Играть") or "Играть").strip()
    window_title = str(entry.get("window_title", "") or "").strip()
    wait_timeout = max(30, min(900, int(entry.get("wait_timeout", 240) or 240)))
    launcher_dry_run = bool(entry.get("launcher_dry_run", False))
    launcher_highlight = bool(entry.get("launcher_highlight", False))
    try:
        min_confidence = float(entry.get("min_window_confidence", 0.90))
    except Exception:
        min_confidence = 0.90
    min_confidence = max(0.65, min(0.99, min_confidence))

    title_patterns = []
    for item in [window_title] + list(deps.build_window_hints(path, window_title)):
        norm = deps.normalize_phrase(item or "")
        if norm and norm not in title_patterns:
            title_patterns.append(norm)

    target = LauncherTarget(
        path=path,
        button_text=play_text,
        title_patterns=title_patterns,
        wait_timeout=wait_timeout,
        min_window_confidence=min_confidence,
        dry_run=launcher_dry_run,
        highlight_only=launcher_highlight,
    )
    deps.logger(
        "SAFE_START | "
        f"path='{path}' play='{play_text}' title_patterns={title_patterns} "
        f"timeout={wait_timeout} dry_run={launcher_dry_run} highlight={launcher_highlight} "
        f"min_conf={min_confidence:.2f}"
    )
    deps.runtime_logger(f"Launcher+Play safe start: path='{path}' mode=launcher_play")

    def process_starter(target_path: str) -> None:
        running_proc = deps.find_running_process(entry)
        if running_proc:
            deps.logger(f"SAFE_INFO | process already running: {running_proc}")
            return
        deps.launch_target(target_path)

    def button_finder(window_wrapper, button_text):
        found = deps.find_play_control(window_wrapper, button_text)
        if not found:
            return None
        control, caption, control_type, score = found
        if not deps.is_control_enabled(control):
            return None
        return {
            "control": control,
            "caption": caption,
            "control_type": control_type,
            "score": score,
        }

    def button_clicker(control_payload, window_wrapper):
        if not isinstance(control_payload, dict):
            return False
        control = control_payload.get("control")
        if control is None:
            return False
        clicked, method = deps.click_play_control(control, window_wrapper)
        if clicked:
            deps.logger(
                f"SAFE_CLICK | method={method} caption='{control_payload.get('caption', '')}' "
                f"type={control_payload.get('control_type', '')} "
                f"score={float(control_payload.get('score', 0.0)):.2f}"
            )
            try:
                time.sleep(0.9)
            except Exception:
                pass
            if deps.play_control_is_ready(window_wrapper, play_text):
                deps.logger("SAFE_CLICK | button still ready after click, launcher may reject it")
            return True
        return False

    def highlighter(window_wrapper, control_payload):
        if not isinstance(control_payload, dict):
            return
        control = control_payload.get("control")
        try:
            deps.activate_window(window_wrapper)
        except Exception:
            pass
        try:
            if hasattr(control, "draw_outline"):
                control.draw_outline(colour="green", thickness=3)
        except Exception:
            pass
        try:
            if hasattr(window_wrapper, "draw_outline"):
                window_wrapper.draw_outline(colour="blue", thickness=2)
        except Exception:
            pass

    deps.set_status(f"Безопасный поиск окна лаунчера: '{play_text}'")
    automation = SafeLauncherAutomation(desktop_factory=deps.desktop_factory, logger=deps.logger)
    report = automation.run(
        target=target,
        process_resolver=deps.process_resolver,
        process_starter=process_starter,
        button_finder=button_finder,
        button_clicker=button_clicker,
        highlighter=highlighter,
    )
    deps.runtime_logger(
        f"Launcher+Play report: ok={report.ok} stage={report.stage} "
        f"clicked={report.clicked} preview={report.preview_only} conf={report.window_confidence:.2f}"
    )
    if report.ok and report.clicked:
        deps.set_status("Лаунчер: безопасный клик выполнен")
        deps.set_last_action("Лаунчер: клик по кнопке выполнен")
    elif report.ok and report.preview_only:
        deps.set_status("Лаунчер: preview/dry-run выполнен, без клика")
        deps.set_last_action("Лаунчер: выполнен безопасный preview")
    else:
        deps.set_status(f"Лаунчер: {report.message}")
        deps.set_last_action(f"Лаунчер: {report.message}")
    return report
