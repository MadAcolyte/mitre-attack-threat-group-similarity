#!/usr/bin/env python3
"""Regenerate data/examples.json from live Gemini API responses.

Keeps the existing X.techniques inputs. Refuses to write unless every y
payload was produced by Gemini (not the TF-IDF/Jaccard fallback) and
validates the examples.json `y` shape.

Usage:
    export GEMINI_API_KEY=...
    python scripts/regenerate_examples.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INCIDENTS_PATH = ROOT / "data" / "incidents_strict.json"
PROMPT_PATH = ROOT / "prompts" / "prompt.json"
EXAMPLES_PATH = ROOT / "data" / "examples.json"

TECHNIQUE_RE = re.compile(r"^T\d{4}(\.\d{3})?$", re.IGNORECASE)
GENERATION_MODEL = os.environ.get("GEMINI_GENERATION_MODEL", "gemini-2.5-flash")
TOP_K = 8


def die(message: str, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def process_query(raw_techniques: list[str], known: set[str]) -> list[str]:
    techniques: list[str] = []
    seen: set[str] = set()
    for raw in raw_techniques:
        token = str(raw).strip().upper()
        if not TECHNIQUE_RE.fullmatch(token):
            die(f"Invalid technique ID in examples.json X: {raw!r}")
        if token in seen:
            continue
        seen.add(token)
        techniques.append(token)
        if token not in known:
            print(f"WARNING: {token} is not in incidents_strict.json")
    if not techniques:
        die("Query has no valid technique IDs")
    return techniques


def jaccard(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def retrieve(incidents: list[dict], techniques: list[str], k: int) -> list[dict]:
    scored = []
    for incident in incidents:
        score = jaccard(techniques, incident["techniques"])
        scored.append((score, incident))
    scored.sort(key=lambda row: row[0], reverse=True)
    hits = []
    for score, incident in scored[:k]:
        hits.append(
            {
                "score": round(float(score), 4),
                "incident": incident,
            }
        )
    return hits


def format_incidents(retrieved: list[dict]) -> str:
    blocks = []
    for hit in retrieved:
        inc = hit["incident"]
        blocks.append(
            "\n".join(
                [
                    f"- incident_id: {inc['incident_id']}",
                    f"  group: {inc['group']}",
                    f"  retrieval_score: {hit['score']}",
                    f"  techniques: {', '.join(inc['techniques'])}",
                    f"  description: {inc['description']}",
                ]
            )
        )
    return "\n".join(blocks)


def parse_model_json(text: str) -> dict:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
        cleaned = re.sub(r"\s*```$", "", cleaned)
    payload = json.loads(cleaned)
    if not isinstance(payload, dict) or not isinstance(payload.get("groups"), list):
        raise ValueError("Gemini output missing groups list")
    if not payload["groups"]:
        raise ValueError("Gemini returned an empty groups list")
    for group in payload["groups"][:3]:
        if not isinstance(group, dict):
            raise ValueError("group entry is not an object")
        for key in (
            "name",
            "match_percentage",
            "matching_techniques",
            "similar_incidents",
            "reasoning",
        ):
            if key not in group:
                raise ValueError(f"group missing {key}")
        if not isinstance(group["match_percentage"], (int, float)):
            raise ValueError("match_percentage must be numeric")
        if not 0 <= float(group["match_percentage"]) <= 100:
            raise ValueError("match_percentage out of range")
    return {"groups": payload["groups"][:3]}


def call_gemini(client, prompt_spec: dict, techniques: list[str], retrieved: list[dict]) -> dict:
    from google.genai import types

    user_prompt = (
        prompt_spec["user_prompt_template"]
        .replace("{{techniques}}", json.dumps(techniques, ensure_ascii=False))
        .replace("{{incidents}}", format_incidents(retrieved))
    )
    response = client.models.generate_content(
        model=GENERATION_MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=prompt_spec["system_prompt"],
            response_mime_type="application/json",
            temperature=0.2,
        ),
    )
    if not response.text:
        raise RuntimeError("Gemini returned an empty response")
    return parse_model_json(response.text)


def main() -> None:
    api_key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    if not api_key:
        die(
            "Refusing to run: GEMINI_API_KEY is not set. "
            "This script will not write placeholder/fake y payloads."
        )

    incidents = json.loads(INCIDENTS_PATH.read_text(encoding="utf-8"))
    prompt_spec = json.loads(PROMPT_PATH.read_text(encoding="utf-8"))
    examples = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
    known = {tid for incident in incidents for tid in incident["techniques"]}

    from google import genai

    client = genai.Client(api_key=api_key)
    updated = []
    for i, example in enumerate(examples, start=1):
        techniques = process_query(example["X"]["techniques"], known)
        retrieved = retrieve(incidents, techniques, TOP_K)
        print(f"[{i}/{len(examples)}] Gemini {GENERATION_MODEL} for {techniques} …")
        try:
            y = call_gemini(client, prompt_spec, techniques, retrieved)
        except Exception as exc:
            die(f"Gemini failed on example {i}; leaving {EXAMPLES_PATH} unchanged. ({exc})")
        updated.append({"X": {"techniques": techniques}, "y": y})
        print(f"  groups: {[g['name'] for g in y['groups']]}")

    EXAMPLES_PATH.write_text(json.dumps(updated, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote live Gemini outputs to {EXAMPLES_PATH}")


if __name__ == "__main__":
    main()
