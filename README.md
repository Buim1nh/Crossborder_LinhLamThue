# Crossborder LinhLamThue - WLF-01

AI-powered financial assistant for expense management and transaction safety.

## Overview

This project is built for the **Cross-Border AI Innovation Hackathon 2026**, specifically the **WLF-01: Quản lý chi tiêu & an toàn giao dịch** challenge by Wealify.

The system acts as a conversational AI assistant that:
- Reads and categorizes account statements
- Matches transactions with email receipts
- Cross-references 3 sources (account, wallet, card)
- Detects anomalies and forgotten subscriptions
- Generates spending reports
- Sends proactive alerts (with user confirmation)

## Tech Stack

- **Frontend**: Next.js 14 (App Router)
- **Backend**: FastAPI (Python)
- **Database**: SQLite
- **LLM**: Pluggable (Claude/GPT-4o/Gemini - TBD)

## Project Structure

```
Crossborder_LinhLamThue/
├── backend/                 # FastAPI application
│   ├── src/
│   │   ├── api/            # API routes
│   │   ├── core/           # Config, security
│   │   ├── models/         # Pydantic models
│   │   ├── parsers/        # Statement, email parsers
│   │   └── services/       # Business logic
│   ├── tests/
│   └── requirements.txt
├── frontend/               # Next.js application
│   ├── src/
│   │   ├── app/           # App router pages
│   │   ├── components/     # React components
│   │   ├── lib/           # Utilities
│   │   └── types/         # TypeScript types
│   └── package.json
└── docs/                   # Documentation
```

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Requirements

- Python 3.10+
- Node.js 18+
- npm or yarn

## Security Notes

- Never hardcode API keys - use environment variables
- Card numbers masked (show only last 4 digits)
- CVV never stored or displayed
- All money operations are READ-ONLY
- Email only sent to user's own email with confirmation

## Team

4 members from VinGroup/VinUni AI Thực Chiến program.
