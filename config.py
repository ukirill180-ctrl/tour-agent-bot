"""Конфигурация проекта. Читается из .env"""
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_CHAT_ID = int(os.getenv("OWNER_CHAT_ID", "0"))
TEAM_CHAT_ID = int(os.getenv("TEAM_CHAT_ID", "0"))
REPORT_CHAT_ID = int(os.getenv("REPORT_CHAT_ID", "0"))

YANDEX_API_KEY = os.getenv("YANDEX_API_KEY", "")
YANDEX_FOLDER_ID = os.getenv("YANDEX_FOLDER_ID", "")
YANDEX_MODEL = os.getenv("YANDEX_MODEL", "yandexgpt")
YANDEX_API_URL = "https://llm.api.cloud.yandex.net/v1/chat/completions"

N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")

DB_PATH = os.getenv("DB_PATH", "agent.db")
FREE_MESSAGE_LIMIT = int(os.getenv("FREE_MESSAGE_LIMIT", "5"))
HISTORY_LIMIT = 10
QUALIFYING_THRESHOLD = 8

KNOWLEDGE_DIR = os.getenv("KNOWLEDGE_DIR", "knowledge")
CASES_DIR = os.getenv("CASES_DIR", "cases")
