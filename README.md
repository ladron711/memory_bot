# Memory Bot
A personal Telegram bot used as a digital diary with AI-powered entry analysis by Claude Sonnet.
The bot finds patterns and insights based on your daily entries.

## Stack
**Backend:** Python, Django, Django REST Framework
**Bot:** Python, aiogram, APScheduler
**Database:** PostgreSQL
**AI:** Claude Sonnet (Anthropic)
**Infrastructure:** Docker, Docker Compose

## Project Structure
```
memory_bot/
├── backend/
│   ├── config/          # Django settings and urls
│   ├── diary/           # Main app: models, views, serializers, analysis
│   ├── Dockerfile
│   ├── manage.py
│   └── requirements.txt
├── bot/
│   ├── bot.py           # Main bot file with handlers and scheduler
│   ├── keyboards.py     # Telegram keyboards
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── .env
```

## Environment Variables
Create a `.env` file in the root directory with the following variables:
| Variable | Description |
|----------|-------------|
| `BOT_TOKEN` | Telegram bot token from @BotFather |
| `ALLOWED_ID` | Your Telegram ID — restricts access to the bot |
| `API_URL` | URL for saving diary entries (Django endpoint) |
| `API_URL_BASE` | Base URL for running AI analysis (Django endpoint) |
| `SECRET_KEY` | Django secret key |
| `POSTGRES_DB` | PostgreSQL database name |
| `POSTGRES_USER` | PostgreSQL username |
| `POSTGRES_PASSWORD` | PostgreSQL password |
| `POSTGRES_HOST` | PostgreSQL host (use `db` for Docker) |
| `POSTGRES_PORT` | PostgreSQL port (default: 5432) |
| `ANTHROPIC_API_KEY` | API key from console.anthropic.com |

## Installation and Running

### Prerequisites
- Docker and Docker Compose installed on your server
- PostgreSQL installed
- Git installed

### Steps
1. Clone the repository
```bash
git clone https://github.com/your_username/memory_bot.git
cd memory_bot
```
2. Create `.env` file in the root directory and fill in all variables from the [Environment Variables](#environment-variables) section
3. Build and start containers
```bash
docker compose up --build -d
```
4. Apply database migrations
```bash
docker exec -it memory_backend python manage.py migrate
```
5. The bot is now running and ready to use

## How It Works

### Diary Entries
- User starts the bot with `/start`
- To add an entry press **Add** button or use `/add` command
- Each entry is collected step by step:
  1. **Category** — work, family, study, sport, rest, other
  2. **Mood** — positive, neutral, negative
  3. **Physical condition** — free text description
  4. **Comment** — free text about the day
The bot sends reminders 3 times a day: morning, afternoon and evening.

### AI Analysis
All analysis is done by **Claude Sonnet** and works automatically:
| Type | Schedule | Description |
|------|----------|-------------|
| Daily | Every day at 21:00 | Analyzes entries of the day, finds patterns |
| Weekly | Every Monday at 21:00 | Deep analysis of the week, correlations across days |
| Monthly | 1st of every month at 21:00 | Long-term trends and patterns across the month |
Each analysis builds on previous ones — patterns found earlier are passed to the next analysis so Claude can track them over time.
