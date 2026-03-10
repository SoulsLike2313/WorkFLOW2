from __future__ import annotations

import json
import subprocess
import sys
import traceback
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


@dataclass
class HealthItem:
    title: str
    ok: bool
    details: str


@dataclass
class EnvironmentHealth:
    checks: List[HealthItem]

    @property
    def all_ok(self) -> bool:
        return all(item.ok for item in self.checks)


def _run_command(command: List[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )


def _run_quick_import_check(python_exe: Path, cwd: Path) -> bool:
    snippet = (
        "import importlib; "
        "mods=['playwright','PySide6']; "
        "all(importlib.import_module(m) for m in mods)"
    )
    result = _run_command([str(python_exe), "-c", snippet], cwd)
    return result.returncode == 0


def _run_playwright_check(python_exe: Path, cwd: Path) -> bool:
    snippet = (
        "from playwright.sync_api import sync_playwright;"
        "p=sync_playwright().start();"
        "b=p.chromium.launch(headless=True);"
        "b.close();"
        "p.stop()"
    )
    result = _run_command([str(python_exe), "-c", snippet], cwd)
    return result.returncode == 0


def inspect_environment(project_root: Path) -> EnvironmentHealth:
    root = Path(project_root)
    venv_python = root / ".venv" / "Scripts" / "python.exe"
    checks: List[HealthItem] = []

    checks.append(
        HealthItem(
            title="Python venv",
            ok=venv_python.exists(),
            details="Найден .venv/Scripts/python.exe" if venv_python.exists() else "Виртуальное окружение не найдено.",
        )
    )

    deps_ok = False
    playwright_ok = False

    if venv_python.exists():
        deps_ok = _run_quick_import_check(venv_python, root)
        checks.append(
            HealthItem(
                title="Зависимости",
                ok=deps_ok,
                details="playwright и PySide6 импортируются." if deps_ok else "Не хватает зависимостей.",
            )
        )

        if deps_ok:
            playwright_ok = _run_playwright_check(venv_python, root)
        checks.append(
            HealthItem(
                title="Playwright Chromium",
                ok=playwright_ok,
                details="Браузер Chromium доступен." if playwright_ok else "Chromium не установлен или не запускается.",
            )
        )
    else:
        checks.append(HealthItem(title="Зависимости", ok=False, details="Проверка пропущена (нет venv)."))
        checks.append(HealthItem(title="Playwright Chromium", ok=False, details="Проверка пропущена (нет venv)."))

    return EnvironmentHealth(checks=checks)


class SetupWorker(QThread):
    log_signal = Signal(str)
    done_signal = Signal(bool, str)

    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = Path(project_root)

    def run(self) -> None:
        try:
            root = self.project_root
            venv_python = root / ".venv" / "Scripts" / "python.exe"

            if not venv_python.exists():
                self._log("Создаю виртуальное окружение (.venv)...")
                create_result = _run_command([sys.executable, "-m", "venv", ".venv"], root)
                self._emit_process_output(create_result)
                if create_result.returncode != 0:
                    self.done_signal.emit(False, "Не удалось создать виртуальное окружение.")
                    return

            self._log("Устанавливаю зависимости из requirements.txt...")
            install_result = _run_command(
                [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
                root,
            )
            self._emit_process_output(install_result)
            if install_result.returncode != 0:
                self.done_signal.emit(False, "Не удалось обновить pip.")
                return

            requirements_result = _run_command(
                [str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"],
                root,
            )
            self._emit_process_output(requirements_result)
            if requirements_result.returncode != 0:
                self.done_signal.emit(False, "Не удалось установить зависимости.")
                return

            self._log("Устанавливаю браузер Chromium для Playwright...")
            playwright_result = _run_command(
                [str(venv_python), "-m", "playwright", "install", "chromium"],
                root,
            )
            self._emit_process_output(playwright_result)
            if playwright_result.returncode != 0:
                self.done_signal.emit(False, "Не удалось установить Playwright Chromium.")
                return

            state_payload = {
                "configured_at": datetime.utcnow().isoformat() + "Z",
                "status": "ok",
            }
            state_path = root / ".first_run_state.json"
            state_path.write_text(json.dumps(state_payload, ensure_ascii=False, indent=2), encoding="utf-8")

            self.done_signal.emit(True, "Автонастройка завершена успешно.")
        except Exception as error:
            details = "".join(traceback.format_exception(error))
            self.done_signal.emit(False, details)

    def _emit_process_output(self, result: subprocess.CompletedProcess[str]) -> None:
        if result.stdout:
            for line in result.stdout.splitlines():
                if line.strip():
                    self._log(line.strip())
        if result.stderr:
            for line in result.stderr.splitlines():
                if line.strip():
                    self._log(line.strip())

    def _log(self, message: str) -> None:
        self.log_signal.emit(message)


class FirstRunWizardDialog(QDialog):
    setup_completed = Signal(bool)

    def __init__(self, project_root: Path, parent: QWidget | None = None):
        super().__init__(parent)
        self.project_root = Path(project_root)
        self.worker: SetupWorker | None = None

        self.setWindowTitle("Мастер первого запуска")
        self.resize(700, 520)
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        hint = QLabel(
            "Проверка окружения и автоподготовка проекта:\n"
            "venv, зависимости и Chromium для Playwright."
        )
        hint.setWordWrap(True)
        root.addWidget(hint)

        self.status_grid = QGridLayout()
        self.status_grid.setHorizontalSpacing(12)
        self.status_grid.setVerticalSpacing(6)
        root.addLayout(self.status_grid)

        self.overall_label = QLabel("")
        root.addWidget(self.overall_label)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Здесь будет лог мастера...")
        root.addWidget(self.log_output, stretch=1)

        buttons = QHBoxLayout()
        self.check_button = QPushButton("Проверить")
        self.setup_button = QPushButton("Автонастройка")
        self.close_button = QPushButton("Закрыть")
        self.check_button.clicked.connect(self._refresh_health)
        self.setup_button.clicked.connect(self._run_setup)
        self.close_button.clicked.connect(self.accept)
        buttons.addWidget(self.check_button)
        buttons.addWidget(self.setup_button)
        buttons.addStretch(1)
        buttons.addWidget(self.close_button)
        root.addLayout(buttons)

        self._refresh_health()

    def _refresh_health(self) -> None:
        health = inspect_environment(self.project_root)
        self._render_checks(health)

    def _render_checks(self, health: EnvironmentHealth) -> None:
        while self.status_grid.count():
            item = self.status_grid.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        for row, item in enumerate(health.checks):
            title = QLabel(item.title)
            value = QLabel("OK" if item.ok else "Проблема")
            details = QLabel(item.details)
            value.setStyleSheet("font-weight: 700; color: #6fcf97;" if item.ok else "font-weight: 700; color: #eb5757;")
            details.setWordWrap(True)
            self.status_grid.addWidget(title, row, 0)
            self.status_grid.addWidget(value, row, 1)
            self.status_grid.addWidget(details, row, 2)

        self.overall_label.setText(
            "Система готова к запуску." if health.all_ok else "Нужна автонастройка перед запуском."
        )
        self.setup_button.setEnabled(not health.all_ok)

    def _run_setup(self) -> None:
        if self.worker and self.worker.isRunning():
            return

        self.log_output.append("Старт автонастройки...")
        self.check_button.setEnabled(False)
        self.setup_button.setEnabled(False)

        self.worker = SetupWorker(self.project_root)
        self.worker.log_signal.connect(self._append_log)
        self.worker.done_signal.connect(self._on_setup_done)
        self.worker.start()

    def _append_log(self, message: str) -> None:
        self.log_output.append(message)

    def _on_setup_done(self, success: bool, details: str) -> None:
        self.check_button.setEnabled(True)
        self._append_log(details)
        self._refresh_health()
        self.setup_completed.emit(success)
