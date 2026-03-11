from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Optional

from ..storage.repository import normalize_command_entry, normalize_phrase


@dataclass
class CommandSaveResult:
    ok: bool
    message: str
    code: str
    entry: Optional[dict] = None
    phrase: str = ""
    conflict_phrase: str = ""
    conflict_score: float = 0.0


def detect_phrase_conflict(
    commands: Dict[str, dict],
    phrase: str,
    score_func: Callable[[str, str], float],
    ignore_phrase: str = "",
) -> tuple[str, float]:
    check_phrase = normalize_phrase(phrase or "")
    if not check_phrase:
        return "", 0.0
    ignore_norm = normalize_phrase(ignore_phrase or "")
    best_phrase = ""
    best_score = 0.0
    for existing in commands.keys():
        existing_norm = normalize_phrase(existing)
        if not existing_norm or existing_norm == ignore_norm:
            continue
        score = score_func(check_phrase, existing_norm)
        if score > best_score:
            best_phrase = existing_norm
            best_score = score
    return best_phrase, best_score


def build_command_entry(
    *,
    path: str,
    use_admin: bool,
    launcher_play: bool,
    play_text: str,
    window_title: str,
    wait_timeout: int,
    single_instance: bool,
    debounce_seconds: float,
    launcher_dry_run: bool,
    launcher_highlight: bool,
    min_window_confidence: float,
    build_task_name: Callable[[str], str],
    post_launch_cooldown: int = 110,
) -> dict:
    entry = {
        "mode": "normal",
        "path": path,
        "task_name": "",
        "play_text": play_text or "Играть",
        "window_title": window_title or "",
        "wait_timeout": int(wait_timeout),
        "single_instance": bool(single_instance),
        "debounce_seconds": float(debounce_seconds),
        "launcher_dry_run": bool(launcher_dry_run),
        "launcher_highlight": bool(launcher_highlight),
        "min_window_confidence": float(min_window_confidence),
        "post_launch_cooldown": int(post_launch_cooldown),
    }
    if use_admin:
        entry["mode"] = "admin_task"
        entry["task_name"] = build_task_name(path)
    elif launcher_play:
        entry["mode"] = "launcher_play"

    normalized = normalize_command_entry(entry)
    if not normalized:
        raise ValueError("Некорректная команда после нормализации")
    return normalized.to_dict()


def save_command_definition(
    *,
    commands: Dict[str, dict],
    phrase: str,
    path: str,
    use_admin: bool,
    launcher_play: bool,
    play_text: str,
    window_title: str,
    wait_timeout: int,
    single_instance: bool,
    debounce_seconds: float,
    launcher_dry_run: bool,
    launcher_highlight: bool,
    min_window_confidence: float,
    build_task_name: Callable[[str], str],
    score_func: Callable[[str, str], float],
    path_exists: Callable[[str], bool],
    ignore_phrase: str = "",
    conflict_threshold: float = 0.90,
    post_launch_cooldown: int = 110,
) -> CommandSaveResult:
    phrase = normalize_phrase(phrase)
    if not phrase:
        return CommandSaveResult(False, "Введите непустую фразу.", code="empty_phrase")
    if not path:
        return CommandSaveResult(False, "Выберите файл.", code="empty_path")
    if not path_exists(path):
        return CommandSaveResult(False, f"Путь не найден: {path}", code="missing_path")

    conflict_phrase, conflict_score = detect_phrase_conflict(
        commands=commands,
        phrase=phrase,
        score_func=score_func,
        ignore_phrase=ignore_phrase,
    )
    if conflict_phrase and conflict_score >= conflict_threshold:
        return CommandSaveResult(
            False,
            (
                f"Найдена слишком похожая команда: '{conflict_phrase}' "
                f"(score {conflict_score:.2f}). Измените фразу."
            ),
            code="phrase_conflict",
            conflict_phrase=conflict_phrase,
            conflict_score=conflict_score,
        )

    try:
        entry = build_command_entry(
            path=path,
            use_admin=use_admin,
            launcher_play=launcher_play,
            play_text=play_text,
            window_title=window_title,
            wait_timeout=wait_timeout,
            single_instance=single_instance,
            debounce_seconds=debounce_seconds,
            launcher_dry_run=launcher_dry_run,
            launcher_highlight=launcher_highlight,
            min_window_confidence=min_window_confidence,
            post_launch_cooldown=post_launch_cooldown,
            build_task_name=build_task_name,
        )
    except ValueError as exc:
        return CommandSaveResult(False, str(exc), code="invalid_entry")

    commands[phrase] = entry
    return CommandSaveResult(True, "Команда сохранена", code="ok", entry=entry, phrase=phrase)
