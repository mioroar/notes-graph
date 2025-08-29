# Notes Graph

Лёгкий бэкенд на FastAPI для заметок в виде графа (узлы—заметки, связи—лейблы + важность).

## Запуск БД и pgAdmin (Docker)
```bash
docker compose up -d
# pgAdmin: http://localhost:5050 (admin@local.com / admin)
# Postgres: localhost:5433, db=notes_graph, user=notes_user, pass=notes_pass
