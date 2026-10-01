"""Telegram-бот"""
import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import Command

from config import BOT_TOKEN, OWNER_CHAT_ID
from database import (
    get_client, create_client, update_state, update_summary,
    increment_message_count, save_message, get_history, check_subscription,
    update_stats, get_stats,
)
from agent import process_message
from actions import parse_action, call_n8n
from message_router import (
    send_to_client, send_to_owner, send_to_team, send_to_reports,
    format_escalation, format_team_notification, format_report,
)
from self_learning import save_lesson

logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    chat_id = message.chat.id
    client = get_client(chat_id)
    if not client:
        create_client(chat_id)
        update_stats("new_clients")
    update_state(chat_id, "greeting")
    await send_to_client(bot, chat_id,
        "Привет! Я ИИ-ассистент турагента. Помогу подобрать тур, "
        "ответить на вопросы и передать вас менеджеру для брони. "
        "Напишите, куда хотите поехать!")
    await send_to_team(bot,
        format_team_notification(chat_id, "new", "greeting", "Новый клиент"))


@dp.message(Command("resume"))
async def cmd_resume(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("Использование: /resume <chat_id>")
        return
    try:
        client_id = int(parts[1])
    except ValueError:
        await message.reply("chat_id должен быть числом")
        return
    if message.chat.id != OWNER_CHAT_ID:
        await message.reply("Команда доступна только владельцу")
        return
    update_state(client_id, "greeting")
    await message.reply(f"Бот возобновлён для клиента {client_id}")
    await send_to_client(bot, client_id, "Менеджер освободился! Продолжаем?")


@dp.message(Command("pause"))
async def cmd_pause(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.reply("Использование: /pause <chat_id>")
        return
    try:
        client_id = int(parts[1])
    except ValueError:
        await message.reply("chat_id должен быть числом")
        return
    if message.chat.id != OWNER_CHAT_ID:
        await message.reply("Команда доступна только владельцу")
        return
    update_state(client_id, "escalated")
    await message.reply(f"Бот приостановлен для клиента {client_id}")


@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.chat.id != OWNER_CHAT_ID:
        await message.reply("Команда доступна только владельцу")
        return
    stats = get_stats()
    await message.reply(format_report(stats))


@dp.message(Command("report"))
async def cmd_report(message: Message):
    if message.chat.id != OWNER_CHAT_ID:
        await message.reply("Команда доступна только владельцу")
        return
    stats = get_stats()
    await send_to_reports(bot, format_report(stats))


@dp.message(F.text)
async def handle_message(message: Message):
    chat_id = message.chat.id
    text = message.text
    if text and text.startswith("/"):
        return
    if not check_subscription(chat_id):
        await send_to_client(bot, chat_id,
            "Лимит бесплатных сообщений исчерпан. Для продолжения обратитесь к менеджеру.")
        return
    client = get_client(chat_id)
    if not client:
        client = create_client(chat_id)
        update_stats("new_clients")
    state = client["state"]
    summary = client["history_summary"]
    if state == "escalated":
        save_message(chat_id, "user", text)
        await send_to_client(bot, chat_id,
            "Ваш запрос передан менеджеру. Он свяжется с вами в ближайшее время.")
        return
    save_message(chat_id, "user", text)
    increment_message_count(chat_id)
    update_stats("messages_total")
    history = get_history(chat_id, limit=10)
    result = await asyncio.to_thread(
        process_message, chat_id, text, state, history, summary)
    action_data = parse_action(result["raw_reply"])
    reply_text = action_data["clean_text"] if action_data else result["reply"]
    await send_to_client(bot, chat_id, reply_text)
    save_message(chat_id, "assistant", reply_text, result["emotion"])
    new_state = result["new_state"]
    update_state(chat_id, new_state)
    state_to_stat = {"qualifying": "qualifying", "searching": "searching",
                     "presenting": "presenting", "escalated": "escalations",
                     "closed": "closed"}
    if new_state in state_to_stat and new_state != state:
        update_stats(state_to_stat[new_state])
    if result["escalate"]:
        esc_text = format_escalation(chat_id, text, history, result["emotion"])
        await send_to_owner(bot, esc_text)
        await send_to_team(bot,
            format_team_notification(chat_id, "state_change", new_state, "Эскалация"))
        save_lesson(history + [{"role": "assistant", "content": reply_text}],
                    result["emotion"], escalated=True)
    if action_data:
        n8n_result = call_n8n(action_data["action"], action_data["params"],
                              chat_id, chat_id, history, result["emotion"])
        update_stats("actions_total")
        update_stats(action_data["action"])
        if n8n_result.get("reply"):
            await send_to_client(bot, chat_id, n8n_result["reply"])
        if n8n_result.get("success"):
            await send_to_team(bot,
                format_team_notification(chat_id, "action", new_state,
                    f"Действие: {action_data['action']}"))
    if client["message_count"] > 0 and client["message_count"] % 10 == 0:
        new_summary = (f"Клиент на этапе {new_state}. "
                       f"Последняя эмоция: {result['emotion']}. "
                       f"Ключевые темы: {text[:100]}")
        update_summary(chat_id, new_summary)
