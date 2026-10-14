#!/usr/bin/env python3
"""Recompute data/examples.json y labels from Jaccard over incidents_strict.json.

y is the expected top incidents/groups of the matcher, not Gemini text.
No API key is used.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCIDENTS_PATH = ROOT / "data" / "incidents_strict.json"
EXAMPLES_PATH = ROOT / "data" / "examples.json"
TOP_K = 3

QUERIES = [
    ["T1059.001", "T1071.001", "T1105"],
    ["T1059.001", "T1566.001", "T1071.001"],
    ["T1547.001", "T1053.005"],
]


def jaccard(query: set[str], incident: set[str]) -> float:
    if not query or not incident:
        return 0.0
    return len(query & incident) / len(query | incident)


def rank(incidents: list[dict], techniques: list[str], k: int) -> list[dict]:
    query = set(techniques)
    scored = []
    for inc in incidents:
        inc_set = set(inc["techniques"])
        shared = sorted(query & inc_set)
        score = jaccard(query, inc_set)
        if score <= 0:
            continue
        scored.append(
            {
                "incident_id": inc["incident_id"],
                "group": inc["group"],
                "jaccard": round(score, 4),
                "match_percentage": round(100.0 * score, 1),
                "shared_techniques": shared,
            }
        )
    scored.sort(key=lambda m: (-m["jaccard"], -len(m["shared_techniques"]), m["incident_id"]))
    return scored[:k]


def main() -> None:
    incidents = json.loads(INCIDENTS_PATH.read_text(encoding="utf-8"))
    examples = []
    for techniques in QUERIES:
        top = rank(incidents, techniques, TOP_K)
        if not top:
            raise SystemExit(f"No Jaccard hits for {techniques}")
        examples.append(
            {
                "X": {"techniques": techniques},
                "y": {
                    "top_incident_id": top[0]["incident_id"],
                    "top_group": top[0]["group"],
                    "jaccard": top[0]["jaccard"],
                    "match_percentage": top[0]["match_percentage"],
                    "top_incidents": top,
                },
            }
        )
    EXAMPLES_PATH.write_text(json.dumps(examples, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {EXAMPLES_PATH}")
    for i, ex in enumerate(examples, 1):
        print(f"  {i}. {ex['X']['techniques']} -> {ex['y']['top_incident_id']} ({ex['y']['top_group']})")


if __name__ == "__main__":
    main()
