# Chill Guy Bot

Chill Guy Bot là Discord bot riêng cho guild **Chill Station**. Dự án gồm bot Discord chính, cơ sở dữ liệu MySQL và Discord Activity **Mergeverse** để phục vụ điều hành server, quản lý vai trò, tự động hóa, theo dõi hoạt động và các tính năng game cộng đồng.

Bot được thiết kế cho một guild duy nhất, không theo kiến trúc multi-guild.

## Tính năng chính

- Discord slash commands và prefix commands với prefix `cg ` hoặc `Cg `.
- Điều hành server: ban, kick, mute, unmute, xóa tin nhắn, auto moderation.
- Quản lý thành viên, staff/mod/admin permission, sinh nhật, thông báo và luồng welcome/leave.
- Theo dõi hoạt động: bảng xếp hạng chat, bảng xếp hạng voice, thưởng top chat hằng tháng.
- Auto responder và anonymous match.
- Economy và farm game: farm, crop, animal, fishing, train event, market, giftcode, daily task, Chill Coin.
- Minigame: slot, blackjack, lotto, Wordle, fortune.
- Giveaway, music event, role shop, booster custom role, ticket và partner/server invite flow.
- Mergeverse Discord Activity: frontend Vite/Matter.js, API FastAPI, lưu leaderboard vào MySQL để bot đọc lại.

## Tech stack

- Python 3.11
- discord.py, APScheduler, SQLAlchemy, mysql-connector-python
- edge-tts, davey, Pillow, requests, googletrans, google-genai
- MySQL 8.0
- FastAPI, pydantic, uvicorn
- Vite, Matter.js, Discord Embedded App SDK
- Docker Compose, Nginx, Cloudflare Tunnel

## Cấu trúc dự án

```text
.
|-- bot/                     # Runtime của Discord bot
|   |-- main.py              # Entry point, load extensions và start bot
|   |-- commands/            # Slash/prefix commands
|   |-- events/              # Discord event listeners
|   |-- tasks/               # APScheduler jobs
|   |-- services/            # Business logic
|   |-- repository/          # Database CRUD/query layer
|   |-- models/              # SQLAlchemy ORM models
|   |-- config/              # Constants, env config, DB config
|   |-- validation/          # Reusable predicate validations
|   |-- views/               # Discord UI components
|   |-- cache/               # Runtime caches
|   `-- assets/              # Fonts, images, render assets
|-- activity/
|   |-- api/                 # FastAPI service cho Discord Activity auth/progress
|   |-- game/                # Vite frontend Mergeverse
|   `-- nginx/               # Nginx proxy config
|-- Dbschema/                # MySQL schema và seed data
|-- docker-compose.yml       # Bot, MySQL, Activity API/web, Cloudflare tunnel
|-- dockerfile               # Dockerfile cho Discord bot
|-- requirements.txt         # Python dependencies của bot
`-- .env.example             # Mẫu biến môi trường
```

## Yêu cầu

- Docker và Docker Compose.
- Discord bot token.
- Discord application OAuth credentials nếu chạy Discord Activity.
- MySQL schema/seed từ `Dbschema/`.

## Cấu hình môi trường

Tạo file `.env` từ `.env.example`:

```bash
cp .env.example .env
```

Các biến chính:

```dotenv
DISCORD_TOKEN=
DISCORD_CLIENT_ID=
DISCORD_CLIENT_SECRET=

DB_HOST=mysql
DB_PORT=3306
DB_NAME=chill_station
DB_USER=root
DB_PASSWORD=root

GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.1-flash-lite
```

Lưu ý:

- Không commit `.env` hoặc credential thật.
- Khi chạy bằng Docker Compose, `DB_HOST` nên là `mysql`.
- `docker-compose.yml` expose MySQL ra host qua port `3310:3306`; bên trong container vẫn dùng port `3306`.
- `.env.example` hiện có `DB_PORT=3307`; nếu chạy Compose mặc định, đổi thành `3306` trong `.env`.

## Chạy bằng Docker Compose

Build và start toàn bộ stack:

```bash
docker compose up --build
```

Stack gồm:

- `bot`: Discord bot, chạy `python -m bot.main`.
- `mysql`: MySQL 8.0, database `chill_station`.
- `game-api`: FastAPI service ở port nội bộ `3001`.
- `game-web`: Nginx serve frontend Activity, expose `http://localhost:8080`.
- `cloudflared`: tunnel tới `game-web`.

