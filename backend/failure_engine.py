"""NetworkX-based cascading failure engine for SpaceWise."""

from __future__ import annotations

import networkx as nx


FAILURE_GRAPH = nx.DiGraph()

# dependency: upstream component -> downstream component
FAILURE_GRAPH.add_edges_from([
    ("battery", "thermal"),
    ("thermal", "comms"),
    ("comms", "propulsion"),
])

NODE_LABELS = {
    "battery": "Battery (Origin)",
    "thermal": "Thermal Control",
    "comms": "Communication",
    "propulsion": "Propulsion",
}

FAILURE_DELAYS = {
    "battery": 0,
    "thermal": 14,
    "comms": 35,
    "propulsion": 53,
}


def build_failure_state(origin: str = "battery") -> list[dict]:
    """Return graph nodes with status and T+ propagation delay."""
    if origin not in FAILURE_GRAPH:
        raise ValueError(f"Unknown failure origin: {origin}")

    affected = {origin}
    affected.update(nx.descendants(FAILURE_GRAPH, origin))

    nodes = []
    for node in FAILURE_GRAPH.nodes:
        if node == origin:
            status = "CRITICAL"
        elif node in affected:
            status = "WATCH"
        else:
            status = "NOMINAL"

        nodes.append({
            "id": node,
            "status": status,
            "label": NODE_LABELS[node],
            "delay": f"T+{FAILURE_DELAYS[node]}s",
        })

    return nodes


def get_failure_path(origin: str = "battery") -> list[dict]:
    """Return the exact directed propagation path."""
    path = [origin]
    current = origin

    while True:
        next_nodes = list(FAILURE_GRAPH.successors(current))
        if not next_nodes:
            break
        current = next_nodes[0]
        path.append(current)

    return [
        {
            "id": node,
            "label": NODE_LABELS[node],
            "delay": f"T+{FAILURE_DELAYS[node]}s",
        }
        for node in path
    ]
