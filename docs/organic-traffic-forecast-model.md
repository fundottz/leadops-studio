# Organic forecast model — Zayavki CRM

## Goal

Estimate whether SEO/organic can produce non-zero qualified traffic for Zayavki CRM and create a forecast chain:

`impressions → visits → bot starts/leads → qualified leads → paid pilots`

## Important caveat

Exact demand must be validated in Yandex Wordstat / Direct Forecast. Without that, numeric traffic estimates are directional only.

## Query groups

1. Direct solution queries
- автоответ на заявки
- telegram бот для заявок
- бот для приема заявок
- crm для обработки заявок
- простая crm для заявок

2. Channel integration queries
- заявки с сайта в telegram
- форма сайта в telegram
- уведомления о заявках в telegram
- авито заявки в crm
- whatsapp заявки в crm

3. Niche CRM queries
- crm для ремонта
- crm для прораба
- crm для строительной компании
- crm для мебельного производства
- crm для кухни на заказ

4. Problem/education queries
- скорость ответа на лид
- быстрый ответ на заявку
- лиды теряются что делать
- автоматизация обработки заявок

## Landing strategy

Core landing pages:
- `/` — offer overview
- `/avtootvet-na-zayavki/`
- `/telegram-bot-dlya-zayavok/`
- `/crm-dlya-remonta/`

Next pages:
- `/zayavki-s-saita-v-telegram/`
- `/mini-crm-dlya-malogo-biznesa/`
- `/skorost-otveta-na-lid/`
- `/avito-zayavki-v-crm/`
- `/whatsapp-zayavki-v-crm/`

## Forecast method

For each query cluster:

1. Get monthly impressions from Wordstat / Direct Forecast.
2. Apply realistic target rank CTR:
   - position 1–3: 8–20%
   - position 4–10: 1–7%
   - position 11–30: 0.1–1%
   - new domain first 1–3 months: assume long-tail only unless backlinks/content improve
3. Apply landing conversion to bot start:
   - cold informational traffic: 0.3–1.5%
   - solution-aware traffic: 1–4%
   - niche commercial traffic: 2–6%
4. Apply bot start → qualified lead:
   - conservative: 15–25%
   - base: 25–40%
   - strong fit: 40–55%
5. Apply qualified lead → paid pilot:
   - cold organic conservative: 2–5%
   - base with follow-up: 5–12%

## Initial directional scenarios

These are placeholders until Wordstat/Direct Forecast data is filled.

### Conservative
- monthly addressable impressions captured: 200–500
- visits: 5–20
- bot starts: 0–1
- qualified leads: 0
- pilots: 0

Interpretation: SEO is background only; not enough for validation.

### Base after 10–20 useful pages + indexing
- monthly addressable impressions captured: 1,000–3,000
- visits: 30–150
- bot starts: 1–6
- qualified leads: 0–2
- pilots: 0–1

Interpretation: enough to see weak signal, not enough as primary acquisition.

### Upside with niche pages + backlinks + good snippets
- monthly addressable impressions captured: 5,000–15,000
- visits: 200–800
- bot starts: 6–32
- qualified leads: 2–12
- pilots: 0–2

Interpretation: can become a real channel if niche intent exists.

## What decides if the theme is dead

Not raw traffic alone. We need:

- Do commercial/niche queries have monthly demand?
- Are SERPs dominated by CRM giants or weak content pages?
- Can our pages rank for long-tail within 2–8 weeks?
- Do visitors start the bot?

If Wordstat shows low direct demand but channel queries (`заявки с сайта в telegram`, `форма сайта в telegram`) have demand, reposition SEO around integrations rather than “автоответ”.

If niche CRM queries have demand, build pages by vertical: ремонт, кухни/мебель, окна/двери, кондиционеры, B2B services.

## Data to collect next

Create a table with columns:

- query
- Wordstat broad frequency
- Wordstat quoted frequency
- Direct forecast impressions
- Direct forecast clicks at suggested bid
- CPC estimate
- SERP difficulty notes
- target page
- priority

