# Заявки CRM / LeadOps Studio

Публичный бренд: **Заявки CRM** (`zayavki-crm.ru`). Внутреннее рабочее имя: LeadOps Studio.

Мини-контакт-центр для малого сервисного бизнеса: входящая заявка из Telegram/WhatsApp/формы → быстрый первый ответ → квалификация → карточка горячей заявки владельцу/менеджеру.

## Текущий статус

Проект в стадии проверки гипотезы.

Готово:

- публичный demo-лендинг: https://fundottz.github.io/leadops-studio/; целевой домен: https://zayavki-crm.ru/
- Telegram-бот: `@LeadOpsStudioBot` (текущий handle; текст обновляется под бренд «Заявки CRM»)
- MVP-flow: бот собирает вводные, сохраняет лид и отправляет карточку менеджеру
- multi-client backend: один движок может запускать несколько клиентских Telegram-ботов с разными сценариями, брендом и manager chat

Рабочая воронка:

1. Лендинг объясняет оффер “первый ответ за 1–2 минуты”.
2. CTA ведёт в Telegram-бота.
3. Бот показывает mini-demo и квалифицирует заявку.
4. Горячий лид эскалируется владельцу/команде.
5. Следующий шаг: ручная проверка на 3–5 тёплых контактах или малый рекламный smoke test после подключения аналитики.

## Структура

- `docs/` — стратегия, лендинг, бюджет, bot-flow, операционная модель.
- `data/` — shortlist компаний и outreach targets.
- `demo/` — локальная demo-страница.
- `scripts/` — вспомогательные скрипты.

## Demo

Публичная версия: https://fundottz.github.io/leadops-studio/

Локально:

```bash
./scripts/serve-demo.sh 8787
```

Открыть: http://127.0.0.1:8787

## Multi-client bot backend

Для первого платного клиента рекомендуем схему: отдельный Telegram-бот под бренд клиента, общий backend LeadOps.

Быстрый старт:

```bash
cp data/clients.example.json data/clients.local.json
./scripts/run-bot.sh --clients-config data/clients.local.json --tenant vasya_kitchens --check
./scripts/run-bot.sh --clients-config data/clients.local.json --tenant vasya_kitchens --set-commands
./scripts/run-bot.sh --clients-config data/clients.local.json
```

Инструкция подключения клиента за 5 минут: `docs/client-onboarding-5min.md`.

## Важные ограничения

- Не хранить здесь секреты, bot tokens, личные контакты и приватные данные.
- Внешние действия: реклама, сообщения компаниям, использование личных контактов — только после явного подтверждения.

## Операционные правила

- Правила ведения проекта и commit policy: `docs/operating-rules.md`.
