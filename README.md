# SPACEWISE — 2-Day Hackathon Prototype

SpaceWise is a simulated AI flight-control copilot and spacecraft digital twin.

## Features

- Interactive 2D spacecraft dependency graph using React Flow.
- NetworkX cascading-failure propagation.
- Mock debris trajectory and 3D Euclidean distance calculation.
- Collision warning when debris enters the 2 km critical zone.
- FastAPI REST + WebSocket state delivery.
- Optional Groq LLM copilot with a deterministic fallback so the demo never depends on an API call.
- Shared `contract.json` defining the integration keys.

## Project structure

```text
spacewise-prototype/
├── contract.json
├── backend/
│   ├── main.py
│   ├── debris_engine.py
│   ├── failure_engine.py
│   ├── copilot_engine.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/
    ├── components/
    ├── pages/
    ├── styles/
    └── package.json
```

## Run backend

From `backend/`:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Then:

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend:
`http://localhost:8000`

State API:
`http://localhost:8000/api/state`

WebSocket:
`ws://localhost:8000/ws`

## Run frontend

Open another terminal in `frontend/`:

```bash
npm install
npm run dev
```

Open:
`http://localhost:3000`

## Optional Groq

Copy `.env.example` to `.env` and set:

```text
GROQ_API_KEY=your_key_here
```

If no key is supplied, the deterministic copilot is used.

## Demo flow

1. Start backend.
2. Start frontend.
3. Dashboard connects to `/ws`.
4. Click **TRIGGER DEBRIS APPROACH**.
5. Debris moves toward the spacecraft.
6. Distance falls toward the 2 km critical threshold.
7. Red **DEBRIS APPROACH** banner appears.
8. Copilot changes its recommendation based on the collision state and propulsion health.
9. Click **RESET SIMULATION** to return to 10 km.

## Important hackathon note

This is a simulation prototype. The debris trajectory and time-to-impact are intentionally simplified and are NOT real orbital mechanics or flight-certified guidance. Do not present the output as operational spacecraft navigation.
