"""SpaceWise AI Flight Control Copilot."""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv

load_dotenv()


def deterministic_recommendation(
    collision: dict,
    graph_nodes: list[dict],
    telemetry: dict | None = None,
) -> dict:
    """Instant local fallback. Works without Groq or internet."""

    telemetry = telemetry or {}

    propulsion_telemetry = telemetry.get("propulsion", {})
    propulsion_status = propulsion_telemetry.get("status")

    propulsion_node = next(
        (n for n in graph_nodes if n.get("id") == "propulsion"),
        None,
    )

    propulsion_critical = (
        propulsion_status == "CRITICAL"
        or (
            propulsion_node
            and propulsion_node.get("status") == "CRITICAL"
        )
    )

    battery_telemetry = telemetry.get("battery", {})
    battery_critical = battery_telemetry.get("status") == "CRITICAL"

    imminent = collision.get("imminent", False)
    warning = collision.get("warning", False)
    distance = collision.get("distance_km", 999)
    debris_id = collision.get("debris_id", "UNKNOWN")

    # 1. IMMINENT COLLISION + CRITICAL PROPULSION
    if imminent and propulsion_critical:
        recommended = "Reaction-Wheel Avoidance"

        options = [
            {
                "strategy": "Reaction-Wheel Avoidance",
                "survival_percent": 88,
                "risk_reduction": 86,
                "energy_impact": "Low",
                "science_impact": "Medium",
            },
            {
                "strategy": "Emergency Safe-Mode",
                "survival_percent": 82,
                "risk_reduction": 78,
                "energy_impact": "Low",
                "science_impact": "High",
            },
            {
                "strategy": "Maintain Current Operations",
                "survival_percent": 35,
                "risk_reduction": 15,
                "energy_impact": "High",
                "science_impact": "Low",
            },
        ]

        explanation = (
            f"Debris {debris_id} is at {distance} km while propulsion is already critical. "
            "The battery cascade further reduces system margin, so immediate attitude-control "
            "avoidance is the safest available response."
        )

    # 2. IMMINENT COLLISION
    elif imminent:
        recommended = "Emergency Collision-Avoidance Maneuver"

        options = [
            {
                "strategy": "Emergency Collision-Avoidance Maneuver",
                "survival_percent": 90,
                "risk_reduction": 94,
                "energy_impact": "High",
                "science_impact": "Medium",
            },
            {
                "strategy": "Power-Conservation Mode",
                "survival_percent": 76,
                "risk_reduction": 55,
                "energy_impact": "Low",
                "science_impact": "High",
            },
            {
                "strategy": "Maintain Current Operations",
                "survival_percent": 30,
                "risk_reduction": 10,
                "energy_impact": "High",
                "science_impact": "Low",
            },
        ]

        explanation = (
            f"Debris is inside the 2.0 km critical threshold at {distance} km. "
            "Immediate collision avoidance is the highest-priority response."
        )

    # 3. WARNING ZONE
    elif warning:
        recommended = "Prepare Collision-Avoidance Maneuver"

        options = [
            {
                "strategy": "Prepare Collision-Avoidance Maneuver",
                "survival_percent": 96,
                "risk_reduction": 82,
                "energy_impact": "Medium",
                "science_impact": "Medium",
            },
            {
                "strategy": "Power-Conservation Mode",
                "survival_percent": 91,
                "risk_reduction": 65,
                "energy_impact": "Low",
                "science_impact": "Medium",
            },
            {
                "strategy": "Continue Monitoring",
                "survival_percent": 80,
                "risk_reduction": 30,
                "energy_impact": "Low",
                "science_impact": "High",
            },
        ]

        if battery_critical:
            explanation = (
                f"Debris {debris_id} is approaching at {distance} km while the battery "
                "is critical. Prepare an avoidance response while conserving available power."
            )
        else:
            explanation = (
                f"Debris {debris_id} is approaching at {distance} km. "
                "Continue monitoring while preparing an avoidance response."
            )

    # 4. NOMINAL
    else:
        recommended = "Continue Nominal Operations"

        options = [
            {
                "strategy": "Continue Nominal Operations",
                "survival_percent": 99,
                "risk_reduction": 5,
                "energy_impact": "Low",
                "science_impact": "High",
            },
            {
                "strategy": "Power-Conservation Mode",
                "survival_percent": 97,
                "risk_reduction": 15,
                "energy_impact": "Low",
                "science_impact": "Medium",
            },
            {
                "strategy": "Prepare Avoidance Maneuver",
                "survival_percent": 95,
                "risk_reduction": 20,
                "energy_impact": "Medium",
                "science_impact": "Medium",
            },
        ]

        if battery_critical:
            explanation = (
                "No immediate collision threat is detected, but the battery is critical. "
                "Continue monitoring while maintaining power reserves."
            )
        else:
            explanation = "No immediate collision threat detected."

    return {
        "diagnostic_explanation": explanation,
        "recommended_action": recommended,
        "response_options": options,

        # Compatibility with current dashboard
        "primary_action": recommended,
        "survival_prob": options[0]["survival_percent"],
        "explanation": explanation,
    }


