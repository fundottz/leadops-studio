# Manager statuses and SLA reminders

Date: 2026-05-07

## What changed

The MVP Telegram bot now has a lightweight manager workflow after a lead is qualified and sent to the manager chat.

## Manager buttons

Every manager lead card gets inline buttons:

- **Взял** — manager accepted the lead for work.
- **Нужен звонок** — lead needs a call / manual follow-up.
- **Связались** — manager contacted the client; closes the operational SLA loop.
- **Нецелевой** — lead is not relevant; closes the SLA loop.
- **Дубль** — duplicate lead; closes the SLA loop.

The bot stores the selected status in `bot-state.json` under `manager_pending_leads` and writes an analytics event:

```json
{
  "event": "bot_manager_status_changed",
  "payload": {
    "status": "taken",
    "status_label": "Взял"
  }
}
```

## SLA reminder

If a new manager card stays in status `new` longer than the SLA threshold during work hours, the bot sends a reminder to the manager chat with the same status buttons.

Defaults:

- SLA threshold: `10` minutes.
- Work hours: `09:00–19:00` by server local time.

Environment overrides:

```bash
LEADOPS_SLA_MINUTES=10
LEADOPS_WORKDAY_START_HOUR=9
LEADOPS_WORKDAY_END_HOUR=19
```

Set `LEADOPS_SLA_MINUTES=0` to disable reminders for a pilot.

## Pilot value

This closes a visible MVP gap: the system no longer only forwards a lead, it also creates a minimal control loop for whether the manager actually took it into work.

For the first pilot report, these statuses can become simple metrics:

- new leads;
- taken to work;
- contacted;
- not target;
- duplicates;
- SLA reminders triggered.
