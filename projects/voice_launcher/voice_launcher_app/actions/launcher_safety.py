from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from typing import Any, Iterable, List, Optional, Sequence, Tuple


def normalize(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


@dataclass
class LauncherTarget:
    path: str
    button_text: str = "Играть"
    title_patterns: Sequence[str] = field(default_factory=list)
    wait_timeout: int = 120
    min_window_confidence: float = 0.90
    dry_run: bool = False
    highlight_only: bool = False


@dataclass
class WindowCandidate:
    title: str
    process_name: str
    process_path: str
    wrapper: Any = None


@dataclass
class LauncherReport:
    ok: bool
    stage: str
    message: str
    clicked: bool = False
    preview_only: bool = False
    window_confidence: float = 0.0
    events: List[str] = field(default_factory=list)

    def log(self, text: str) -> None:
        self.events.append(text)


def compute_window_confidence(candidate: WindowCandidate, target: LauncherTarget) -> float:
    score = 0.0
    target_path = os.path.normcase(os.path.abspath(target.path or ""))
    cand_path = os.path.normcase(os.path.abspath(candidate.process_path or ""))
    target_name = os.path.basename(target_path).lower() if target_path else ""
    proc_name = os.path.basename(str(candidate.process_name or "")).lower()

    if target_path and cand_path and target_path == cand_path:
        # Точное совпадение process path считаем сильным и безопасным сигналом.
        score += 0.92
    elif target_path and cand_path and os.path.basename(target_path) == os.path.basename(cand_path):
        score += 0.68
    elif target_name and proc_name and target_name == proc_name:
        score += 0.56

    title_norm = normalize(candidate.title)
    patterns = [normalize(p) for p in target.title_patterns if normalize(p)]
    if patterns:
        if title_norm:
            matched = sum(1 for p in patterns if p in title_norm)
            if matched:
                score += min(0.20, 0.10 * matched)
            else:
                score -= 0.12
        else:
            # Некоторые лаунчеры рисуют окно без доступного заголовка.
            score -= 0.02
    elif title_norm:
        score += 0.05

    return max(0.0, min(1.0, score))


def select_best_window(
    candidates: Iterable[WindowCandidate],
    target: LauncherTarget,
) -> Tuple[Optional[WindowCandidate], float]:
    best = None
    best_score = 0.0
    for candidate in candidates:
        score = compute_window_confidence(candidate, target)
        if score > best_score:
            best = candidate
            best_score = score
    if best_score < target.min_window_confidence:
        return None, best_score
    return best, best_score


class SafeLauncherAutomation:
    """Verification-first launcher automation with click safety."""

    def __init__(self, desktop_factory, logger=None):
        self.desktop_factory = desktop_factory
        self.logger = logger

    def _log(self, report: LauncherReport, text: str) -> None:
        report.log(text)
        if self.logger:
            try:
                self.logger(text)
            except Exception:
                pass

    def _window_to_candidate(self, wrapper, process_resolver) -> Optional[WindowCandidate]:
        handle = None
        for attr in ("handle", "hwnd"):
            try:
                handle = int(getattr(wrapper, attr))
                break
            except Exception:
                continue
        if not handle:
            return None

        try:
            title = wrapper.window_text() or ""
        except Exception:
            title = ""
        title = str(title).strip()
        try:
            if hasattr(wrapper, "is_visible") and not wrapper.is_visible():
                return None
        except Exception:
            pass
        try:
            rect = wrapper.rectangle()
            width = int(rect.right) - int(rect.left)
            height = int(rect.bottom) - int(rect.top)
            if width < 240 or height < 160:
                return None
        except Exception:
            pass

        proc_name, proc_path = process_resolver(handle)
        return WindowCandidate(
            title=title,
            process_name=proc_name,
            process_path=proc_path,
            wrapper=wrapper,
        )

    def run(
        self,
        target: LauncherTarget,
        process_resolver,
        process_starter,
        button_finder,
        button_clicker,
        highlighter=None,
    ) -> LauncherReport:
        report = LauncherReport(ok=False, stage="start", message="init")
        target_path = str(target.path or "").strip()

        report.stage = "validate_target"
        if not target_path:
            report.message = "Пустой путь launcher target"
            return report
        if not os.path.exists(target_path):
            report.message = f"Файл не найден: {target_path}"
            return report
        self._log(report, f"target validated: {target_path}")

        report.stage = "ensure_process"
        process_starter(target_path)
        self._log(report, "process start requested")

        report.stage = "wait_window"
        deadline = time.time() + max(5, int(target.wait_timeout))
        best = None
        best_score = 0.0
        last_debug_ts = 0.0
        while time.time() < deadline:
            try:
                wrappers = self.desktop_factory().windows()
            except Exception as exc:
                report.message = f"Desktop enumeration failed: {exc}"
                return report

            candidates: List[WindowCandidate] = []
            for wrapper in wrappers:
                item = self._window_to_candidate(wrapper, process_resolver)
                if item:
                    candidates.append(item)

            best, best_score = select_best_window(candidates, target)
            if best is not None:
                break
            now = time.time()
            if now - last_debug_ts >= 2.5:
                self._log(
                    report,
                    f"wait-window: candidates={len(candidates)} best_score={best_score:.2f}",
                )
                last_debug_ts = now
            time.sleep(0.35)

        if best is None:
            report.stage = "verify_window"
            report.message = f"Окно не прошло верификацию (max confidence={best_score:.2f})"
            report.window_confidence = best_score
            return report

        report.stage = "verify_window"
        report.window_confidence = best_score
        self._log(
            report,
            f"window verified: title='{best.title}' process='{best.process_name}' score={best_score:.2f}",
        )

        report.stage = "find_button"
        control = button_finder(best.wrapper, target.button_text)
        if control is None:
            report.message = f"Кнопка '{target.button_text}' не найдена"
            return report
        self._log(report, f"button found: '{target.button_text}'")

        if target.highlight_only:
            report.stage = "highlight"
            if highlighter:
                highlighter(best.wrapper, control)
            report.ok = True
            report.preview_only = True
            report.message = "Подсветка выполнена, клик не выполнялся"
            return report

        if target.dry_run:
            report.stage = "dry_run"
            report.ok = True
            report.preview_only = True
            report.message = "Dry-run: верификация прошла, клик пропущен"
            return report

        report.stage = "click"
        clicked = button_clicker(control, best.wrapper)
        if not clicked:
            report.message = "Клик по кнопке отклонен или не выполнен"
            return report

        report.ok = True
        report.clicked = True
        report.message = "Клик выполнен безопасно"
        return report
