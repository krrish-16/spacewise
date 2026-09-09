"""SpaceWise FastAPI gateway."""

from __future__ import annotations

import asyncio
import copy
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from debris_engine import advance_debris, check_debris, reset_debris, trigger_approach
from failure_engine import build_failure_state, get_failure_path
from copilot_engine import generate_copilot_forecast


BASE_TELEMETRY = {
    "solar_power": {"voltage": 28.1, "status": "NOMINAL"},
    "battery": {"level": 31.0, "status": "CRITICAL"},
    "thermal": {"temp": 19.5, "status": "WATCH"},
    "comms": {"signal": -64.6, "status": "WATCH"},
    "propulsion": {"thrust": 13.8, "status": "CRITICAL"},
    "payload": {"power": 117.0, "status": "NOMINAL"},
}

SCENARIOS = {
    "battery_cascade": "battery",
    "solar_failure": "battery",
}

active_scenario = "battery_cascade"
websocket_clients: set[WebSocket] = set()


def get_full_state() -> dict:
    collision = check_debris()
    graph_nodes = build_failure_state(SCENARIOS[active_scenario])
    copilot = generate_copilot_forecast(collision, graph_nodes)

    telemetry = copy.deepcopy(BASE_TELEMETRY)

    # Small deterministic telemetry effects tied to the demo scenario.
    if collision["imminent"]:
        telemetry["propulsion"]["status"] = "CRITICAL"

    return {
        "active_scenario": active_scenario,
        "telemetry": telemetry,
        "graph_nodes": graph_nodes,
        "collision_data": {
            "imminent": collision["imminent"],
            "distance_km": collision["distance_km"],
            "time_to_impact_sec": collision["time_to_impact_sec"],
            "debris_id": collision["debris_id"],
        },
        "copilot_recommendation": copilot,
        "failure_path": get_failure_path(SCENARIOS[active_scenario]),
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(simulation_loop())
    yield
    task.cancel()


app = FastAPI(title="SpaceWise Mission Control API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"service": "SpaceWise", "status": "online"}


@app.get("/api/state")
def api_state():
    return get_full_state()


@app.post("/api/debris/advance")
async def api_advance():
    advance_debris(20)
    state = get_full_state()
    await broadcast(state)
    return state


@app.post("/api/debris/trigger")
async def api_trigger():
    trigger_approach()
    state = get_full_state()
    await broadcast(state)
    return state


@app.post("/api/reset")
async def api_reset():
    reset_debris()
    state = get_full_state()
    await broadcast(state)
    return state


@app.post("/api/scenario/{scenario_name}")
async def api_scenario(scenario_name: str):
    global active_scenario

    if scenario_name not in SCENARIOS:
        return {"error": f"Unknown scenario: {scenario_name}"}

    active_scenario = scenario_name
    state = get_full_state()
    await broadcast(state)
    return state


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.add(websocket)

    try:
        await websocket.send_json(get_full_state())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_clients.discard(websocket)
    except Exception:
        websocket_clients.discard(websocket)


async def broadcast(state: dict):
    dead = []
    for client in websocket_clients:
        try:
            await client.send_json(state)
        except Exception:
            dead.append(client)

    for client in dead:
        websocket_clients.discard(client)


async def simulation_loop():
    """Slow background loop keeps the dashboard feeling live."""
    while True:
        await asyncio.sleep(5)
        advance_debris(20)
        await broadcast(get_full_state())
