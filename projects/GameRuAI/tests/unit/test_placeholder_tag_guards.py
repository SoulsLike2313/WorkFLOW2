from __future__ import annotations

from app.normalizers.placeholder_guard import extract_placeholders, placeholders_preserved
from app.normalizers.tag_guard import extract_tags, tags_preserved


def test_placeholder_detection_and_preservation() -> None:
    source = "Press [E], %PLAYER_NAME% has {money} credits."
    translated_ok = "Нажми [E], %PLAYER_NAME% получил {money} кредитов."
    translated_bad = "Нажми кнопку, игрок получил кредиты."
    assert set(extract_placeholders(source)) == {"[E]", "%PLAYER_NAME%", "{money}"}
    assert placeholders_preserved(source, translated_ok)
    assert not placeholders_preserved(source, translated_bad)


def test_tag_detection_and_preservation() -> None:
    source = "<b>Warning</b> Reactor unstable."
    translated_ok = "<b>Предупреждение</b> Реактор нестабилен."
    translated_bad = "Предупреждение: реактор нестабилен."
    assert "<b>" in extract_tags(source)
    assert tags_preserved(source, translated_ok)
    assert not tags_preserved(source, translated_bad)
