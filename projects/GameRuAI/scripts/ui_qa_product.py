from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


@dataclass(frozen=True)
class UiQaScenario:
    key: str
    screen_name: str
    state_name: str
    notes: str
    requires_loaded: bool = True


def scenario_catalog() -> list[UiQaScenario]:
    return [
        UiQaScenario(
            key="project_initial_empty",
            screen_name="Project",
            state_name="initial_empty",
            notes="Fresh launch before project selection; onboarding CTA visibility baseline.",
            requires_loaded=False,
        ),
        UiQaScenario(
            key="project_loaded_pipeline",
            screen_name="Project",
            state_name="pipeline_loaded_ready",
            notes="Project configured and full pipeline executed on demo fixture.",
        ),
        UiQaScenario(
            key="scan_manifest_loaded",
            screen_name="Scan",
            state_name="manifest_loaded",
            notes="Manifest and extracted file table visible after scan.",
        ),
        UiQaScenario(
            key="asset_tree_loaded",
            screen_name="Asset Explorer",
            state_name="tree_loaded_no_selection",
            notes="Asset tree and archive report visible without active item selection.",
        ),
        UiQaScenario(
            key="asset_active_selection",
            screen_name="Asset Explorer",
            state_name="active_selection_metadata",
            notes="Selected asset shows metadata and preview fallback/ready state.",
        ),
        UiQaScenario(
            key="entries_many_items",
            screen_name="Entries",
            state_name="many_items_loaded",
            notes="Entry table populated with large demo dataset.",
        ),
        UiQaScenario(
            key="entries_filtered_fr",
            screen_name="Entries",
            state_name="filtered_language_fr",
            notes="Language filter active for French rows.",
        ),
        UiQaScenario(
            key="entries_long_search",
            screen_name="Entries",
            state_name="long_search_query",
            notes="Long query with placeholders/tags applied to stress search toolbar layout.",
        ),
        UiQaScenario(
            key="language_hub_overview",
            screen_name="Language Hub",
            state_name="overview_loaded",
            notes="Language overview/queue/backend block populated from project metrics.",
        ),
        UiQaScenario(
            key="language_hub_review_focus",
            screen_name="Language Hub",
            state_name="review_and_stress_loaded",
            notes="Language review and localization stress blocks populated for manual triage.",
        ),
        UiQaScenario(
            key="translation_loaded",
            screen_name="Translation",
            state_name="loaded_translations",
            notes="Backend transparency and translated table populated.",
        ),
        UiQaScenario(
            key="translation_correction_prefilled",
            screen_name="Translation",
            state_name="correction_form_long_content",
            notes="Long manual correction text entered to stress form and typography fit.",
        ),
        UiQaScenario(
            key="voice_no_selection",
            screen_name="Voice",
            state_name="no_selection",
            notes="Voice attempts visible with no selected row.",
        ),
        UiQaScenario(
            key="voice_active_selection",
            screen_name="Voice",
            state_name="active_selection_details",
            notes="Voice preview/duration panels filled for selected attempt.",
        ),
        UiQaScenario(
            key="learning_loaded",
            screen_name="Learning",
            state_name="loaded_history",
            notes="Correction/adaptation history visible.",
        ),
        UiQaScenario(
            key="glossary_loaded",
            screen_name="Glossary",
            state_name="loaded_terms",
            notes="Glossary table and add-term controls visible.",
        ),
        UiQaScenario(
            key="qa_loaded",
            screen_name="QA",
            state_name="findings_loaded",
            notes="QA findings table populated from pipeline run.",
        ),
        UiQaScenario(
            key="reports_loaded",
            screen_name="Reports",
            state_name="dashboard_loaded",
            notes="Translation/language/QA summary widgets populated.",
        ),
        UiQaScenario(
            key="diagnostics_loaded",
            screen_name="Diagnostics",
            state_name="backend_metrics_loaded",
            notes="Backend diagnostics and report history visible.",
        ),
        UiQaScenario(
            key="export_log_loaded",
            screen_name="Export",
            state_name="export_log_loaded",
            notes="Export panel contains last export details and paths.",
        ),
        UiQaScenario(
            key="jobs_loaded",
            screen_name="Jobs / Logs",
            state_name="jobs_payload_loaded",
            notes="Jobs panel contains structured runtime payload.",
        ),
        UiQaScenario(
            key="live_scene_selected",
            screen_name="Live Demo",
            state_name="scene_selected_ready",
            notes="Live demo scene selector contains fixture scenes and active selection.",
        ),
        UiQaScenario(
            key="companion_idle",
            screen_name="Companion",
            state_name="idle_no_session",
            notes="Companion tab in safe idle mode without running session.",
        ),
        UiQaScenario(
            key="companion_invalid_exec",
            screen_name="Companion",
            state_name="configured_invalid_executable",
            notes="Companion fields prefilled with invalid executable for pre-launch validation checks.",
        ),
    ]


