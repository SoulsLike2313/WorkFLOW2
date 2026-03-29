# EXECUTION NODE VALIDATION CHECKLIST V1

Перед стартом:
- [ ] GPT получил `02_EXECUTION_NODE_GPT_ENTRY_V1.md`
- [ ] Codex получил `03_EXECUTION_NODE_CODEX_ENTRY_V1.md`
- [ ] owner подтвердил корректность восстановления (yes)
- [ ] fixation prompt применен после owner yes

Во время работы:
- [ ] bounded scope соблюдается
- [ ] authority-sensitive действия не выполняются без escalation
- [ ] truth/gap маркируется честно
- [ ] нет fake realtime/fake completeness claims

Перед возвратом:
- [ ] review root собран
- [ ] chatgpt_transfer собран
- [ ] what worked/failed/unknown заполнено
- [ ] owner decisions выделены явно
- [ ] пакет готов к handoff на main machine
