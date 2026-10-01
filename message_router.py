"""Роутер: отправка в разные чаты"""
import logging
from config import OWNER_CHAT_ID, TEAM_CHAT_ID, REPORT_CHAT_ID

logger = logging.getLogger(__name__)


async def send_to_client(bot, chat_id, text, parse_mode=None):
    try:
        await bot.send_message(chat_id, text, parse_mode=parse_mode)
    except Exception as e:
        logger.error("send_to_client error: %s", e)


async def send_to_owner(bot, text, parse_mode=None):
    if not OWNER_CHAT_ID:
        return
    try:
        await bot.send_message(OWNER_CHAT_ID, text, parse_mode=parse_mode)
    except Exception as e:
        logger.error("send_to_owner error: %s", e)


async def send_to_team(bot, text, parse_mode=None):
    if not TEAM_CHAT_ID:
        return
    try:
        await bot.send_message(TEAM_CHAT_ID, text, parse_mode=parse_mode)
    except Exception as e:
        logger.error("send_to_team error: %s", e)


async def send_to_reports(bot, text, parse_mode=None):
    if not REPORT_CHAT_ID:
        return
    try:
        await bot.send_message(REPORT_CHAT_ID, text, parse_mode=parse_mode)
    except Exception as e:
        logger.error("send_to_reports error: %s", e)


def format_escalation(client_id, client_msg, history, emotion):
    lines = ["\U0001F6A8 Эскалация", f"Клиент: {client_id}",
             f"Эмоция: {emotion}", f"Сообщение: {client_msg[:200]}", "",
             "Последние сообщения:"]
    for m in history[-5:]:
        role = "Клиент" if m["role"] == "user" else "Агент"
        lines.append(f"[{role}] {m['content'][:100]}")
    lines.append("")
    lines.append(f"Для возобновления: /resume {client_id}")
    return "\n".join(lines)


def format_team_notification(client_id, event_type, state, msg=""):
    icons = {"new": "\U0001F4DD Новая заявка",
             "state_change": "\U0001F4CA Изменение статуса",
             "action": "\U0001F501 Выполнено действие"}
    icon = icons.get(event_type, "\U0001F4E8 Уведомление")
    lines = [icon, f"Клиент: {client_id}", f"Статус: {state}"]
    if msg:
        lines.append(f"Сообщение: {msg[:150]}")
    return "\n".join(lines)


def format_report(stats):
    lines = ["\U0001F4CA Ежедневный отчёт", ""]
    lines.append(f"Новых клиентов: {stats.get('new_clients', 0)}")
    lines.append(f"Всего сообщений: {stats.get('messages_total', 0)}")
    lines.append(f"На квалификации: {stats.get('qualifying', 0)}")
    lines.append(f"На подборе: {stats.get('searching', 0)}")
    lines.append(f"На презентации: {stats.get('presenting', 0)}")
    lines.append(f"Эскалаций: {stats.get('escalations', 0)}")
    lines.append(f"Закрыто: {stats.get('closed', 0)}")
    lines.append(f"Действий всего: {stats.get('actions_total', 0)}")
    lines.append("")
    total = stats.get("messages_total", 0)
    esc = stats.get("escalations", 0)
    if total > 0:
        lines.append(f"Конверсия в эскалацию: {(esc / total) * 100:.1f}%")
    else:
        lines.append("Конверсия: нет данных")
    return "\n".join(lines)
