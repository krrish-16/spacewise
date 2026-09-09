"""SpaceWise Copilot: deterministic safety logic with optional Groq explanation."""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()


def deterministic_recommendation(collision: dict, graph_nodes: list[dict]) -> dict:
    """Reliable fallback used even when no LLM API key exists."""
    propulsion = next(
        (n for n in graph_nodes if n["id"] == "propulsion"), None
    )

    if collision["imminent"] and propulsion and propulsion["status"] == "CRITICAL":
        return {
            "primary_action": "Reaction-Wheel Avoidance",
            "survival_prob": 88,
            "explanation": (
                f"Debris {collision['debris_id']} is at "
                f"{collision['distance_km']} km. Propulsion is unavailable, "
                "so use attitude control/reaction wheels for the simulated avoidance maneuver."
            ),
        }

    if collision["imminent"]:
        return {
            "primary_action": "Emergency Collision-Avoidance Maneuver",
            "survival_prob": 90,
            "explanation": (
                f"Debris is inside the {2.0} km critical threshold. "
                "Execute the highest-priority approved avoidance maneuver."
            ),
        }

    if collision.get("warning"):
        return {
            "primary_action": "Prepare Collision-Avoidance Maneuver",
            "survival_prob": 96,
            "explanation": (
                f"Debris is approaching at {collision['distance_km']} km. "
                "Continue monitoring and prepare an avoidance maneuver."
            ),
        }

    return {
        "primary_action": "Continue Nominal Operations",
        "survival_prob": 99,
        "explanation": "No immediate collision threat detected.",
    }


def generate_copilot_forecast(collision: dict, graph_nodes: list[dict]) -> dict:
    """Use Groq if configured; otherwise return deterministic advice."""
    fallback = deterministic_recommendation(collision, graph_nodes)

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        return fallback

    try:
        from groq import Groq

        client = Groq(api_key=api_key)
        prompt = f"""
You are a spacecraft mission-control copilot for a hackathon simulator.
Do not invent telemetry. Use only this state:
Collision: {collision}
Failure graph: {graph_nodes}

Return exactly three lines:
ACTION: <short recommended action>
CONFIDENCE: <integer 0-100>
EXPLANATION: <one concise safety-oriented explanation>
"""
        response = client.chat.completions.create(
            model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=180,
        )

        text = response.choices[0].message.content.strip()
        action = fallback["primary_action"]
        confidence = fallback["survival_prob"]
        explanation = fallback["explanation"]

        for line in text.splitlines():
            if line.upper().startswith("ACTION:"):
                action = line.split(":", 1)[1].strip()
            elif line.upper().startswith("CONFIDENCE:"):
                try:
                    confidence = int(line.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif line.upper().startswith("EXPLANATION:"):
                explanation = line.split(":", 1)[1].strip()

        return {
            "primary_action": action,
            "survival_prob": max(0, min(100, confidence)),
            "explanation": explanation,
        }

    except Exception:
        # Never let an LLM/API problem break the flight-control demo.
        return fallback
