#!/usr/bin/env python3
"""Apply incremental SQLite schema migrations for AgriMove AI."""

import os
import sqlite3
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

CROP_SWAHILI = {
    "maize": "Mahindi",
    "rice": "Mpunga",
    "tomatoes": "Nyanya",
    "beans": "Maharagwe",
    "cabbage": "Kabichi",
    "potatoes": "Viazi",
    "cassava": "Muhogo",
    "onions": "Vitunguu",
    "coffee": "Kahawa",
    "cashews": "Korosho",
}


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def table_columns(conn, table):
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {row["name"] for row in rows}


def ensure_migrations_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version INTEGER NOT NULL UNIQUE,
            name TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )
        """
    )
    conn.commit()


def applied_versions(conn):
    ensure_migrations_table(conn)
    rows = conn.execute("SELECT version FROM schema_migrations ORDER BY version").fetchall()
    return {row["version"] for row in rows}


def record_migration(conn, version, name):
    conn.execute(
        "INSERT INTO schema_migrations (version, name, applied_at) VALUES (?, ?, ?)",
        (version, name, datetime.now().isoformat(timespec="seconds")),
    )


def add_column_if_missing(conn, table, column, definition):
    if column not in table_columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
        print(f"  + {table}.{column}")


def migration_001_buyers_table(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS buyers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    print("  + buyers table ready")


def migration_002_market_prices_columns(conn):
    add_column_if_missing(conn, "market_prices", "crop_name_swahili", "TEXT")
    add_column_if_missing(conn, "market_prices", "market_name", "TEXT")
    add_column_if_missing(conn, "market_prices", "price_per_kg_tzs", "REAL DEFAULT 0.0")
    add_column_if_missing(conn, "market_prices", "price_trend", "TEXT DEFAULT 'stable'")
    add_column_if_missing(conn, "market_prices", "last_updated", "TEXT")


def migration_003_backfill_market_prices(conn):
    rows = conn.execute("SELECT id, crop_name, region, price, updated_at FROM market_prices").fetchall()
    for row in rows:
        swahili = CROP_SWAHILI.get(row["crop_name"].lower(), row["crop_name"])
        market_name = f"{row['region']} Market"
        price_per_kg = round(row["price"] / 100, 2) if row["price"] else 0.0
        conn.execute(
            """
            UPDATE market_prices
            SET crop_name_swahili = COALESCE(crop_name_swahili, ?),
                market_name = COALESCE(market_name, ?),
                price_per_kg_tzs = CASE
                    WHEN price_per_kg_tzs IS NULL OR price_per_kg_tzs = 0 THEN ?
                    ELSE price_per_kg_tzs
                END,
                price_trend = COALESCE(price_trend, 'stable'),
                last_updated = COALESCE(last_updated, ?)
            WHERE id = ?
            """,
            (swahili, market_name, price_per_kg, row["updated_at"], row["id"]),
        )
    print(f"  ~ backfilled {len(rows)} market_prices rows")


def migration_004_transport_callbacks(conn):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS transport_callbacks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL UNIQUE,
            source TEXT DEFAULT 'voice',
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
        """
    )
    print("  + transport_callbacks table ready")


MIGRATIONS = [
    (1, "buyers_table", migration_001_buyers_table),
    (2, "market_prices_columns", migration_002_market_prices_columns),
    (3, "backfill_market_prices", migration_003_backfill_market_prices),
    (4, "transport_callbacks", migration_004_transport_callbacks),
]


def run_migrations():
    if not os.path.exists(DATABASE):
        print(f"No database at {DATABASE}. Run the app once to create it, or copy database.db.")
        return 1

    conn = get_connection()
    done = applied_versions(conn)
    pending = [(v, name, fn) for v, name, fn in MIGRATIONS if v not in done]

    if not pending:
        print("Database is up to date.")
        conn.close()
        return 0

    print(f"Migrating {DATABASE}...")
    for version, name, fn in pending:
        print(f"[{version}] {name}")
        fn(conn)
        record_migration(conn, version, name)
        conn.commit()

    conn.close()
    print("Migration complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run_migrations())