Dừng stack:

```bash
docker compose down
```

Dừng kèm xóa volume database:

```bash
docker compose down -v
```

## Khởi tạo database

Sau khi MySQL container đã chạy, import schema và seed data:

```bash
docker exec -i chill-guy-db mysql -uroot -proot chill_station < Dbschema/chillguy.sql
docker exec -i chill-guy-db mysql -uroot -proot chill_station < Dbschema/farmGameData.sql
docker exec -i chill-guy-db mysql -uroot -proot chill_station < Dbschema/guessWord.sql
docker exec -i chill-guy-db mysql -uroot -proot chill_station < Dbschema/keyWord.sql
```

Nếu chạy MySQL local qua port host:

```bash
mysql -h 127.0.0.1 -P 3310 -uroot -proot chill_station < Dbschema/chillguy.sql
```

## Chạy bot local không Docker

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
python -m bot.main
```

Khi chạy local, đặt `DB_HOST=127.0.0.1` và `DB_PORT=3310` nếu MySQL đang chạy từ Docker Compose.

## Discord Activity Mergeverse

Activity có 2 phần:

- `activity/game`: Vite frontend, Matter.js merge game, Discord Embedded App SDK auth.
- `activity/api`: FastAPI API, exchange Discord OAuth code, validate `/users/@me`, save progress vào `merge_game_play_history`.

Frontend gọi:

- `POST /api/discord/token`
- `POST /api/game-progress`
- `POST /api/game-over`
- `GET /health`

Game auto-save progress mỗi 20 giây và force-save khi game over. Lần save đầu tạo row `merge_game_play_history`; các lần sau update row đó. Khi update, API giữ `sun_time` nhanh nhất nếu có.

Chạy frontend riêng:

```bash
cd activity/game
npm install
npm run dev
```

Build frontend:

```bash
cd activity/game
npm run build
```

Chạy API riêng:

```bash
cd activity/api
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 3001
```

## Kiến trúc code

Dự án tách layer theo trách nhiệm:

- `commands/`: nhận tương tác Discord, validate permission, gọi service.
- `events/`: lắng nghe event Discord, kiểm tra điều kiện, gọi service.
- `services/`: business logic và điều phối repository/view/task.
- `repository/`: CRUD và query database.
- `models/`: SQLAlchemy models, cần khớp schema MySQL.
- `tasks/`: scheduled jobs.
- `validation/`: predicate validation dùng lại.
- `views/`: Discord UI buttons, selects, pagination, persistent views.

Entry point `bot/main.py` load tất cả commands, events và tasks; sync slash commands vào guild Chill Station; preload caches; đăng ký persistent views cho music event, giveaway và lotto.

## Quy ước phát triển

- Commands phải mỏng; business logic đặt trong `services/`.
- Không viết query database trong command/event.
- Mỗi command mới nằm trong file command riêng.
- Không gom 2 command class vào cùng 1 file.
- Một repository cho mỗi model.
- Models phải khớp database schema.
- Không hardcode token, secret, database credential.
- Dùng camelCase cho biến và function.
- Thay đổi nhỏ gọn, ưu tiên pattern hiện có của repo.

## Kiểm tra nhanh

Kiểm tra syntax Python:

```bash
python -m compileall bot activity/api
```

Kiểm tra build frontend:

```bash
cd activity/game
npm install
npm run build
```

Kiểm tra service health khi chạy Compose:

```bash
curl http://localhost:8080/health
```

## Ghi chú vận hành

- Bot cần Discord privileged intents: members, presences, message content, guilds và voice states.
- Slash commands được sync vào guild ID cấu hình trong `bot/config/config.py`.
- `cloudflared` trong Compose tạo tunnel tạm thời tới Activity web; cấu hình production Discord Activity cần URL public hợp lệ.
- Database là nguồn chung: Discord Activity ghi merge game data, Discord bot đọc leaderboard từ MySQL.
