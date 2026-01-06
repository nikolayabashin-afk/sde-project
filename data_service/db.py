import sqlite3
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).parent / "data.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class SQLiteAdapter:
    def __init__(self) -> None:
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys = ON;")
        return con

    def _init_db(self) -> None:
        if not DB_PATH.exists():
            DB_PATH.touch()
        with self._connect() as con:
            con.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
            con.commit()

    # Users
    def create_user(self, name: str) -> int:
        with self._connect() as con:
            cur = con.execute("INSERT INTO users(name) VALUES (?)", (name,))
            con.commit()
            return int(cur.lastrowid)

    # Tracked Items
    def add_tracked_item(
        self,
        user_id: int,
        marketplace: str,
        external_id: str,
        title: Optional[str],
        url: Optional[str],
    ) -> int:
        with self._connect() as con:
            con.execute(
                """INSERT OR IGNORE INTO tracked_items(user_id, marketplace, external_id, title, url)
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, marketplace, external_id, title, url),
            )
            con.commit()
            row = con.execute(
                "SELECT id FROM tracked_items WHERE user_id=? AND marketplace=? AND external_id=?",
                (user_id, marketplace, external_id),
            ).fetchone()
            return int(row["id"])

    def get_tracked_items(self, user_id: int) -> List[Dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT * FROM tracked_items WHERE user_id=? AND is_active=1",
                (user_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    # Rules
    def add_rule(self, tracked_item_id: int, rule_type: str, params: Dict[str, Any]) -> int:
        with self._connect() as con:
            cur = con.execute(
                "INSERT INTO alert_rules(tracked_item_id, rule_type, params_json) VALUES (?, ?, ?)",
                (tracked_item_id, rule_type, json.dumps(params)),
            )
            con.commit()
            return int(cur.lastrowid)

    def get_rules(self, tracked_item_id: int) -> List[Dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute(
                "SELECT * FROM alert_rules WHERE tracked_item_id=? AND is_enabled=1",
                (tracked_item_id,),
            ).fetchall()
            out: List[Dict[str, Any]] = []
            for r in rows:
                d = dict(r)
                d["params"] = json.loads(d.pop("params_json"))
                out.append(d)
            return out

    def update_rule_last_triggered(self, rule_id: int, snapshot_id: int) -> None:
        with self._connect() as con:
            con.execute(
                "UPDATE alert_rules SET last_triggered_snapshot_id=? WHERE id=?",
                (snapshot_id, rule_id),
            )
            con.commit()

    # Snapshots
    def insert_snapshot(self, tracked_item_id: int, price: float, currency: str, in_stock: bool) -> int:
        with self._connect() as con:
            cur = con.execute(
                """INSERT INTO price_snapshots(tracked_item_id, price, currency, in_stock)
                   VALUES (?, ?, ?, ?)""",
                (tracked_item_id, float(price), currency, 1 if in_stock else 0),
            )
            con.commit()
            return int(cur.lastrowid)

    def get_latest_snapshot(self, tracked_item_id: int) -> Optional[Dict[str, Any]]:
        with self._connect() as con:
            row = con.execute(
                """SELECT * FROM price_snapshots
                   WHERE tracked_item_id=?
                   ORDER BY id DESC LIMIT 1""",
                (tracked_item_id,),
            ).fetchone()
            return dict(row) if row else None

    # Triggered Alerts
    def insert_triggered_alert(
        self,
        rule_id: int,
        tracked_item_id: int,
        snapshot_id: int,
        message: str,
        details: Dict[str, Any],
    ) -> int:
        with self._connect() as con:
            cur = con.execute(
                """INSERT INTO triggered_alerts(alert_rule_id, tracked_item_id, snapshot_id, message, details_json)
                   VALUES (?, ?, ?, ?, ?)""",
                (rule_id, tracked_item_id, snapshot_id, message, json.dumps(details)),
            )
            con.commit()
            return int(cur.lastrowid)

    def get_user_alerts(self, user_id: int) -> List[Dict[str, Any]]:
        with self._connect() as con:
            rows = con.execute(
                """
                SELECT ta.*, ti.user_id
                FROM triggered_alerts ta
                JOIN tracked_items ti ON ti.id = ta.tracked_item_id
                WHERE ti.user_id=?
                ORDER BY ta.id DESC
                """,
                (user_id,),
            ).fetchall()
            out: List[Dict[str, Any]] = []
            for r in rows:
                d = dict(r)
                d["details"] = json.loads(d.pop("details_json"))
                out.append(d)
            return out