def expected_screen_names() -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for scenario in scenario_catalog():
        if scenario.screen_name in seen:
            continue
        seen.add(scenario.screen_name)
        ordered.append(scenario.screen_name)
    return ordered


def expected_state_keys() -> list[str]:
    return [f"{scenario.screen_name}|{scenario.state_name}" for scenario in scenario_catalog()]


def switch_to_screen(window: Any, screen_name: str) -> bool:
    for index in range(window.tabs.count()):
        if window.tabs.tabText(index) == screen_name:
            window.tabs.setCurrentIndex(index)
            return True
    return False


def _first_asset_leaf_item(tree_widget: Any) -> Any | None:
    from PySide6.QtCore import Qt

    queue = [tree_widget.topLevelItem(i) for i in range(tree_widget.topLevelItemCount())]
    while queue:
        item = queue.pop(0)
        if item is None:
            continue
        file_path = item.data(0, Qt.UserRole)
        if file_path:
            return item
        for child_index in range(item.childCount()):
            queue.append(item.child(child_index))
    return None


def prepare_loaded_state(window: Any, *, project_name: str) -> dict[str, Any]:
    cached = getattr(window, "_uiqa_loaded_summary", None)
    if isinstance(cached, dict):
        return cached

    game_root = window.services.config.paths.fixtures_root
    summary = window.services.pipeline_end_to_end(project_name, game_root)

    window.current_project_id = int(summary["project"]["id"])
    window.current_game_root = game_root
    window.project_panel.project_name_edit.setText(project_name)
    window.project_panel.game_path_edit.setText(str(game_root))
    window.project_panel.info_label.setText(
        "Pipeline done: "
        f"extracted={summary['extract']['entries_extracted']}, "
        f"translated={summary['translate']['translated']}, "
        f"voice={summary['voice']['voice_attempts']}"
    )
    window.scan_panel.show_manifest(summary.get("scan", {}))
    window.translation_panel.set_backend_status(summary.get("translate", {}))
    window.live_panel.load_scenes(window.services.load_scenes(game_root))
    window.companion_panel.watched_path_edit.setText(str(game_root))
    window.refresh_all_views()

    setattr(window, "_uiqa_loaded_summary", summary)
    return summary


