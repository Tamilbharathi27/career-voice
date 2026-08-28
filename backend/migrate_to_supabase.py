"""
Supabase / Cloud Database Migration Script for Career Voice
------------------------------------------------------------
This script migrates all data and schema from local SQLite (career_voice.db)
to your cloud Supabase (PostgreSQL) database.
"""

import sys
import os
import sqlite3
from sqlalchemy import create_engine, text, inspect, Boolean

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.base import Base
from app.core.config import settings

def main():
    target_db_url = settings.DATABASE_URL

    if "sqlite" in target_db_url:
        print("[!] Error: Target DATABASE_URL is set to local SQLite.")
        print("Please set your PostgreSQL DATABASE_URL in backend/.env")
        sys.exit(1)

    if target_db_url.startswith("postgres://"):
        target_db_url = target_db_url.replace("postgres://", "postgresql://", 1)

    print("[*] Connecting to target cloud database...")
    db_engine = create_engine(target_db_url, echo=False)

    dialect_name = db_engine.dialect.name
    print(f"[*] Detected database dialect: {dialect_name}")

    try:
        with db_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"[+] Successfully connected to cloud {dialect_name} database!")
    except Exception as e:
        print(f"[-] Failed to connect to target database: {e}")
        sys.exit(1)

    # Step 1: Create all tables in target database
    print("\n[*] Creating database schema...")
    Base.metadata.create_all(bind=db_engine)
    print("[+] Schema created successfully!")

    # Step 2: Extract data from local SQLite
    sqlite_db_path = os.path.join(os.path.dirname(__file__), "career_voice.db")
    if not os.path.exists(sqlite_db_path):
        print(f"[!] Local SQLite database '{sqlite_db_path}' not found. Schema created successfully!")
        return

    print(f"\n[*] Migrating data from local SQLite database ({sqlite_db_path})...")
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_conn.row_factory = sqlite3.Row
    sqlite_cursor = sqlite_conn.cursor()

    tables = [
        "users",
        "profiles",
        "interview_sessions",
        "questions",
        "answers",
        "answer_evaluations",
        "session_reports"
    ]

    inspector = inspect(db_engine)
    existing_tables = inspector.get_table_names()

    # Identify boolean columns from SQLAlchemy models
    bool_columns_by_table = {}
    for table_name, table_obj in Base.metadata.tables.items():
        bool_cols = set()
        for col in table_obj.columns:
            if isinstance(col.type, Boolean):
                bool_cols.add(col.name)
        bool_columns_by_table[table_name] = bool_cols

    with db_engine.begin() as conn:
        for table in tables:
            if table not in existing_tables:
                print(f"  - Table '{table}' does not exist in target database, skipping.")
                continue

            rows = sqlite_cursor.execute(f"SELECT * FROM {table}").fetchall()
            if not rows:
                print(f"  - {table}: 0 rows (skipped)")
                continue

            q = '"' if dialect_name == "postgresql" else "`"
            
            # Truncate target table
            if dialect_name == "postgresql":
                conn.execute(text(f'TRUNCATE TABLE {q}{table}{q} CASCADE;'))
            else:
                conn.execute(text(f"DELETE FROM {q}{table}{q};"))

            columns = rows[0].keys()
            col_names = ", ".join([f"{q}{c}{q}" for c in columns])
            param_names = ", ".join([f":{c}" for c in columns])

            stmt = text(f"INSERT INTO {q}{table}{q} ({col_names}) VALUES ({param_names});")

            # Convert 0/1 integers to Python booleans for Boolean columns
            target_bool_cols = bool_columns_by_table.get(table, set())
            data = []
            for row in rows:
                row_dict = dict(row)
                for col_name in target_bool_cols:
                    if col_name in row_dict and row_dict[col_name] is not None:
                        row_dict[col_name] = bool(row_dict[col_name])
                data.append(row_dict)

            conn.execute(stmt, data)
            print(f"  - {table}: Successfully migrated {len(data)} rows.")

            # Update PostgreSQL sequence counters
            if dialect_name == "postgresql":
                try:
                    seq_query = text(f"""
                        SELECT setval(pg_get_serial_sequence('{table}', 'id'), coalesce(max(id), 1)) 
                        FROM "{table}";
                    """)
                    conn.execute(seq_query)
                except Exception:
                    pass

    print("\n[+] Migration completed successfully!")
    print(" All tables & data are now live in your Supabase PostgreSQL cloud database!")

if __name__ == "__main__":
    main()
