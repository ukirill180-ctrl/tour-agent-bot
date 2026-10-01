"""Самообучение: извлечение уроков из диалогов и сохранение в RAG"""
import os
from datetime import datetime
from config import KNOWLEDGE_DIR, CASES_DIR


def save_lesson(history, emotion, escalated):
    if not history or len(history) < 3:
        return
    user_msgs = [m for m in history if m["role"] == "user"]
    if not user_msgs:
        return
    last_user = user_msgs[-1]["content"]
    assistant_msgs = [m for m in history if m["role"] == "assistant"]
    if not assistant_msgs:
        return
    last_assistant = assistant_msgs[-1]["content"]
    if escalated:
        _save_objection_case(last_user, last_assistant, emotion)
    else:
        _save_faq_entry(last_user, last_assistant)


def _save_objection_case(user_msg, agent_reply, emotion):
    path = os.path.join(KNOWLEDGE_DIR, "objections.md")
    entry = (f"\n\n---\n"
            f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"**Эмоция:** {emotion}\n"
            f"**Возражение клиента:** {user_msg[:200]}\n"
            f"**Ответ агента:** {agent_reply[:500]}\n"
            f"**Результат:** Передано менеджеру (эскалация)\n")
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry)


def _save_faq_entry(user_msg, agent_reply):
    if "?" not in user_msg:
        return
    path = os.path.join(KNOWLEDGE_DIR, "faq.md")
    entry = (f"\n\n---\n"
             f"**Дата:** {datetime.now().strftime('%Y-%m-%d')}\n"
             f"**Вопрос:** {user_msg[:200]}\n"
             f"**Ответ:** {agent_reply[:500]}\n")
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry)


def save_playbook_entry(dialog_summary, outcome):
    path = os.path.join(KNOWLEDGE_DIR, "playbook.md")
    entry = (f"\n\n---\n"
            f"**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
            f"**Исход:** {outcome}\n"
            f"**Краткое описание:** {dialog_summary[:300]}\n")
    with open(path, "a", encoding="utf-8") as f:
        f.write(entry)


def save_case(history, client_id):
    if not os.path.isdir(CASES_DIR):
        os.makedirs(CASES_DIR)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(CASES_DIR, f"case_{timestamp}_{client_id}.md")
    lines = [f"# Кейс от {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"]
    for msg in history:
        role_label = "Клиент" if msg["role"] == "user" else "Агент"
        lines.append(f"**{role_label}:** {msg['content']}\n")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
