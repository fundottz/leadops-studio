#!/usr/bin/env python3
"""Minimal Telegram polling bot for LeadOps Studio.

No third-party dependencies. Secrets are loaded from .env and must not be committed.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT / ".env"
STATE_PATH = ROOT / "data" / "bot-state.json"
LEADS_PATH = ROOT / "data" / "leads.jsonl"

QUESTIONS = [
    {
        "key": "niche",
        "text": "1/6. Какая у вас ниша?",
        "options": [
            "клиника / стоматология / косметология",
            "ремонт / кухни / окна",
            "юридические услуги",
            "недвижимость",
            "B2B-услуги",
            "другое",
        ],
    },
    {
        "key": "channels",
        "text": "2/6. Откуда приходят заявки?",
        "options": ["сайт / форма", "квиз", "Telegram", "WhatsApp", "Авито", "Яндекс.Директ", "другое"],
    },
    {
        "key": "volume",
        "text": "3/6. Сколько заявок примерно в месяц?",
        "options": ["до 20", "20–50", "50–150", "150+", "пока не знаю"],
    },
    {
        "key": "response_time",
        "text": "4/6. Как быстро сейчас отвечаете на заявку?",
        "options": ["до 5 минут", "5–30 минут", "30–60 минут", "больше часа", "зависит от смены / менеджера"],
    },
    {
        "key": "pain",
        "text": "5/6. Что болит сильнее всего?",
        "options": [
            "долго отвечаем",
            "заявки теряются",
            "не фиксируем в CRM",
            "нет квалификации до менеджера",
            "ночь / выходные провисают",
            "хотим понять потери",
        ],
    },
    {
        "key": "next_step",
        "text": "6/6. Что удобно дальше?",
        "options": ["получить demo в Telegram", "созвон 10–15 минут", "узнать стоимость пилота", "просто посмотреть пример"],
    },
]

COMMANDS = [
    {"command": "start", "description": "Начать разбор заявки"},
    {"command": "demo", "description": "Собрать demo-сценарий"},
    {"command": "audit", "description": "Разобрать обработку заявок"},
    {"command": "pilot", "description": "Узнать про пилот"},
]


def load_env() -> dict[str, str]:
    values = dict(os.environ)
    if ENV_PATH.exists():
        for raw in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    return values


class TelegramBot:
    def __init__(self, token: str, manager_chat_id: str | None = None) -> None:
        self.token = token
        self.manager_chat_id = manager_chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.state = self.load_state()

    def load_state(self) -> dict[str, Any]:
        if STATE_PATH.exists():
            try:
                return json.loads(STATE_PATH.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return {"offset": 0, "sessions": {}}
        return {"offset": 0, "sessions": {}}

    def save_state(self) -> None:
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = STATE_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(STATE_PATH)

    def api(self, method: str, payload: dict[str, Any] | None = None, timeout: int = 30) -> dict[str, Any]:
        body = json.dumps(payload or {}).encode("utf-8")
        req = Request(
            f"{self.base_url}/{method}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            data = exc.read().decode("utf-8", errors="replace")
            try:
                parsed = json.loads(data)
            except json.JSONDecodeError:
                parsed = {"description": data[:300]}
            return {"ok": False, "error_code": exc.code, **parsed}
        except URLError as exc:
            return {"ok": False, "description": str(exc.reason)}

    def keyboard(self, rows: list[list[tuple[str, str]]]) -> dict[str, Any]:
        return {
            "inline_keyboard": [
                [{"text": text, "callback_data": callback} for text, callback in row]
                for row in rows
            ]
        }

    def send(self, chat_id: int | str, text: str, rows: list[list[tuple[str, str]]] | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
        if rows:
            payload["reply_markup"] = self.keyboard(rows)
        return self.api("sendMessage", payload)

    def answer_callback(self, callback_id: str) -> None:
        self.api("answerCallbackQuery", {"callback_query_id": callback_id}, timeout=10)

    def set_commands(self) -> dict[str, Any]:
        return self.api("setMyCommands", {"commands": COMMANDS})

    def get_me(self) -> dict[str, Any]:
        return self.api("getMe")

    def welcome(self, chat_id: int) -> None:
        self.send(
            chat_id,
            "Привет! Это LeadOps Studio.\n\n"
            "Покажем, как может выглядеть быстрый автоответ на заявку в вашей нише: "
            "клиент получает ответ за 1–2 минуты, бот собирает вводные, менеджер получает готовую карточку лида.\n\n"
            "Что сделать?",
            [
                [("Собрать demo-сценарий", "start_demo")],
                [("Разобрать мою воронку", "start_audit")],
                [("Узнать про пилот", "pilot_info")],
            ],
        )

    def pilot_info(self, chat_id: int) -> None:
        self.send(
            chat_id,
            "Пилот занимает 1–3 дня на запуск и 2 недели на проверку.\n\n"
            "Обычно начинаем с Telegram + таблицы/CRM: автоответ, 3–6 вопросов, карточка лида менеджеру.\n\n"
            "Стоимость первого пилота: 15–30 тыс ₽ — зависит от каналов заявок и интеграций.",
            [[("Оценить мой кейс", "start_demo")], [("Показать demo", "start_demo")]],
        )

    def start_flow(self, chat_id: int, source: str) -> None:
        self.state.setdefault("sessions", {})[str(chat_id)] = {
            "source": source,
            "step": 0,
            "answers": {},
            "started_at": int(time.time()),
        }
        self.save_state()
        self.ask_question(chat_id)

    def ask_question(self, chat_id: int) -> None:
        session = self.state.get("sessions", {}).get(str(chat_id))
        if not session:
            self.welcome(chat_id)
            return
        step = int(session.get("step", 0))
        if step >= len(QUESTIONS):
            self.finish_flow(chat_id)
            return
        question = QUESTIONS[step]
        rows = [[(option, f"answer:{step}:{idx}")] for idx, option in enumerate(question["options"])]
        self.send(chat_id, question["text"], rows)

    def handle_answer(self, chat_id: int, step: int, option_idx: int) -> None:
        session = self.state.get("sessions", {}).get(str(chat_id))
        if not session:
            self.welcome(chat_id)
            return
        if step != int(session.get("step", 0)) or step >= len(QUESTIONS):
            self.ask_question(chat_id)
            return
        question = QUESTIONS[step]
        try:
            answer = question["options"][option_idx]
        except IndexError:
            self.ask_question(chat_id)
            return
        session.setdefault("answers", {})[question["key"]] = answer
        session["step"] = step + 1
        self.save_state()
        self.ask_question(chat_id)

    def score(self, answers: dict[str, str]) -> tuple[str, int]:
        points = 0
        if answers.get("volume") in {"20–50", "50–150", "150+"}:
            points += 2
        if answers.get("response_time") in {"5–30 минут", "30–60 минут", "больше часа", "зависит от смены / менеджера"}:
            points += 2
        if answers.get("channels") in {"сайт / форма", "квиз", "Telegram", "WhatsApp", "Авито", "Яндекс.Директ"}:
            points += 1
        if answers.get("next_step") in {"получить demo в Telegram", "созвон 10–15 минут", "узнать стоимость пилота"}:
            points += 2
        if points >= 5:
            return "горячий", points
        if points >= 3:
            return "тёплый", points
        return "холодный", points

    def finish_flow(self, chat_id: int) -> None:
        session = self.state.get("sessions", {}).get(str(chat_id), {})
        answers: dict[str, str] = session.get("answers", {})
        lead_status, points = self.score(answers)
        preview = (
            "Понял. Для вашей ниши demo-сценарий будет такой:\n\n"
            "1. Клиент оставляет заявку.\n"
            "2. Бот отвечает за 1–2 минуты.\n"
            "3. Уточняет услугу, срочность, удобный контакт и детали заказа.\n"
            "4. Менеджер получает карточку лида в Telegram/CRM.\n\n"
            "Если хотите, можем показать такой flow на вашем примере и оценить, где сейчас теряются заявки."
        )
        self.send(
            chat_id,
            preview,
            [[("Показать demo на моём примере", "request_demo")], [("Узнать стоимость пилота", "pilot_info")]],
        )
        self.store_lead(chat_id, answers, lead_status, points)
        self.notify_manager(chat_id, answers, lead_status, points)
        self.state.get("sessions", {}).pop(str(chat_id), None)
        self.save_state()

    def store_lead(self, chat_id: int, answers: dict[str, str], status: str, points: int) -> None:
        LEADS_PATH.parent.mkdir(parents=True, exist_ok=True)
        record = {
            "ts": int(time.time()),
            "chat_id": chat_id,
            "status": status,
            "score": points,
            "answers": answers,
        }
        with LEADS_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def notify_manager(self, chat_id: int, answers: dict[str, str], status: str, points: int) -> None:
        if not self.manager_chat_id:
            return
        if str(self.manager_chat_id) == str(chat_id):
            # In local tests the owner may be both the client and manager.
            # Do not leak the internal lead card into the client conversation.
            print(f"manager_notify_skipped_same_chat chat_id={chat_id} status={status} score={points}", flush=True)
            return
        text = (
            "Новый лид LeadOps Studio\n\n"
            f"Статус: {status} ({points} баллов)\n"
            f"Ниша: {answers.get('niche', '-')}\n"
            f"Каналы заявок: {answers.get('channels', '-')}\n"
            f"Объём заявок: {answers.get('volume', '-')}\n"
            f"Скорость ответа: {answers.get('response_time', '-')}\n"
            f"Боль: {answers.get('pain', '-')}\n"
            f"Интерес: {answers.get('next_step', '-')}\n"
            f"Telegram chat_id: {chat_id}\n\n"
            "Рекомендация: если лид тёплый/горячий — подключиться и предложить demo/пилот."
        )
        result = self.send(self.manager_chat_id, text)
        if not result.get("ok"):
            print(f"manager_notify_failed: {result.get('description', 'unknown error')}", file=sys.stderr)

    def request_demo(self, chat_id: int) -> None:
        self.send(
            chat_id,
            "Супер. Напишите в одном сообщении: нишу, сайт/канал заявок и что сейчас не устраивает. "
            "Мы подготовим короткий demo-сценарий под ваш пример.",
        )

    def handle_text(self, message: dict[str, Any]) -> None:
        chat_id = message["chat"]["id"]
        text = (message.get("text") or "").strip()
        if text in {"/start", "start"}:
            self.welcome(chat_id)
        elif text == "/demo":
            self.start_flow(chat_id, "demo_command")
        elif text == "/audit":
            self.start_flow(chat_id, "audit_command")
        elif text == "/pilot":
            self.pilot_info(chat_id)
        else:
            self.send(
                chat_id,
                "Принял. Если хотите собрать demo-сценарий, нажмите кнопку ниже.",
                [[("Собрать demo-сценарий", "start_demo")], [("Узнать про пилот", "pilot_info")]],
            )

    def handle_callback(self, query: dict[str, Any]) -> None:
        self.answer_callback(query["id"])
        chat_id = query["message"]["chat"]["id"]
        data = query.get("data") or ""
        if data in {"start_demo", "start_audit"}:
            self.start_flow(chat_id, data)
        elif data == "pilot_info":
            self.pilot_info(chat_id)
        elif data == "request_demo":
            self.request_demo(chat_id)
        elif data.startswith("answer:"):
            _, step_raw, idx_raw = data.split(":", 2)
            self.handle_answer(chat_id, int(step_raw), int(idx_raw))
        else:
            self.welcome(chat_id)

    def process_update(self, update: dict[str, Any]) -> None:
        if "message" in update:
            self.handle_text(update["message"])
        elif "callback_query" in update:
            self.handle_callback(update["callback_query"])

    def poll_once(self, timeout: int = 25) -> int:
        payload = {"timeout": timeout, "offset": int(self.state.get("offset", 0))}
        result = self.api("getUpdates", payload, timeout=timeout + 10)
        if not result.get("ok"):
            print(f"get_updates_failed: {result.get('description', 'unknown error')}", file=sys.stderr)
            return 1
        updates = result.get("result", [])
        for update in updates:
            self.state["offset"] = update["update_id"] + 1
            self.process_update(update)
        self.save_state()
        return len(updates)

    def run(self) -> None:
        print("leadops_bot_started", flush=True)
        stopping = False

        def stop(_signum: int, _frame: Any) -> None:
            nonlocal stopping
            stopping = True

        signal.signal(signal.SIGTERM, stop)
        signal.signal(signal.SIGINT, stop)
        while not stopping:
            self.poll_once(timeout=25)
        print("leadops_bot_stopped", flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Validate token with getMe")
    parser.add_argument("--set-commands", action="store_true", help="Register Telegram bot commands")
    parser.add_argument("--once", action="store_true", help="Process updates once and exit")
    args = parser.parse_args()

    env = load_env()
    token = env.get("LEADOPS_BOT_TOKEN")
    if not token:
        print("LEADOPS_BOT_TOKEN is not set", file=sys.stderr)
        return 2
    bot = TelegramBot(token=token, manager_chat_id=env.get("LEADOPS_MANAGER_CHAT_ID"))

    if args.check:
        result = bot.get_me()
        if not result.get("ok"):
            print(json.dumps({"ok": False, "description": result.get("description")}, ensure_ascii=False))
            return 1
        info = result.get("result", {})
        print(json.dumps({"ok": True, "username": info.get("username"), "first_name": info.get("first_name")}, ensure_ascii=False))
        return 0
    if args.set_commands:
        result = bot.set_commands()
        print(json.dumps({"ok": bool(result.get("ok")), "description": result.get("description")}, ensure_ascii=False))
        return 0 if result.get("ok") else 1
    if args.once:
        bot.poll_once(timeout=1)
        return 0
    bot.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
