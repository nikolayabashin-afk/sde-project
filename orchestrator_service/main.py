import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

app = FastAPI(title="Orchestrator Service", version="1.0")

DATA_URL = "http://127.0.0.1:8001"
ADAPTER_URL = "http://127.0.0.1:8002"
LOGIC_URL = "http://127.0.0.1:8003"


class RunIn(BaseModel):
    user_id: int


@app.post("/run-cycle")
def run_cycle(payload: RunIn):
    user_id = payload.user_id

    # 1) Get tracked items
    r = requests.get(f"{DATA_URL}/users/{user_id}/tracked-items", timeout=10)
    if r.status_code != 200:
        raise HTTPException(status_code=502, detail="Data service failed to return tracked items")
    items = r.json().get("items", [])

    results: List[Dict[str, Any]] = []

    for item in items:
        tracked_item_id = item["id"]
        marketplace = item["marketplace"]
        external_id = item["external_id"]

        # 2) Get latest snapshot (previous)
        prev_resp = requests.get(f"{DATA_URL}/tracked-items/{tracked_item_id}/latest-snapshot", timeout=10)
        prev_snapshot = prev_resp.json().get("snapshot")

        # 3) Get rules for item
        rules_resp = requests.get(f"{DATA_URL}/tracked-items/{tracked_item_id}/rules", timeout=10)
        rules = rules_resp.json().get("rules", [])

        # 4) Query adapter for current price/stock
        cur_resp = requests.get(
            f"{ADAPTER_URL}/marketplace/price-stock",
            params={"marketplace": marketplace, "external_id": external_id},
            timeout=10,
        )
        if cur_resp.status_code != 200:
            results.append({"tracked_item_id": tracked_item_id, "error": "Adapter failed"})
            continue

        current = cur_resp.json()

        # 5) Store snapshot in Data Service
        snap_resp = requests.post(
            f"{DATA_URL}/snapshots",
            json={
                "tracked_item_id": tracked_item_id,
                "price": current["price"],
                "currency": current["currency"],
                "in_stock": current["in_stock"],
            },
            timeout=10,
        )
        snapshot_id = snap_resp.json().get("snapshot_id")

        # 6) Evaluate alerts in Business Logic
        eval_resp = requests.post(
            f"{LOGIC_URL}/evaluate-alerts",
            json={
                "tracked_item_id": tracked_item_id,
                "current": {
                    "price": current["price"],
                    "currency": current["currency"],
                    "in_stock": current["in_stock"],
                },
                "previous": None if not prev_snapshot else {
                    "price": prev_snapshot["price"],
                    "currency": prev_snapshot["currency"],
                    "in_stock": bool(prev_snapshot["in_stock"]),
                },
                "rules": [
                    {
                        "id": rule["id"],
                        "rule_type": rule["rule_type"],
                        "params": rule["params"],
                        "last_triggered_snapshot_id": rule.get("last_triggered_snapshot_id"),
                    }
                    for rule in rules
                ],
            },
            timeout=10,
        )

        triggered = eval_resp.json().get("triggered", [])

        # 7) Persist triggered alerts
        persisted_alerts = 0
        for t in triggered:
            requests.post(
                f"{DATA_URL}/triggered-alerts",
                json={
                    "alert_rule_id": t["rule_id"],
                    "tracked_item_id": tracked_item_id,
                    "snapshot_id": snapshot_id,
                    "message": t["message"],
                    "details": t["details"],
                },
                timeout=10,
            )
            persisted_alerts += 1

        results.append(
            {
                "tracked_item_id": tracked_item_id,
                "marketplace": marketplace,
                "external_id": external_id,
                "snapshot_id": snapshot_id,
                "triggered_count": persisted_alerts,
                "triggered": triggered,
            }
        )

    return {"user_id": user_id, "results": results}
