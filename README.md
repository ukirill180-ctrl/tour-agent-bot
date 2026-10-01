# Tour Agent AI

ИИ-ассистент турагента на Python + YandexGPT + n8n.

## Возможности
- RAG (база знаний из .md)
- Эмпатия (6 эмоций)
- Самообучение (сохранение уроков в RAG)
- 4 потока сообщений (клиент, владелец, команда, отчёты)
- Эскалация ([ESCALATE])
- n8n webhook ([ACTION: ...])
- Машина состояний (6 состояний)
- Подписки + cron
- Ежедневные отчёты

## Запуск
```bash
pip install -r requirements.txt
cp .env.example .env
python main.py
```

## Docker
```bash
docker-compose up -d
```
