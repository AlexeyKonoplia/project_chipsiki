# Деплой на сервер

Стек уже упакован в `docker compose` (db + backend + frontend), поэтому проще
всего собрать образы прямо на сервере. Ниже — рекомендуемый способ и альтернатива
без пересборки.

## Способ 0 (авто-CI/CD): образы из ghcr.io

Самый удобный вариант: GitHub Actions (`.github/workflows/docker-publish.yml`)
при каждом пуше в `main` собирает образы backend и frontend и публикует их в
GitHub Container Registry. Сервер их только **подтягивает** — ничего не собирает.

### Разовая настройка

1. Запушить проект в репозиторий и дождаться, пока экшен `Build and publish
   Docker images` отработает (вкладка **Actions**).
2. Сделать пакеты публичными (иначе сервер не скачает без логина):
   GitHub → профиль → **Packages** → `project_chipsiki-backend` и
   `project_chipsiki-frontend` → *Package settings* → **Change visibility → Public**.
   Либо оставить приватными и на сервере один раз выполнить:
   ```bash
   echo <PERSONAL_ACCESS_TOKEN> | docker login ghcr.io -u AlexeyKonoplia --password-stdin
   ```
   (токен с правом `read:packages`).

### На сервере

```bash
git clone https://github.com/AlexeyKonoplia/project_chipsiki.git chipsiki
cd chipsiki
cp .env.example .env      # заполнить SECRET_KEY, пароль БД, FRONTEND_PORT=80
docker compose -f docker-compose.prod.yml up -d    # подтянет образы из ghcr.io
```

Обновление после нового пуша в `main`:

```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

`docker-compose.prod.yml` уже указывает на
`ghcr.io/alexeykonoplia/project_chipsiki-backend:latest` и `...-frontend:latest`
(с `pull_policy: always`), db остаётся официальным `postgres:16-alpine`.

---

## Способ 1 (рекомендуется): собрать на сервере

### 1. Установить Docker на сервере (Ubuntu/Debian)

```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER   # чтобы docker работал без sudo (перелогиниться)
```

Проверка: `docker version` и `docker compose version`.

### 2. Доставить код на сервер

Вариант с git:

```bash
git clone <URL-репозитория> chipsiki && cd chipsiki
```

Вариант без git — скопировать с локальной машины (из папки проекта):

```bash
rsync -av --exclude node_modules --exclude .venv --exclude '*/uploads' \
  ./ user@SERVER_IP:/home/user/chipsiki/
```

### 3. Создать `.env` с боевыми секретами

```bash
cp .env.example .env
nano .env
```

Обязательно поменять:

```dotenv
POSTGRES_PASSWORD=<сложный-пароль>
SECRET_KEY=<длинная-случайная-строка>   # openssl rand -hex 32
ADMIN_USERNAMES=koh0                     # ваши админ-логины через запятую
FRONTEND_PORT=80                         # сайт на 80 порту
```

### 4. Запустить

```bash
docker compose up -d --build
```

### 5. Открыть порт в фаерволе

```bash
sudo ufw allow 80/tcp
```

Готово — сайт доступен на `http://SERVER_IP`. Зайдите и зарегистрируйтесь под
логином из `ADMIN_USERNAMES` — аккаунт сразу станет админом.

---

## Способ 2: собрать локально, перенести образы (без сборки на сервере)

Если на сервере мало ресурсов для сборки. С локальной машины:

```bash
docker compose build
docker save project_chipsiki-backend project_chipsiki-frontend postgres:16-alpine \
  | gzip > images.tar.gz
scp images.tar.gz docker-compose.yml .env user@SERVER_IP:/home/user/chipsiki/
```

На сервере:

```bash
cd chipsiki
gunzip -c images.tar.gz | docker load
docker compose up -d          # без --build, образы уже загружены
```

(Альтернатива — запушить образы в реестр Docker Hub/GHCR и сделать `docker pull`.)

---

## Эксплуатация

```bash
docker compose ps                 # статус
docker compose logs -f backend    # логи
docker compose pull && docker compose up -d --build   # обновить после git pull
docker compose down               # остановить (данные в volume сохраняются)
```

### Обновление кода

```bash
git pull
docker compose up -d --build
```

### Бэкап данных

Всё состояние — в двух volume: `db_data` (БД) и `uploads_data` (фото).

```bash
# дамп БД
docker compose exec -T db pg_dump -U postgres reviews > backup.sql
# бэкап загруженных фото
docker run --rm -v project_chipsiki_uploads_data:/data -v $(pwd):/out \
  alpine tar czf /out/uploads.tar.gz -C /data .
```

---

## HTTPS (домен + сертификат)

Для боевого сайта нужен HTTPS. Самое простое — поставить перед фронтендом
Caddy (автоматический Let's Encrypt). Тогда `FRONTEND_PORT` верните на внутренний
(например 8080), а наружу смотрит Caddy:

`/etc/caddy/Caddyfile`:

```
example.com {
    reverse_proxy localhost:8080
}
```

`FRONTEND_PORT=8080` в `.env`, открыть порты 80 и 443, `docker compose up -d`,
`sudo systemctl reload caddy`. Caddy сам получит и продлит сертификат.
