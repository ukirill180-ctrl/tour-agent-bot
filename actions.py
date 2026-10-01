"""Парсинг действий из ответа ИИ и отправка webhook в n8n"""
import re
import logging
import requests
from config import N8N_WEBHOOK_URL

logger = logging.getLogger(__name__)

VALID_ACTIONS = {
    "create_lead", "book_slot", "search_tours",
    "generate_contract", "send_payment_link",
    "call_agent", "send_email",
}

ACTION_PATTERN = re.compile(r'\[ACTION:\s*(\w+)(?::\s*(.+?))?\]')


def parse_action(text):
    match = ACTION_PATTERN.search(text)
    if not match:
        return None
    action = match.group(1).strip().lower()
    if action not in VALID_ACTIONS:
        logger.warning("Unknown action: %s", action)
        return None
    params = (match.group(2) or "").strip()
    clean_text = ACTION_PATTERN.sub("", text).strip()
    return {"action": action, "params": params, "clean_text": clean_text}


def call_n8n(action, params, client_id, chat_id, history=None, emotion=""):
    if not N8N_WEBHOOK_URL:
        logger.warning("N8N_WEBHOOK_URL not configured, skipping: %s", action)
        return {"reply": "", "success": False, "error": "webhook_not_configured"}
    payload = {
        "action": action, "params": params,
        "client_id": client_id, "chat_id": chat_id,
        "history": history or [], "emotion": emotion,
    }
    try:
        resp = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=30)
        if resp.ok:
            return resp.json()
        return {"reply": "", "success": False, "error": f"HTTP {resp.status_code}"}
    except requests.exceptions.Timeout:
        return {"reply": "", "success": False, "error": "timeout"}
    except requests.exceptions.ConnectionError:
        return {"reply": "", "success": False, "error": "connection_error"}
    except Exception as e:
        logger.exception("n8n webhook error")
        return {"reply": "", "success": False, "error": str(e)}
