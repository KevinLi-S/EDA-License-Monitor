# EDA License Hub (MVP)

Web dashboard for monitoring EDA license servers (Synopsys, Cadence, Mentor, Ansys).

## MVP scope
- Dashboard: vendor/server health + top busy features
- Servers page: status + last collection time + Start/Stop/Restart actions + Add/Edit/Delete server
- Command preview + Dry Run mode for safer operations
- Operation logs panel for server commands
- Features page: total/used/free snapshots
- Alerts page: low-free + server-down alerts

## Stack
- Backend: FastAPI + SQLAlchemy + SQLite (switchable to Postgres)
- Frontend: React + Vite + Ant Design
- Collector: vendor adapters -> unified JSON schema

## Quick start (frontend first)

### Frontend only (mock mode, no backend required)
```bash
cd frontend
copy .env.example .env
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

### Full stack (local)

Backend:
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Set `.env` to `VITE_USE_MOCK=false` to use live API.

### Portable deployment (Docker)
```bash
docker compose up --build
```

- Frontend: `http://127.0.0.1:8080`
- Backend: `http://127.0.0.1:8000`

## Unified collector payload
```json
{
  "vendor": "synopsys",
  "server": "snps-lic-01",
  "features": [{"name":"VCS","total":100,"used":76,"free":24}],
  "collected_at": "2026-03-05T12:00:00+08:00"
}
```
