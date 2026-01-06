from fastapi import FastAPI
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

app = FastAPI(title="Alert Engine Service", version="1.0")


class PriceState(BaseModel):
    price: float
    currency: str
    in_stock: bool


class Rule(BaseModel):
    id: int
    rule_type: str  # PRICE_BELOW, DROP_PERCENT, BACK_IN_STOCK
    params: Dict[str, Any]
    last_triggered_snapshot_id: Optional[int] = None


class EvaluateIn(BaseModel):
    tracked_item_id: int
    current: PriceState
    previous: Optional[PriceState] = None
    rules: List[Rule]


class Triggered(BaseModel):
    rule_id: int
    message: str
    details: Dict[str, Any]


class EvaluateOut(BaseModel):
    triggered: List[Triggered]


def percent_drop(prev: float, cur: float) -> float:
    if prev <= 0:
        return 0.0
    return (prev - cur) / prev * 100.0


@app.post("/evaluate-alerts", response_model=EvaluateOut)
def evaluate(payload: EvaluateIn):
    triggered: List[Triggered] = []
    cur = payload.current
    prev = payload.previous

    for rule in payload.rules:
        rt = rule.rule_type.upper()

        if rt == "PRICE_BELOW":
            target = float(rule.params.get("target", 0))
            if cur.price <= target:
                triggered.append(
                    Triggered(
                        rule_id=rule.id,
                        message=f"Price is below target ({target})",
                        details={"price": cur.price, "target": target},
                    )
                )

        elif rt == "DROP_PERCENT" and prev is not None:
            threshold = float(rule.params.get("percent", 0))
            drop = percent_drop(prev.price, cur.price)
            if drop >= threshold:
                triggered.append(
                    Triggered(
                        rule_id=rule.id,
                        message=f"Price dropped by {drop:.2f}% (>= {threshold}%)",
                        details={
                            "prev_price": prev.price,
                            "price": cur.price,
                            "drop_percent": drop,
                            "threshold": threshold,
                        },
                    )
                )

        elif rt == "BACK_IN_STOCK" and prev is not None:
            if (not prev.in_stock) and cur.in_stock:
                triggered.append(
                    Triggered(
                        rule_id=rule.id,
                        message="Item is back in stock",
                        details={"prev_in_stock": prev.in_stock, "in_stock": cur.in_stock},
                    )
                )

    return EvaluateOut(triggered=triggered)