def generate_copilot_forecast(
    collision: dict,
    graph_nodes: list[dict],
    telemetry: dict | None = None,
) -> dict:
    """Use Groq when configured, otherwise use the local fallback."""

    fallback = deterministic_recommendation(
        collision,
        graph_nodes,
        telemetry,
    )

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return fallback

    try:
        from groq import Groq

        client = Groq(api_key=api_key)

        prompt = f"""
You are SpaceWise, an AI spacecraft mission-control copilot.

Analyze ONLY the supplied spacecraft state.

TELEMETRY:
{json.dumps(telemetry or {})}

COLLISION STATE:
{json.dumps(collision)}

FAILURE CASCADE:
{json.dumps(graph_nodes)}

Return ONLY valid JSON using exactly this structure:

{{
  "diagnostic_explanation": "Exactly 2 concise sentences explaining the anomaly and cascade.",
  "recommended_action": "Safest recommended procedure",
  "response_options": [
    {{
      "strategy": "Strategy name",
      "survival_percent": 0,
      "risk_reduction": 0,
      "energy_impact": "Low",
      "science_impact": "Low"
    }},
    {{
      "strategy": "Strategy name",
      "survival_percent": 0,
      "risk_reduction": 0,
      "energy_impact": "Medium",
      "science_impact": "Medium"
    }},
    {{
      "strategy": "Strategy name",
      "survival_percent": 0,
      "risk_reduction": 0,
      "energy_impact": "High",
      "science_impact": "High"
    }}
  ]
}}

Rules:
- survival_percent must be between 0 and 100.
- risk_reduction must be between 0 and 100.
- Do not invent telemetry.
- Use telemetry, collision state, and failure cascade together.
- Critical telemetry must influence the recommended response.
- Consider both spacecraft failures and debris proximity.
- Keep the response concise.
"""

        response = client.chat.completions.create(
            model=os.getenv(
                "GROQ_MODEL",
                "openai/gpt-oss-120b",
            ),
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a safety-focused spacecraft "
                        "mission-control copilot."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            max_tokens=700,
            response_format={"type": "json_object"},
        )

        text = response.choices[0].message.content.strip()
        result = json.loads(text)

        if not isinstance(result, dict):
            return fallback

        if "diagnostic_explanation" not in result:
            return fallback

        if "recommended_action" not in result:
            return fallback

        if not isinstance(result.get("response_options"), list):
            return fallback

        if len(result["response_options"]) != 3:
            return fallback

        result["primary_action"] = result["recommended_action"]

        result["survival_prob"] = int(
            result["response_options"][0].get(
                "survival_percent",
                0,
            )
        )

        result["explanation"] = result["diagnostic_explanation"]

        return result

    except Exception:
        # Groq/API failure must NEVER break the demo.
        return fallback