def apply_scenario_state(window: Any, scenario: UiQaScenario, *, project_name: str, wait_fn: Callable[[], None]) -> bool:
    if not switch_to_screen(window, scenario.screen_name):
        return False

    if scenario.requires_loaded:
        prepare_loaded_state(window, project_name=project_name)

    if scenario.key == "project_initial_empty":
        # Keep startup state untouched.
        pass

    elif scenario.key == "project_loaded_pipeline":
        prepare_loaded_state(window, project_name=project_name)

    elif scenario.key == "scan_manifest_loaded":
        prepare_loaded_state(window, project_name=project_name)
        if not window.scan_panel.manifest_view.toPlainText().strip():
            summary = getattr(window, "_uiqa_loaded_summary", {})
            if isinstance(summary, dict):
                window.scan_panel.show_manifest(summary.get("scan", {}))

    elif scenario.key == "asset_tree_loaded":
        window.asset_panel.filter_combo.setCurrentText("all")
        window.refresh_assets()
        window.asset_panel.resource_tree.clearSelection()

    elif scenario.key == "asset_active_selection":
        window.asset_panel.filter_combo.setCurrentText("all")
        window.refresh_assets()
        leaf = _first_asset_leaf_item(window.asset_panel.resource_tree)
        if leaf is not None:
            window.asset_panel.resource_tree.setCurrentItem(leaf)
            window.on_asset_selected()

    elif scenario.key == "entries_many_items":
        window.entries_panel.lang_filter.setCurrentText("all")
        window.entries_panel.search_edit.setText("")
        window.refresh_entries()

    elif scenario.key == "entries_filtered_fr":
        window.entries_panel.search_edit.setText("")
        index = window.entries_panel.lang_filter.findText("fr")
        if index >= 0:
            window.entries_panel.lang_filter.setCurrentIndex(index)
        window.refresh_entries()

    elif scenario.key == "entries_long_search":
        window.entries_panel.lang_filter.setCurrentText("all")
        window.entries_panel.search_edit.setText("mission %PLAYER_NAME% {money} [E] <b>radio chatter</b> sidequest long context")
        window.refresh_entries()

    elif scenario.key == "translation_loaded":
        window.refresh_translations()

    elif scenario.key == "translation_correction_prefilled":
        window.refresh_translations()
        rows = window.services.repo.list_translations(window.current_project_id) if window.current_project_id else []
        if rows:
            first = rows[0]
            entry_id = first.get("entry_id")
            if entry_id is not None:
                window.translation_panel.correction_entry_id.setText(str(entry_id))
        window.translation_panel.correction_text.setPlainText(
            "Очень длинная ручная правка перевода для проверки читаемости формы и поведения поля при большом объеме текста."
        )
        window.translation_panel.correction_note.setText("UI QA prefill state")

    elif scenario.key == "language_hub_overview":
        window.refresh_language_hub()

    elif scenario.key == "language_hub_review_focus":
        window.refresh_language_hub()
        if window.language_hub_panel.review_table.rowCount() > 0:
            window.language_hub_panel.review_table.setCurrentCell(0, 0)
        if window.language_hub_panel.stress_table.rowCount() > 0:
            window.language_hub_panel.stress_table.setCurrentCell(0, 0)

    elif scenario.key == "voice_no_selection":
        window.refresh_voice()
        window.voice_panel.attempts_table.clearSelection()

    elif scenario.key == "voice_active_selection":
        window.refresh_voice()
        if window.voice_panel.attempts_table.rowCount() > 0:
            window.voice_panel.attempts_table.setCurrentCell(0, 0)
            window.on_voice_attempt_selected()

    elif scenario.key == "learning_loaded":
        window.refresh_learning()

    elif scenario.key == "glossary_loaded":
        window.refresh_glossary()

    elif scenario.key == "qa_loaded":
        window.refresh_qa()

    elif scenario.key == "reports_loaded":
        window.refresh_reports()

    elif scenario.key == "diagnostics_loaded":
        window.refresh_diagnostics()

    elif scenario.key == "export_log_loaded":
        if window.current_project_id is not None:
            export_result = window.services.export(window.current_project_id)
            window.export_panel.info.setPlainText(
                "\n".join(
                    [
                        f"Export directory: {export_result.output_dir}",
                        f"Manifest: {export_result.manifest_path}",
                        f"Diff report: {export_result.diff_report_path}",
                        f"Translated entries: {export_result.translated_entries}",
                        f"Voiced entries: {export_result.voiced_entries}",
                    ]
                )
            )
            window.refresh_reports()
            window.refresh_diagnostics()
            window.refresh_jobs()

    elif scenario.key == "jobs_loaded":
        window.refresh_jobs()

    elif scenario.key == "live_scene_selected":
        window.live_panel.load_scenes(window.services.load_scenes(window.current_game_root))
        if window.live_panel.scene_combo.count() > 0:
            window.live_panel.scene_combo.setCurrentIndex(0)

    elif scenario.key == "companion_idle":
        window.companion_panel.executable_edit.setText("")
        window.companion_panel.watched_path_edit.setText(str(window.current_game_root))
        window.companion_panel.args_edit.setText("")
        window.refresh_companion()

    elif scenario.key == "companion_invalid_exec":
        invalid_exec = window.current_game_root / "missing_game.exe"
        window.companion_panel.executable_edit.setText(str(invalid_exec))
        window.companion_panel.watched_path_edit.setText(str(window.current_game_root))
        window.companion_panel.args_edit.setText("--windowed")
        window.refresh_companion()

    wait_fn()
    return True
