"""Точка входа"""
import asyncio
import logging
import datetime as dt

from bot import bot, dp
from subscription import daily_job
from database import init_db

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def scheduler():
    while True:
        now = dt.datetime.now()
        next_run = now.replace(hour=9, minute=0, second=0, microsecond=0)
        if next_run <= now:
            next_run = next_run + dt.timedelta(days=1)
        wait_seconds = (next_run - now).total_seconds()
        logger.info("Scheduler: next at %s (%.0fs)", next_run, wait_seconds)
        await asyncio.sleep(wait_seconds)
        try:
            await daily_job()
        except Exception:
            logger.exception("Scheduler error")


async def run_all():
    init_db()
    logger.info("Database initialized")
    asyncio.create_task(scheduler())
    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(run_all())
