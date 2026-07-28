"""Postgres connection + LangGraph checkpointer setup."""

import os

import psycopg
from psycopg.rows import dict_row
from langgraph.checkpoint.postgres import PostgresSaver
from dotenv import load_dotenv
import streamlit as st
load_dotenv()
DATABASE_URL = st.secrets["DATABASE_URL"]

print("connecting")
_conn = psycopg.connect(
    DATABASE_URL,
    autocommit=True,
    row_factory=dict_row
)

checkpointer = PostgresSaver(_conn)
checkpointer.setup()

# ── Trip history (reuses the same _conn already created above) ──────────────


def setup_history_table():
    print(">>> RUNNING setup_history_table")

    with _conn.cursor() as cur:

        cur.execute("""
            CREATE TABLE IF NOT EXISTS trip_history (
                id SERIAL PRIMARY KEY,
                user_email TEXT NOT NULL,
                thread_id TEXT NOT NULL,
                user_query TEXT NOT NULL,
                final_result TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT NOW()
            );
        """)

        print(">>> CREATE TABLE DONE")

        cur.execute("""
            ALTER TABLE trip_history
            ADD COLUMN IF NOT EXISTS status TEXT NOT NULL DEFAULT 'done';
        """)

        print(">>> STATUS MIGRATION DONE")

        cur.execute("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'trip_history'
            ORDER BY ordinal_position;
        """)

        print(">>> ACTUAL COLUMNS:", cur.fetchall())

        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_trip_history_email
            ON trip_history(user_email);
        """)

        cur.execute("""
            DELETE FROM trip_history a
            USING trip_history b
            WHERE a.thread_id = b.thread_id
              AND a.id < b.id;
        """)

        cur.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_trip_history_thread_id
            ON trip_history(thread_id);
        """)

    print(">>> setup_history_table FINISHED")


def create_trip(user_email: str, thread_id: str, user_query: str):
    """
    Insert a trip row the MOMENT the user hits Generate, before the pipeline
    has produced anything. Call this, then st.rerun() — the sidebar (which
    renders earlier in app.py's script) will pick up the new thread on that
    very next rerun, showing it as "pending" while the plan is built.
    """
    with _conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO trip_history (user_email, thread_id, user_query, final_result, status)
            VALUES (%s, %s, %s, '', 'pending')
            ON CONFLICT (thread_id) DO NOTHING
            """,
            (user_email, thread_id, user_query),
        )


def update_trip_result(thread_id: str, final_result: str):
    """Fill in the result once the pipeline finishes, updating the same row/thread_id."""
    with _conn.cursor() as cur:
        cur.execute(
            """
            UPDATE trip_history
            SET final_result = %s, status = 'done'
            WHERE thread_id = %s
            """,
            (final_result, thread_id),
        )


def save_trip(user_email: str, thread_id: str, user_query: str, final_result: str):
    """Back-compat one-shot save (create + fill immediately). The current
    app.py flow uses create_trip() + update_trip_result() instead so the
    thread shows up before generation finishes, but this is kept in case
    anything else still calls save_trip() directly."""
    create_trip(user_email, thread_id, user_query)
    update_trip_result(thread_id, final_result)


def get_trip_history(user_email: str, limit: int = 20):
    if not user_email:
        print("HISTORY ERROR: user_email is empty")
        return []

    print(f"Fetching history for: {user_email}")

    with _conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                id,
                thread_id,
                user_query,
                final_result,
                status,
                created_at
            FROM trip_history
            WHERE user_email = %s
            ORDER BY created_at DESC
            LIMIT %s
            """,
            (user_email, limit),
        )

        rows = cur.fetchall()

        print(f"HISTORY ROWS FOUND: {len(rows)}")
        print(rows)

        return rows


# Run once at import time, same pattern as checkpointer.setup() above.
setup_history_table()
