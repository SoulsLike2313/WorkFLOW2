# UI Layout Bug Report

## Таблица дефектов

| Экран | Блок | Проблема | Severity | Вероятная причина | Стратегия фикса | Статус |
|---|---|---|---|---|---|---|
| All | Page transition layer | Пустые/битые зоны при быстром переключении | critical | Неочищенный opacity effect | Явный cleanup fade target при stop/finished | Fixed |
| Sessions | Session frame + status chips | Clipping статусов на `1366x768` и `1280x800` | major | Длинные строки + ограниченная ширина | Сокращённые статусы + выравнивание + scroll container | Fixed |
| Sessions | Нижняя зона preview | Визуальный срез при плотном окне | major | Мин. высота preview + плотная вертикальная композиция | Коррекция min-size и контейнеризации | Fixed |
| Analytics | Validation expectations | Ложный critical “missing CTA” | major | Валидация ждала кнопку вместо label-индикатора | Разделение required buttons и required labels | Fixed |
| Workspace split | Main area vs context panel | Риск конфликтной ширины колонок на resize | major | Недостаточная ребалансировка split | Явный `rebalance_main_splitter()` + guards | Fixed |

## Текущий остаток
- Critical layout-багов по текущим инвариантам не найдено.
- Major layout-багов по текущим инвариантам не найдено.
- Остаётся обязательный ручной visual acceptance на реальном DPI/шрифтах.
