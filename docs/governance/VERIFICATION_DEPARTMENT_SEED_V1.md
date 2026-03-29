# VERIFICATION_DEPARTMENT_SEED_V1

Статус:
- department_id: `verification_department`
- current_status: `SEED`
- labels_used: `PROVEN | ACTIVE | MAPPED | FROZEN | NOT YET IMPLEMENTED`

## Миссия

Подтверждать, что hardening реальный, а не косметический; блокировать false PASS и фиксировать достоверный quality verdict.

## Вход

1. engineering output bundles;
2. expected behavior/test contracts;
3. trust/gate constraints.

## Выход

1. verification evidence bundle;
2. blocker/incident bundle;
3. verification verdict note.

## Что обязан выпускать (seed minimum)

1. charter;
2. intake/output/blocker contracts;
3. completion note;
4. status card;
5. future evolution note.

## Чего делать не может

1. подменять owner final verdict;
2. закрывать критические дефекты “по договоренности”;
3. пропускать красные сигналы без эскалации.

## Кто руководит

1. Primarch-level verification lead.

## Нужен ли Primarch

Да, обязателен.

## Какие bundle types должен понимать

1. Verification Pack;
2. Test/Check Evidence Bundle;
3. Blocker/Incident Bundle;
4. Completion Candidate Bundle.

## Будущие возможности (`MAPPED`)

1. cross-product verification ladders;
2. contradiction auto-detection assist;
3. release-grade precheck pipelines.

