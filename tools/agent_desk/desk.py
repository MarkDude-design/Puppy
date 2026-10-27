#!/usr/bin/env python3
"""Offline validator and failover rehearsal for Puppf's 2+1 helper desk.

No network, provider clients, secret access, files written or GitHub actions.
This is a coordination test, NOT a live multi-agent dispatcher.
"""
import argparse
import json
from pathlib import Path
import sys

STATES = {"READY", "ACTIVE", "STANDBY", "BLOCKED", "COMPLETE", "STOPPED"}
BUSY = {"READY", "ACTIVE"}
SLOTS = {"H1", "H2", "R"}
SCHEMA = "puppf-agent-desk/0"


class InvalidDesk(ValueError):
    pass


def no_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise InvalidDesk("duplicate JSON key: " + key)
        value[key] = item
    return value


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"),
                      object_pairs_hook=no_duplicate_keys)


def validate(doc):
    if not isinstance(doc, dict) or doc.get("schema_version") != SCHEMA:
        raise InvalidDesk("invalid desk schema")
    if doc.get("active_limit") != 2 or type(doc["active_limit"]) is not int:
        raise InvalidDesk("exactly two possible active helper slots in pilot")
    if not isinstance(doc.get("source_commit"), str) or len(doc["source_commit"]) != 40:
        raise InvalidDesk("source_commit must be a full 40-character SHA")
    if not all(c in "0123456789abcdef" for c in doc["source_commit"]):
        raise InvalidDesk("source_commit must be lowercase hex")
    if not isinstance(doc.get("parent_task_id"), str) or not doc["parent_task_id"]:
        raise InvalidDesk("parent_task_id required")
    if doc.get("paid_calls_allowed") is not False:
        raise InvalidDesk("pilot does not authorize external paid calls")
    tasks = doc.get("tasks")
    if not isinstance(tasks, list) or len(tasks) != 3:
        raise InvalidDesk("pilot requires H1, H2 and one standby R task")
    ids, slots, busy = set(), set(), []
    for task in tasks:
        if not isinstance(task, dict):
            raise InvalidDesk("each task must be an object")
        slot = task.get("slot")
        task_id = task.get("task_id")
        if slot not in SLOTS or slot in slots:
            raise InvalidDesk("invalid or duplicate helper slot")
        if not isinstance(task_id, str) or not task_id or task_id in ids:
            raise InvalidDesk("task_id absent or duplicated")
        ids.add(task_id)
        slots.add(slot)
        state = task.get("state")
        if state not in STATES:
            raise InvalidDesk("invalid task state: " + str(state))
        if slot == "R" and state == "ACTIVE" and not task.get("replaces"):
            raise InvalidDesk("reserve cannot activate without named replacement")
        if not isinstance(task.get("question"), str) or not task["question"].strip():
            raise InvalidDesk("each helper needs one substantive question")
        if task.get("read_only") is not True:
            raise InvalidDesk("helper may not write repository changes")
        paths = task.get("inputs")
        if not isinstance(paths, list) or not paths or not all(
                isinstance(path, str) and path and ".." not in path for path in paths):
            raise InvalidDesk("helper needs named public-safe input paths")
        words = task.get("max_words")
        if type(words) is not int or not 1 <= words <= 800:
            raise InvalidDesk("max_words must be an integer from 1 to 800")
        if task.get("cost_usd") is not None or task.get("model_observed") is not None:
            raise InvalidDesk("planning queue cannot invent observed model/cost data")
        if task.get("provider") is not None or task.get("model_requested") is not None:
            raise InvalidDesk("model/provider assignment needs a later authorized dispatch")
        if state in BUSY:
            busy.append(slot)
    if slots != SLOTS:
        raise InvalidDesk("must have H1 H2 R slots")
    if len(busy) > doc["active_limit"]:
        raise InvalidDesk("more than two ready or active helpers")
    if any(task["slot"] == "R" and task["state"] in BUSY for task in tasks):
        if not any(task["slot"] in {"H1", "H2"} and task["state"] == "BLOCKED"
                   for task in tasks):
            raise InvalidDesk("reserve may only substitute for blocked H1 or H2")
    return {"schema_version": SCHEMA, "valid": True,
            "planned_busy_slots": sorted(busy),
            "standby_slots": sorted(x["slot"] for x in tasks if x["state"] == "STANDBY"),
            "paid_calls_allowed": False, "actual_dispatches": 0}


def simulate_failover(doc, blocked_slot):
    validate(doc)
    if blocked_slot not in {"H1", "H2"}:
        raise InvalidDesk("failover requires blocked H1 or H2")
    # Round-trip copy: never change source queue on disk.
    proposed = json.loads(json.dumps(doc))
    items = {t["slot"]: t for t in proposed["tasks"]}
    if items[blocked_slot]["state"] not in BUSY:
        raise InvalidDesk("requested helper was not available for first dispatch")
    if items["R"]["state"] != "STANDBY":
        raise InvalidDesk("reserve not in standby state")
    items[blocked_slot]["state"] = "BLOCKED"
    items["R"]["state"] = "READY"
    items["R"]["replaces"] = blocked_slot
    result = validate(proposed)
    return {"simulation_only": True, "blocked": blocked_slot,
            "reserve_replaces": blocked_slot, "proposal": proposed, "validation": result}


ROUTES = {"native_subagent", "api_consult", "native_ferry"}
ROUTE_NOTES = {
    "native_subagent": "Requires verified access to native Codex subagent capability.",
    "api_consult": "Needs separate model/provider, authorization, enforced key cap and usage receipts.",
    "native_ferry": "Human-mediated GitHub handoff only; does not wake a native chat.",
}


def preview_combo(doc, h1_route, h2_route):
    """Non-executing comparison of two possible helper transport routes."""
    validate(doc)
    if h1_route not in ROUTES or h2_route not in ROUTES:
        raise InvalidDesk("unsupported helper route")
    return {"simulation_only": True, "actual_agent_calls": 0,
            "planned_slots": {"H1": h1_route, "H2": h2_route, "R": "STANDBY"},
            "route_caveats": {"H1": ROUTE_NOTES[h1_route],
                             "H2": ROUTE_NOTES[h2_route]},
            "independence_claim": "not established until actual model/provider evidence",
            "paid_calls_allowed": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["validate", "simulate-failover", "preview-combo"])
    parser.add_argument("queue", type=Path)
    parser.add_argument("--blocked", choices=["H1", "H2"])
    parser.add_argument("--h1-route", choices=sorted(ROUTES))
    parser.add_argument("--h2-route", choices=sorted(ROUTES))
    args = parser.parse_args()
    try:
        doc = load(args.queue)
        if args.command == "simulate-failover":
            if args.blocked is None:
                parser.error("--blocked H1|H2 required for simulation")
            result = simulate_failover(doc, args.blocked)
        elif args.command == "preview-combo":
            if args.h1_route is None or args.h2_route is None:
                parser.error("--h1-route and --h2-route required")
            result = preview_combo(doc, args.h1_route, args.h2_route)
        else:
            result = validate(doc)
    except (OSError, ValueError, TypeError) as exc:
        print("BLOCKED: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
