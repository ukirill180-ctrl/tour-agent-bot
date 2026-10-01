"""RAG: загрузка базы знаний и поиск релевантных фрагментов"""
import os
import re
from config import KNOWLEDGE_DIR, CASES_DIR


def load_knowledge() -> dict:
    result = {}
    for d in [KNOWLEDGE_DIR, CASES_DIR]:
        if not os.path.isdir(d):
            continue
        for fname in os.listdir(d):
            if fname.endswith(".md"):
                path = os.path.join(d, fname)
                with open(path, "r", encoding="utf-8") as f:
                    result[fname] = f.read()
    return result


def search(query: str, knowledge: dict, top_k: int = 3) -> str:
    if not knowledge:
        return ""
    query_lower = query.lower()
    query_words = set(re.findall(r"\w+", query_lower))
    scored = []
    for fname, content in knowledge.items():
        content_lower = content.lower()
        score = 0
        for word in query_words:
            score += content_lower.count(word)
        if score > 0:
            scored.append((score, fname, content))
    scored.sort(key=lambda x: x[0], reverse=True)
    if not scored:
        for fname in ["profile.md", "services.md"]:
            if fname in knowledge:
                return f"--- {fname} ---\n{knowledge[fname]}"
        return ""
    parts = []
    for _, fname, content in scored[:top_k]:
        if len(content) > 2000:
            content = content[:2000] + "..."
        parts.append(f"--- {fname} ---\n{content}")
    return "\n\n".join(parts)
