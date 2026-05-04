# ZAYAVKI-CRM.RU: domain + SEO launch plan

## Decision

Public brand: **Заявки CRM** / `zayavki-crm.ru`.
Internal project name can remain LeadOps Studio.

## Hosting recommendation

Start with GitHub Pages + custom domain.

Why:
- fast and free;
- static landing is enough for the first organic smoke test;
- GitHub Pages serves HTTPS and is usually indexable by Yandex/Google;
- moving to Russian hosting later is easy if indexing/accessibility is weak.

Fallback if RU indexing/access is poor:
- move static landing to Timeweb/Beget/REG.RU/VPS in RU zone;
- keep the same domain and paths;
- keep `robots.txt`, `sitemap.xml`, canonical URL unchanged.

## DNS for GitHub Pages

For apex `zayavki-crm.ru` add A records:

```text
@  A  185.199.108.153
@  A  185.199.109.153
@  A  185.199.110.153
@  A  185.199.111.153
```

For `www.zayavki-crm.ru` add CNAME:

```text
www  CNAME  fundottz.github.io.
```

In GitHub Pages custom domain set:

```text
zayavki-crm.ru
```

Enable HTTPS after DNS propagates.

## SEO smoke-test baseline

Already prepared in `demo/`:
- `CNAME`
- `robots.txt`
- `sitemap.xml`
- canonical URL
- RU title/description
- OpenGraph tags
- JSON-LD Service schema

## Organic test reality check

A one-page landing without content/backlinks can be indexed but traffic will likely be near zero. To test organic demand, add 3–5 narrow pages/articles next:

1. `/avtootvet-na-zayavki/` — автоответ на заявки с сайта и Telegram
2. `/telegram-bot-dlya-zayavok/` — Telegram-бот для обработки заявок
3. `/crm-dlya-remonta/` — CRM/автоответ для ремонта, окон, кухонь
4. `/skorost-otveta-na-lid/` — почему скорость ответа влияет на конверсию
5. `/mini-crm-dlya-malogo-biznesa/` — мини-CRM без внедрения

Minimum success signals after 2–4 weeks:
- pages indexed in Yandex Webmaster;
- non-zero impressions;
- at least a few organic clicks or bot starts.

If impressions are zero: content/SEO footprint insufficient or domain not indexed yet.
If impressions exist but CTR zero: adjust titles/snippets.
If clicks exist but no bot starts: landing/CTA mismatch.
