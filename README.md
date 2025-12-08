# Math Helper

Math Helper is a teaching companion that coaches students from single-digit arithmetic through confident long division. It delivers structured practice, adaptive question generation, and transparent progress insights so families can track growth over time.

## Product pillars

- **Guided curriculum** – Learners advance through themed levels (facts, multi-digit operations, long division) with increasing digit counts and mixed formats.
- **Flash-card drills** – Rapid-fire cards build recall for smaller problems while logging speed and accuracy.
- **Step-aware challenges** – Larger problems capture written steps, verify intermediate work, and provide hints when needed.
- **Progress intelligence** – A results hub visualizes streaks, pace, and accuracy by operation, showing momentum at a glance.
- **Question history** – Every prompt is reviewable, including frequency, correctness, and time-to-answer metrics.

## Architecture snapshot

```
math-helper/
├── backend/           # Flask service (hello-world API, ready for data layer)
│   ├── app/__init__.py
│   └── app/routes.py
├── frontend/          # React + TypeScript client (Vite)
│   ├── src/components/MathDashboard.tsx  # Animated learner dashboard
│   ├── src/App.tsx    # Renders the dashboard
│   └── vite.config.ts # Dev server proxy → Flask backend
└── README.md
```

- **Frontend** (React + TypeScript + Tailwind) now ships the animated Math Dashboard experience with sample streak cards, achievements, and the backend-powered learner invite flow. A new `/practice` route renders the mocked practice session surface that consumes the PIN-verified submission endpoint.
- **Backend** (Flask) powers real-time question generation, evaluation, and analytics APIs.
- **Storage** uses SQLite for lightweight persistence, perfect for edge deployments and sync workflows.

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Set port via environment variable or use --port flag
export FLASK_RUN_PORT=5004  # Optional: Flask uses this by default
flask --app app run --debug --port 5004
```

API is served at `http://localhost:5004` (or configured port) with a `/api/hello` handshake and `/healthz` probe for readiness checks.

**Environment Variables:**
- `FLASK_RUN_PORT` - Port for Flask server (default: can be set via --port flag)
- `TESTING` - Set to `true` to enable testing mode (default: `false`)
- `LOG_LEVEL` - Logging level: DEBUG, INFO, WARN, ERROR (default: `INFO`)
- `DEBUG_ACHIEVEMENTS` - Set to `true` for detailed achievement logging (default: `false`)

See `backend/.env.example` for all available configuration options.

### Frontend

```bash
cd frontend
npm install

# Set port via environment variable or use --port flag
export VITE_PORT=5173  # Optional: Vite defaults to 5173
npm run dev
```

The Vite dev server proxies `/api/*` calls to Flask, confirming the end-to-end wiring while UI features are built out.

**Environment Variables:**
- `VITE_BACKEND_URL` - Backend API URL (default: `http://localhost:5004`)
- `VITE_PORT` - Port for Vite dev server (default: `5173`)
- `VITE_DEV_MODE` - Set to `true` to enable dev mode features (default: `false`)
- `VITE_LOG_LEVEL` - Logging level: DEBUG, INFO, WARN, ERROR, NONE (default: DEBUG in dev, INFO in production)
- `VITE_LOGGING_ENABLED` - Set to `false` to disable logging (default: `true`)

See `frontend/.env.example` for all available configuration options.

### E2E Testing

The frontend includes Playwright E2E tests. See `frontend/README.md` for detailed instructions. Quick start:

**Both backend and frontend must be running:**

```bash
# Terminal 1: Start backend
cd backend
source .venv/bin/activate
export FLASK_RUN_PORT=5004  # Optional
flask --app app run --debug --port 5004 --host 0.0.0.0

# Terminal 2: Start frontend
cd frontend
export VITE_PORT=5003  # Optional
export FRONTEND_PORT=5003  # For Playwright tests
npm run dev -- --port 5003

# Terminal 3: Run tests
cd frontend
export BACKEND_PORT=5004  # Optional: defaults to 5004
export FRONTEND_PORT=5003  # Optional: defaults to 5003
npm run test:e2e
```

**Environment Variables for E2E Tests:**
- `BACKEND_PORT` - Backend server port (default: `5004`)
- `FRONTEND_PORT` - Frontend server port (default: `5003`)
- `FRONTEND_URL` - Full frontend URL (default: `http://localhost:${FRONTEND_PORT}`)
- `VITE_BACKEND_URL` - Backend API URL for frontend proxy (default: `http://localhost:5004`)

## Security posture

Math Helper is designed for trusted, local-network deployments while the curriculum engine evolves. Authentication is limited to a shared display name + 4-digit PIN that are stored in plain text and embedded in app URLs for convenience. Do **not** deploy this configuration to public networks without hardening the auth layer and removing the plain-text PIN storage/transport.

## API sketch

- `POST /api/users` – Create a learner profile with `{ "avatar": "🐯", "name": "Taylor", "pin": "1234" }`. The response includes `share_url_params` for future invite links, even though the current frontend keeps everything local-only.
- `GET /api/users` – List every learner plus derived dashboard metrics (levels, accuracy, speed, streaks) and any persisted achievements awarded by the backend rules engine.
- `GET /api/users/<id>` – Fetch a single learner snapshot with the same metric payload as the list endpoint.
- `GET /api/achievements?user_id=<id>` – Fetch the persisted achievements across all learners or scoped to a single learner for the global activity rail shown on the dashboard.
- `POST /api/practice/submissions` – Accepts `{ userId?, userName?, pin, attempts[] }`, verifies the PIN from share-link parameters, and returns a mocked practice session summary so the new practice UI can gate submissions before the real engine lands.

Schema groundwork (SQLite via SQLAlchemy) also defines `questions` and `responses` tables, ready for future endpoints that log generated prompts and learner answers with timestamps.
