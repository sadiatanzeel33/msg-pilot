# Msg-Pilot — Bulk WhatsApp Automation Platform

A complete, production-ready bulk WhatsApp messaging system with campaign management, Excel import, contact management, and analytics dashboard.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌────────────┐
│  Next.js 14  │────▶│  FastAPI      │────▶│ PostgreSQL │
│  (Frontend)  │     │  (Backend)    │     └────────────┘
│  Port 3000   │     │  Port 8000    │──────┐
└─────────────┘     └──────────────┘      │
                           │           ┌──────┐
                    ┌──────▼──────┐    │Redis │
                    │Celery Worker│◀───┤      │
                    │(Playwright) │    └──────┘
                    └─────────────┘
```

## Features

- **User Auth** — JWT signup/login, role-based (Admin/User)
- **Excel Upload** — Import .xlsx with validation, preview, duplicate detection
- **Campaign Engine** — Personalized messages with `{Name}`, queue-based sending
- **WhatsApp Web** — Playwright automation, QR login, session persistence
- **Media Support** — Send images, PDFs, documents
- **Campaign Control** — Create, schedule, start, pause, resume, stop
- **Dashboard** — Stats, charts, delivery logs
- **Anti-Block** — Random delays, daily limits, invalid number handling
- **Contact Management** — Tags, groups, search, import/export
- **Activity Logs** — Full audit trail, exportable reports

## Quick Start (Docker)

```bash
# 1. Clone and enter project
cd Msg-Pilot

# 2. Copy environment file
cp backend/.env.example backend/.env
# Edit backend/.env with a real SECRET_KEY

# 3. Start everything
cd docker
docker compose up --build -d

# 4. Install Playwright browsers (first time only)
docker compose exec backend playwright install chromium

# 5. Open the app
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
```

## Manual Setup (Development)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7+

### Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Setup environment
cp .env.example .env
# Edit .env — set DATABASE_URL to your local PostgreSQL:
# DATABASE_URL=postgresql+asyncpg://msgpilot:msgpilot_secret@localhost:5432/msgpilot

# Create database
createdb msgpilot  # or via psql: CREATE DATABASE msgpilot;

# Run server (auto-creates tables on startup)
uvicorn app.main:app --reload --port 8000

# In a separate terminal — run Celery worker
celery -A app.services.celery_app worker -l info -c 1

# In another terminal — run Celery Beat (for scheduled campaigns)
celery -A app.services.celery_app beat -l info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Open http://localhost:3000
```

### Generate Sample Excel

```bash
cd sample_data
pip install openpyxl
python create_sample.py
# Creates sample_contacts.xlsx
```

## Usage Guide

### 1. Create Account
- Open http://localhost:3000
- Sign up (first user becomes Admin)

### 2. Connect WhatsApp
- Go to **WhatsApp Session** in sidebar
- Click **Get QR Code**
- Scan with your phone (WhatsApp → Linked Devices → Link a Device)
- Session is saved — no need to re-scan

### 3. Import Contacts
- Go to **Contacts → Upload Excel**
- Upload .xlsx with columns: `Name`, `PhoneNumber`, `Message` (optional)
- Preview validates all numbers
- Click **Import Valid Contacts**

### 4. Create Campaign
- Go to **Campaigns → New Campaign**
- Set name, message template (use `{Name}` for personalization)
- Adjust delay (8–25 sec recommended) and daily limit
- Select contacts
- Optionally attach media and schedule
- Click **Create Campaign**

### 5. Start Sending
- Click the ▶️ play button on a campaign
- Monitor progress in real-time
- Pause/stop anytime
- Download delivery report (Excel)

## Excel File Format

| Name | PhoneNumber | Message |
|------|-------------|---------|
| Alice Johnson | +14155551234 | Hello {Name}, check out our sale! |
| Bob Smith | +447911123456 | |

- **Name** — Required
- **PhoneNumber** — Required, international format with country code
- **Message** — Optional, overrides campaign template for this contact

## API Documentation

When the backend is running, visit: http://localhost:8000/docs

Key endpoints:
- `POST /api/auth/signup` — Create account
- `POST /api/auth/login` — Get JWT token
- `POST /api/contacts/upload/preview` — Preview Excel upload
- `POST /api/contacts/upload/confirm` — Import contacts
- `POST /api/campaigns/` — Create campaign
- `POST /api/campaigns/{id}/start` — Start sending
- `GET /api/dashboard/stats` — Analytics
- `POST /api/whatsapp/session/qr` — Get QR code

## Project Structure

```
Msg-Pilot/
├── backend/
│   ├── app/
│   │   ├── api/routes/      # auth, contacts, campaigns, dashboard, logs, whatsapp
│   │   ├── core/            # config, database, security
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # WhatsApp engine, Celery tasks
│   │   ├── utils/           # Phone validation, Excel parsing
│   │   └── main.py          # FastAPI app
│   ├── migrations/          # Alembic
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── app/             # Next.js pages (auth, dashboard, campaigns, contacts, settings)
│       ├── components/      # UI components (Button, Card, Badge, Sidebar, Shell)
│       ├── hooks/           # useAuth
│       └── lib/             # API client, utils
├── docker/                  # Docker Compose + Dockerfiles
├── sample_data/             # Sample Excel generator
├── database_schema.sql      # Reference SQL schema
└── README.md
```

## Anti-Block Best Practices

| Setting | Recommended | Aggressive (risky) |
|---------|-------------|-------------------|
| Min delay | 8 sec | 3 sec |
| Max delay | 25 sec | 10 sec |
| Daily limit | 300–500 | 1000+ |
| Personalization | Always use `{Name}` | Identical messages |

## License

Private — for authorized use only.
