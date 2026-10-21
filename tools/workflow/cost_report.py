#!/usr/bin/env python3
"""Deterministic cost coverage and accepted-result report from receipt files.

The receipt cost_items ledger is authoritative. Provider telemetry is captured
separately and must be represented in that ledger to count toward totals.
Never infer zero cost from a missing platform usage block.
"""
import argparse
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
import sys


def money(value):
    if value is None or isinstance(value, bool):
        return None
    try:
        n = Decimal(str(value))
        if not n.is_finite() or n < 0:
            raise ValueError("cost must be a finite nonnegative number")
        return n
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("invalid cost value") from exc


def report(receipts):
    if not receipts:
        raise ValueError("at least one receipt required")
    seen = set()
    known = Decimal(0)
    all_complete = True
    accepted = 0
    row_details = []
    for receipt in receipts:
        task_id = receipt.get("task_id")
        if not isinstance(task_id, str) or not task_id or task_id in seen:
            raise ValueError("task_id missing or duplicated")
        seen.add(task_id)
        reviewed = receipt.get("review", {}).get("decision") == "ACCEPTED"
        accepted_by_mark = (receipt.get("acceptance", {}).get("decision") == "ACCEPTED"
                            and receipt.get("acceptance", {}).get("authority") == "Mark")
        is_accepted = (receipt.get("status") == "ACCEPTED" and reviewed
                       and accepted_by_mark)
        accepted += int(is_accepted)
        costs = receipt.get("cost_items", [])
        if not isinstance(costs, list):
            raise ValueError("cost_items must be a list")
        subtotal = Decimal(0)
        observed = bool(costs)
        for item in costs:
            if not isinstance(item, dict) or not item.get("label"):
                raise ValueError("each cost item requires label")
            amount = money(item.get("cost_usd"))
            if amount is None:
                observed = False
            else:
                subtotal += amount
        known += subtotal
        complete = (receipt.get("cost_coverage") == "complete"
                    and observed
                    and bool(receipt.get("cost_coverage_explanation")))
        all_complete = all_complete and complete
        row_details.append({"task_id": task_id, "accepted": is_accepted,
                            "coverage_complete": complete,
                            "known_cost_subtotal_usd": str(subtotal)})
    total = str(known) if all_complete else None
    return {"receipt_count": len(receipts),
            "accepted_result_count": accepted,
            "cost_coverage": "complete" if all_complete else "incomplete_or_unknown",
            "known_cost_subtotal_usd": str(known),
            "total_attributable_cost_usd": total,
            "cost_per_accepted_result_usd": str(known / accepted)
                if all_complete and accepted else None,
            "receipts": row_details}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("receipts", nargs="+", type=Path)
    args = p.parse_args()
    try:
        receipts = [json.loads(path.read_text(encoding="utf-8")) for path in args.receipts]
        print(json.dumps(report(receipts), sort_keys=True, indent=2))
    except (OSError, ValueError, TypeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
