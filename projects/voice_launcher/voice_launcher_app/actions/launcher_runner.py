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
    click_window_point: Callable[[Any, float, float], tuple[bool, str]] | None = None


def run_launcher_play(entry: dict, deps: LauncherRunnerDeps) -> LauncherReport:
    path = str(entry.get("path", "") or "").strip()
    play_text = str(entry.get("play_text", "Играть") or "Играть").strip()
    window_title = str(entry.get("window_title", "") or "").strip()
    wait_timeout = max(30, min(900, int(entry.get("wait_timeout", 240) or 240)))
    launcher_dry_run = bool(entry.get("launcher_dry_run", False))
    launcher_highlight = bool(entry.get("launcher_highlight", False))

    path_low = path.replace("\\", "/").lower()
    war_thunder_point_mode = "warthunder" in path_low
    point_mode = str(entry.get("point_mode", "auto") or "auto").strip().lower()
    if point_mode not in {"auto", "force", "off"}:
        point_mode = "auto"
    force_point_click = point_mode == "force" or (point_mode == "auto" and war_thunder_point_mode)
    allow_point_fallback = force_point_click or (point_mode == "auto" and war_thunder_point_mode)

    default_x_ratio = 0.855 if war_thunder_point_mode else 0.86
    default_y_ratio = 0.945 if war_thunder_point_mode else 0.90
    try:
        point_x_ratio = float(entry.get("point_x_ratio", default_x_ratio))
    except Exception:
        point_x_ratio = default_x_ratio
    try:
        point_y_ratio = float(entry.get("point_y_ratio", default_y_ratio))
    except Exception:
        point_y_ratio = default_y_ratio
    point_x_ratio = max(0.05, min(0.98, point_x_ratio))
    point_y_ratio = max(0.05, min(0.98, point_y_ratio))

    try:
        min_confidence = float(entry.get("min_window_confidence", 0.90))
    except Exception:
        min_confidence = 0.90
    min_confidence = max(0.65, min(0.99, min_confidence))
    if force_point_click and min_confidence > 0.65:
        deps.logger(
            f"SAFE_INFO | lowering min_window_confidence from {min_confidence:.2f} to 0.65 for point-click mode"
        )
        min_confidence = 0.65

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
        f"min_conf={min_confidence:.2f} wt_point_mode={war_thunder_point_mode} "
        f"point_mode={point_mode} force_point={force_point_click} "
        f"point=({point_x_ratio:.2f},{point_y_ratio:.2f})"
    )
    deps.runtime_logger(f"Launcher+Play safe start: path='{path}' mode=launcher_play")

    def build_point_payload(score: float) -> dict:
        return {
            "point_click": True,
            "x_ratio": point_x_ratio,
            "y_ratio": point_y_ratio,
            "caption": "",
            "control_type": "PointFallback",
            "score": score,
        }

    def process_starter(target_path: str) -> None:
        running_proc = deps.find_running_process(entry)
        if running_proc:
            deps.logger(f"SAFE_INFO | process already running: {running_proc}")
            return
        deps.launch_target(target_path)

    def button_finder(window_wrapper, button_text):
        if force_point_click:
            deps.logger(
                f"SAFE_INFO | point-click mode active ({point_x_ratio:.2f},{point_y_ratio:.2f}), "
                "skip text button lookup"
            )
            return build_point_payload(0.70)

        found = deps.find_play_control(window_wrapper, button_text)
        if not found:
            if allow_point_fallback:
                deps.logger(
                    f"SAFE_INFO | button text not found, fallback to point-click mode ({point_x_ratio:.2f},{point_y_ratio:.2f})"
                )
                return build_point_payload(0.56)
            return None

        control, caption, control_type, score = found
        if not deps.is_control_enabled(control):
            if allow_point_fallback:
                deps.logger(
                    f"SAFE_INFO | text control disabled, fallback to point-click mode ({point_x_ratio:.2f},{point_y_ratio:.2f})"
                )
                return build_point_payload(0.54)
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

        if bool(control_payload.get("point_click")):
            if deps.click_window_point is None:
                return False
            clicked, method = deps.click_window_point(
                window_wrapper,
                float(control_payload.get("x_ratio", point_x_ratio)),
                float(control_payload.get("y_ratio", point_y_ratio)),
            )
            if clicked:
                deps.logger(
                    f"SAFE_CLICK | method={method} caption='point-fallback' type='PointFallback' "
                    f"score={float(control_payload.get('score', 0.0)):.2f}"
                )
            return bool(clicked)

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

            still_ready = deps.play_control_is_ready(window_wrapper, play_text)
            if still_ready:
                deps.logger("SAFE_CLICK | button still ready after click, launcher may reject it")
                if allow_point_fallback and deps.click_window_point is not None:
                    deps.logger(
                        f"SAFE_INFO | control click had no visible effect, retry via point-click ({point_x_ratio:.2f},{point_y_ratio:.2f})"
                    )
                    clicked_retry, method_retry = deps.click_window_point(
                        window_wrapper,
                        point_x_ratio,
                        point_y_ratio,
                    )
                    if clicked_retry:
                        deps.logger(
                            "SAFE_CLICK | "
                            f"method={method_retry} caption='point-fallback-after-control' "
                            "type='PointFallback' score=0.58"
                        )
                        return True
            return True

        if allow_point_fallback and deps.click_window_point is not None:
            deps.logger(
                f"SAFE_INFO | control click failed, retry via point-click ({point_x_ratio:.2f},{point_y_ratio:.2f})"
            )
            clicked_retry, method_retry = deps.click_window_point(
                window_wrapper,
                point_x_ratio,
                point_y_ratio,
            )
            if clicked_retry:
                deps.logger(
                    "SAFE_CLICK | "
                    f"method={method_retry} caption='point-fallback-after-fail' "
                    "type='PointFallback' score=0.55"
                )
                return True
        return False

    def highlighter(window_wrapper, control_payload):
        if not isinstance(control_payload, dict):
            return
        try:
            deps.activate_window(window_wrapper)
        except Exception:
            pass
        if bool(control_payload.get("point_click")):
            return
        control = control_payload.get("control")
        if control is not None:
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
