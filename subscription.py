"""Проверка подписок и ежедневные отчёты"""
import logging
from datetime import datetime
from database import get_all_clients, get_subscription, update_subscription, get_stats
from message_router import send_to_reports, format_report
from bot import bot

logger = logging.getLogger(__name__)


async def check_subscriptions():
    clients = get_all_clients()
    now = datetime.now()
    for client in clients:
        chat_id = client["chat_id"]
        sub = get_subscription(chat_id)
        if not sub or sub["status"] != "active" or not sub["paid_until"]:
            continue
        try:
            paid_until = datetime.fromisoformat(sub["paid_until"])
        except (ValueError, TypeError):
            continue
        if now > paid_until:
            update_subscription(chat_id, "expired", "")
            logger.info("Подписка истекла для клиента %s", chat_id)


async def send_daily_report():
    stats = get_stats()
    await send_to_reports(bot, format_report(stats))


async def daily_job():
    await check_subscriptions()
    await send_daily_report()
