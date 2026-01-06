from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, Optional

from data_service.db import SQLiteAdapter

app = FastAPI(title="Data Service", version="1.0")
db = SQLiteAdapter()


class CreateUserIn(BaseModel):
    name: str


class TrackedItemIn(BaseModel):
    user_id: int
    marketplace: str
    external_id: str
    title: Optional[str] = None
    url: Optional[str] = None


class RuleIn(BaseModel):
    tracked_item_id: int
    rule_type: str  # PRICE_BELOW, DROP_PERCENT, BACK_IN_STOCK
    params: Dict[str, Any]


class SnapshotIn(BaseModel):
    tracked_item_id: int
    price: float
    currency: str
    in_stock: bool


class TriggeredAlertIn(BaseModel):
    alert_rule_id: int
    tracked_item_id: int
    snapshot_id: int
    message: str
    details: Dict[str, Any]


@app.post("/users")
def create_user(payload: CreateUserIn):
    user_id = db.create_user(payload.name)
    return {"user_id": user_id}


@app.post("/tracked-items")
def add_tracked_item(payload: TrackedItemIn):
    item_id = db.add_tracked_item(
        payload.user_id,
        payload.marketplace,
        payload.external_id,
        payload.title,
        payload.url,
    )
    return {"tracked_item_id": item_id}


@app.get("/users/{user_id}/tracked-items")
def get_tracked_items(user_id: int):
    return {"items": db.get_tracked_items(user_id)}


@app.post("/rules")
def add_rule(payload: RuleIn):
    rule_id = db.add_rule(payload.tracked_item_id, payload.rule_type, payload.params)
    return {"rule_id": rule_id}


@app.get("/tracked-items/{tracked_item_id}/rules")
def get_rules(tracked_item_id: int):
    return {"rules": db.get_rules(tracked_item_id)}


@app.post("/snapshots")
def insert_snapshot(payload: SnapshotIn):
    snapshot_id = db.insert_snapshot(payload.tracked_item_id, payload.price, payload.currency, payload.in_stock)
    return {"snapshot_id": snapshot_id}


@app.get("/tracked-items/{tracked_item_id}/latest-snapshot")
def latest_snapshot(tracked_item_id: int):
    snap = db.get_latest_snapshot(tracked_item_id)
    return {"snapshot": snap}


@app.post("/triggered-alerts")
def insert_triggered_alert(payload: TriggeredAlertIn):
    alert_id = db.insert_triggered_alert(
        payload.alert_rule_id,
        payload.tracked_item_id,
        payload.snapshot_id,
        payload.message,
        payload.details,
    )
    db.update_rule_last_triggered(payload.alert_rule_id, payload.snapshot_id)
    return {"triggered_alert_id": alert_id}


@app.get("/users/{user_id}/alerts")
def get_alerts(user_id: int):
    return {"alerts": db.get_user_alerts(user_id)}
