# LeadOps Studio: MVP-аналитика воронки

Дата: 2026-04-28
Статус: подготовлено к подключению, внешний счётчик не включён

## Цель

Минимально видеть, где ломается inbound-воронка:

1. визит на лендинг;
2. клик CTA в Telegram;
3. старт бота по deep link;
4. старт demo-flow;
5. завершение квалификации;
6. qualified lead: тёплый/горячий лид.

## Что уже добавлено

### Лендинг

Файл: `demo/index.html`.

Добавлены события:

| Событие | Когда срабатывает |
|---|---|
| `landing_cta_bot_click` | клик по CTA “Получить demo в Telegram” |
| `landing_demo_scroll` | клик “Показать demo на странице” |
| `landing_audit_click` | клик “Разобрать заявки” |
| `landing_demo_submit` | отправка demo-формы на странице |

CTA ведёт в бот с deep link:

```text
https://t.me/LeadOpsStudioBot?start=landing_demo
```

События сейчас пишутся в:

- `window.leadOpsEvents`;
- `localStorage.leadops_events` — последние 50 событий в браузере;
- `dataLayer`, если на странице есть GTM;
- `ym(...reachGoal...)`, если задан `window.LEADOPS_YM_COUNTER_ID` и подключена Яндекс.Метрика.

### Telegram-бот

Файл: `scripts/leadops_bot.py`.

Добавлены локальные события в `data/analytics-events.jsonl`:

| Событие | Когда срабатывает |
|---|---|
| `bot_deeplink_start` | пользователь пришёл по `/start landing_demo` |
| `bot_start` | показано welcome-сообщение |
| `bot_flow_start` | пользователь начал demo/audit-flow |
| `bot_lead_finished` | пользователь дошёл до конца квалификации |
| `bot_qualified_lead` | лид тёплый или горячий |
| `bot_human_request` | пользователь нажал “Связаться с человеком” |

Файл `data/analytics-events.jsonl` добавлен в `.gitignore`, чтобы не коммитить chat_id и сырые события.

## Как проверять вручную

1. Открыть публичный лендинг.
2. Нажать “Получить demo в Telegram”.
3. В Telegram нажать Start.
4. Пройти demo-flow до конца.
5. На сервере проверить:

```bash
tail -n 20 data/analytics-events.jsonl
```

Ожидаемая цепочка:

```text
bot_deeplink_start -> bot_start -> bot_flow_start -> bot_lead_finished -> bot_qualified_lead
```

Для browser-side событий без Метрики/GTM можно проверить в консоли страницы:

```js
JSON.parse(localStorage.getItem('leadops_events') || '[]')
```

## Что нужно от Андрея для полноценного внешнего запуска

Выбрать вариант счётчика:

1. Яндекс.Метрика — самый логичный вариант перед Директом.
2. Google Tag Manager — если нужен более универсальный слой.
3. Без внешнего счётчика на первом ручном тесте — достаточно bot-side JSONL и заявок.

Рекомендация: перед платным Директом подключить Яндекс.Метрику и передать counter id, чтобы события `landing_cta_bot_click` и `landing_demo_submit` стали целями.

## Что пока не делаем

- Не подключаем платные сервисы.
- Не отправляем события во внешние системы без подтверждения.
- Не коммитим приватные лиды, chat_id и логи.
