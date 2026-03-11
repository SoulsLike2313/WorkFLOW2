from __future__ import annotations


def build_diff_report(*, translated: list[dict], voice_attempts: list[dict]) -> str:
    lines = [
        "# GameRuAI Export Diff Report",
        "",
        f"- Translated lines: {len(translated)}",
        f"- Voice attempts: {len(voice_attempts)}",
        "",
        "## Sample translations",
    ]
    for item in translated[:20]:
        lines.append(
            f"- `{item.get('line_id')}`: `{item.get('source_text', '')[:55]}` -> `{item.get('translated_text', '')[:55]}`"
        )
    lines.extend(["", "## Sample voice attempts"])
    for item in voice_attempts[:20]:
        lines.append(
            f"- `{item.get('line_id')}` speaker `{item.get('speaker_id')}` status `{item.get('status')}` output `{item.get('output_voice_path')}`"
        )
    return "\n".join(lines) + "\n"
