# EXECUTION NODE ACCEPTANCE FLOW V1

Точный порядок запуска:

1. owner отправляет GPT entry:
- `02_EXECUTION_NODE_GPT_ENTRY_V1.md`

2. owner отправляет Codex entry:
- `03_EXECUTION_NODE_CODEX_ENTRY_V1.md`

3. Codex дает понимание режима в bundle-форме:
- права/лимиты;
- scope миссии;
- что будет сделано первым.

4. owner передает этот Codex bundle в GPT.

5. GPT задает owner контрольный вопрос:
- "подтверждаешь восстановление контекста и границ?"

6. owner отвечает yes/no.

7. только при yes GPT выдает:
- `05_EXECUTION_NODE_FIXATION_PROMPT_V1.md`

8. Codex фиксирует execution-node entrypoint в локальный continuity контекст.

9. после выполнения миссии ноутбук формирует return bundle и отправляет на main machine.
