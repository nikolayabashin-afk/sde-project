PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tracked_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  marketplace TEXT NOT NULL,
  external_id TEXT NOT NULL,
  title TEXT,
  url TEXT,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(user_id, marketplace, external_id),
  FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS alert_rules (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tracked_item_id INTEGER NOT NULL,
  rule_type TEXT NOT NULL,          -- PRICE_BELOW, DROP_PERCENT, BACK_IN_STOCK
  params_json TEXT NOT NULL,        -- JSON string
  is_enabled INTEGER NOT NULL DEFAULT 1,
  last_triggered_snapshot_id INTEGER,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  FOREIGN KEY(tracked_item_id) REFERENCES tracked_items(id)
);

CREATE TABLE IF NOT EXISTS price_snapshots (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tracked_item_id INTEGER NOT NULL,
  ts TEXT NOT NULL DEFAULT (datetime('now')),
  price REAL NOT NULL,
  currency TEXT NOT NULL,
  in_stock INTEGER NOT NULL,        -- 1/0
  FOREIGN KEY(tracked_item_id) REFERENCES tracked_items(id)
);

CREATE TABLE IF NOT EXISTS triggered_alerts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  alert_rule_id INTEGER NOT NULL,
  tracked_item_id INTEGER NOT NULL,
  snapshot_id INTEGER NOT NULL,
  ts TEXT NOT NULL DEFAULT (datetime('now')),
  message TEXT NOT NULL,
  details_json TEXT NOT NULL,       -- JSON string
  FOREIGN KEY(alert_rule_id) REFERENCES alert_rules(id),
  FOREIGN KEY(tracked_item_id) REFERENCES tracked_items(id),
  FOREIGN KEY(snapshot_id) REFERENCES price_snapshots(id)
);
