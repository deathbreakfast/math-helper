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
│   ├── src/App.tsx    # Placeholder status view hitting the API
│   └── vite.config.ts # Dev server proxy → Flask backend
└── README.md
```

- **Frontend** (React + TypeScript) renders flash-card flows, dashboards, and results views. Styling upgrades (e.g., Tailwind) can be layered on without changing the stack.
- **Backend** (Flask) powers real-time question generation, evaluation, and analytics APIs.
- **Storage** uses SQLite for lightweight persistence, perfect for edge deployments and sync workflows.

## Local setup

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug
```

API is served at `http://localhost:5000` with a `/api/hello` handshake and `/healthz` probe for readiness checks.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies `/api/*` calls to Flask, confirming the end-to-end wiring while UI features are built out.

## TODOs

1. Question engine with level definitions, flash-card pools, and long-division builders.
2. SQLite-backed progress tracking for attempts, speed, hints, and accuracy trends.
3. Results dashboard featuring charts, filters, and personalized recommendations.
4. Parent-facing insights: historical exports, focus area suggestions, and progress share-outs.

This repository keeps the implementation ready for those features while presenting the product vision in the present tense.
