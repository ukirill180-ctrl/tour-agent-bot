"""Работа с SQLite: клиенты, история, подписки, статистика"""
import sqlite3
from datetime import datetime
from config import DB_PATH, FREE_MESSAGE_LIMIT

VALID_STATS_FIELDS = {
    "new_clients", "qualifying", "searching", "presenting",
    "escalations", "closed", "messages_total", "actions_total",
    "create_lead", "book_slot", "search_tours",
    "generate_contract", "send_payment_link", "call_agent", "send_email",
}


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS clients (
        chat_id INTEGER PRIMARY KEY,
        state TEXT DEFAULT 'new',
        message_count INTEGER DEFAULT 0,
        history_summary TEXT DEFAULT '',
        last_contact TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER,
        role TEXT,
        content TEXT,
        emotion TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS subscriptions (
        chat_id INTEGER PRIMARY KEY,
        status TEXT DEFAULT 'trial',
        paid_until TEXT DEFAULT '',
        created_at TEXT DEFAULT (datetime('now'))
    );
    CREATE TABLE IF NOT EXISTS stats (
        date TEXT PRIMARY KEY,
        new_clients INTEGER DEFAULT 0,
        qualifying INTEGER DEFAULT 0,
        searching INTEGER DEFAULT 0,
        presenting INTEGER DEFAULT 0,
        escalations INTEGER DEFAULT 0,
        closed INTEGER DEFAULT 0,
        messages_total INTEGER DEFAULT 0,
        actions_total INTEGER DEFAULT 0,
        create_lead INTEGER DEFAULT 0,
        book_slot INTEGER DEFAULT 0,
        search_tours INTEGER DEFAULT 0,
        generate_contract INTEGER DEFAULT 0,
        send_payment_link INTEGER DEFAULT 0,
        call_agent INTEGER DEFAULT 0,
        send_email INTEGER DEFAULT 0
    );
    """)
    conn.commit()
    conn.close()


def get_client(chat_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM clients WHERE chat_id = ?", (chat_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def create_client(chat_id):
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO clients (chat_id) VALUES (?)", (chat_id,))
    conn.execute("INSERT OR IGNORE INTO subscriptions (chat_id, status) VALUES (?, 'trial')", (chat_id,))
    conn.commit()
    client = get_client(chat_id)
    conn.close()
    return client


def update_state(chat_id, state):
    conn = get_conn()
    conn.execute("UPDATE clients SET state = ? WHERE chat_id = ?", (state, chat_id))
    conn.commit()
    conn.close()


def update_summary(chat_id, summary):
    conn = get_conn()
    conn.execute("UPDATE clients SET history_summary = ? WHERE chat_id = ?", (summary, chat_id))
    conn.commit()
    conn.close()


def increment_message_count(chat_id):
    conn = get_conn()
    conn.execute("UPDATE clients SET message_count = message_count + 1, last_contact = ? WHERE chat_id = ?",
                 (datetime.now().isoformat(), chat_id))
    conn.commit()
    conn.close()


def save_message(chat_id, role, content, emotion=""):
    conn = get_conn()
    conn.execute("INSERT INTO messages (chat_id, role, content, emotion) VALUES (?, ?, ?, ?)",
                 (chat_id, role, content, emotion))
    conn.commit()
    conn.close()


def get_history(chat_id, limit=10):
    conn = get_conn()
    rows = conn.execute(
        "SELECT role, content FROM messages WHERE chat_id = ? ORDER BY id DESC LIMIT ?",
        (chat_id, limit)
    ).fetchall()
    conn.close()
    return list(reversed([dict(r) for r in rows]))


def get_subscription(chat_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM subscriptions WHERE chat_id = ?", (chat_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def update_subscription(chat_id, status, paid_until):
    conn = get_conn()
    conn.execute("UPDATE subscriptions SET status = ?, paid_until = ? WHERE chat_id = ?",
                 (status, paid_until, chat_id))
    conn.commit()
    conn.close()


def get_stats(date_str=None):
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_conn()
    row = conn.execute("SELECT * FROM stats WHERE date = ?", (date_str,)).fetchone()
    conn.close()
    return dict(row) if row else {}


def update_stats(field, value=1):
    if field not in VALID_STATS_FIELDS:
        raise ValueError(f"Invalid stats field: {field}")
    date_str = datetime.now().strftime("%Y-%m-%d")
    conn = get_conn()
    conn.execute("INSERT OR IGNORE INTO stats (date) VALUES (?)", (date_str,))
    conn.execute(f"UPDATE stats SET {field} = {field} + ? WHERE date = ?", (value, date_str))
    conn.commit()
    conn.close()


def check_subscription(chat_id):
    client = get_client(chat_id)
    if not client:
        return True
    if client["message_count"] < FREE_MESSAGE_LIMIT:
        return True
    sub = get_subscription(chat_id)
    if not sub:
        return False
    return sub["status"] == "active"


def get_all_clients():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM clients ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_clients_by_state(state):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM clients WHERE state = ? ORDER BY last_contact DESC", (state,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def reset_client(chat_id):
    conn = get_conn()
    conn.execute("UPDATE clients SET state = 'greeting', history_summary = '' WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()
