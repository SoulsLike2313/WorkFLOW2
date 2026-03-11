from voice_launcher_app.ui.controller import UiController, UiControllerDeps


class DummyRoot:
    def after(self, _delay, fn):
        fn()


class DummyVar:
    def __init__(self, value=""):
        self.value = value

    def set(self, value):
        self.value = value

    def get(self):
        return self.value


class DummyNotebook:
    def __init__(self):
        self.hidden = []
        self.added = []

    def hide(self, tab):
        self.hidden.append(tab)

    def add(self, tab, text=""):
        self.added.append((tab, text))


class DummyListbox:
    def __init__(self):
        self.items = []

    def delete(self, _start, _end):
        self.items = []

    def insert(self, _where, text):
        self.items.append(text)


def test_apply_mode_updates_notebook_and_label():
    settings = {"simple_mode": True}
    statuses = []
    controller = UiController(
        UiControllerDeps(
            root=DummyRoot(),
            settings=settings,
            save_settings=lambda: None,
            set_status=lambda text: statuses.append(text),
            heard_history=[],
            action_history=[],
        )
    )
    notebook = DummyNotebook()
    mode_var = DummyVar()
    controller.bind_mode_controls(notebook=notebook, advanced_tab="audio_tab", mode_text_var=mode_var)

    controller.apply_mode()
    assert notebook.hidden == ["audio_tab"]
    assert "Простой" in mode_var.get()

    settings["simple_mode"] = False
    controller.apply_mode()
    assert notebook.added[-1] == ("audio_tab", "Расширенный")
    assert "Расширенный" in mode_var.get()


def test_toggle_mode_persists_and_sets_status():
    settings = {"simple_mode": True}
    save_calls = []
    statuses = []
    controller = UiController(
        UiControllerDeps(
            root=DummyRoot(),
            settings=settings,
            save_settings=lambda: save_calls.append(True),
            set_status=lambda text: statuses.append(text),
            heard_history=[],
            action_history=[],
        )
    )
    controller.bind_mode_controls(notebook=DummyNotebook(), advanced_tab="audio_tab", mode_text_var=DummyVar())

    controller.toggle_mode()
    assert settings["simple_mode"] is False
    assert save_calls
    assert any("Режим интерфейса сохранен" in text for text in statuses)


def test_push_last_phrase_and_action_refresh_history_widgets():
    heard = []
    actions = []
    controller = UiController(
        UiControllerDeps(
            root=DummyRoot(),
            settings={"simple_mode": True},
            save_settings=lambda: None,
            set_status=lambda _text: None,
            heard_history=heard,
            action_history=actions,
        )
    )
    events = DummyListbox()
    phrase_var = DummyVar()
    action_var = DummyVar()
    controller.bind_history_widgets(events_listbox=events, last_phrase_var=phrase_var, last_action_var=action_var)

    controller.push_last_phrase("танки")
    controller.push_last_action("запуск выполнен")

    assert heard == ["танки"]
    assert actions == ["запуск выполнен"]
    assert "танки" in phrase_var.get()
    assert "запуск выполнен" in action_var.get()
    assert any(item.startswith("Фраза:") for item in events.items)
    assert any(item.startswith("Действие:") for item in events.items)
