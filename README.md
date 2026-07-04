# ⭐ Отзывы на продукты

Веб-приложение для отзывов на товары. Пользователи регистрируются, добавляют
товары (название, фото, описание, категории) и оставляют отзывы с оценкой.
При создании отзыва можно выбрать существующий товар или добавить новый прямо
на месте.

## Стек

- **Backend:** Python 3.12 + FastAPI + SQLAlchemy 2.0, JWT-авторизация
- **Frontend:** Vue 3 + Vite + Pinia + Vue Router, сборка отдаётся через nginx
- **База данных:** PostgreSQL 16
- **Инфраструктура:** Docker + docker-compose

## Быстрый старт

```bash
cp .env.example .env        # при необходимости поменяйте SECRET_KEY / пароли
docker compose up --build
```

После сборки:

- Фронтенд: <http://localhost:8080>
- API (Swagger): <http://localhost:8000/docs>

Nginx во фронтенд-контейнере проксирует `/api` и `/uploads` на backend, поэтому
из браузера всё работает через один origin (порт 8080).

## Функционал

- **Регистрация и вход** — JWT-токен хранится в `localStorage`.
- **Товары** — название, необязательное описание, фото (до 5 МБ), категории
  (many-to-many). Список с поиском по названию и фильтром по категории,
  средний рейтинг и число отзывов.
- **Категории** — общий справочник; можно создавать новые прямо в форме товара.
- **Отзывы** — оценка 1–5 звёзд + необязательный текст. На форме отзыва можно
  выбрать существующий товар **или** добавить новый (с фото). Один пользователь —
  один отзыв на товар.

## Структура

```
backend/            FastAPI-приложение
  app/
    main.py         точка входа, CORS, статика /uploads, создание таблиц
    config.py       настройки (env)
    database.py     подключение к БД, сессии
    models.py       модели: User, Category, Product, Review
    schemas.py      Pydantic-схемы
    security.py     хеширование паролей, JWT
    deps.py         зависимость get_current_user
    routers/        auth, categories, products, reviews
frontend/           Vue 3 + Vite (SPA), nginx для раздачи
docker-compose.yml  db + backend + frontend
```

## Локальная разработка (без Docker)

Backend:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/reviews
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173, проксирует API на :8000
```

## Заметки

- Таблицы создаются автоматически при старте (`Base.metadata.create_all`).
  Для продакшена стоит подключить Alembic-миграции.
- Загруженные изображения лежат в volume `uploads_data` и раздаются backend'ом
  по пути `/uploads/...`.
```
