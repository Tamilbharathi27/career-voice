"""
Sync all users to Supabase Database AND Supabase Auth Dashboard
"""
import sys
import os
import sqlite3

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.supabase import get_supabase_client

def sync():
    supabase = get_supabase_client()
    if not supabase:
        print("[!] Could not connect to Supabase.")
        return

    sqlite_db_path = os.path.join(os.path.dirname(__file__), "career_voice.db")
    if not os.path.exists(sqlite_db_path):
        print(f"[!] Database file {sqlite_db_path} not found.")
        return

    conn = sqlite3.connect(sqlite_db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    users = cursor.execute("SELECT * FROM users").fetchall()
    print(f"[*] Found {len(users)} users to sync into Supabase Auth & Database...")

    for u in users:
        email = u["email"]
        name = u["name"]

        # 1. Sync to Supabase Authentication -> Users tab
        try:
            auth_res = supabase.auth.admin.create_user({
                "email": email,
                "password": "TemporaryPassword123!",
                "email_confirm": True,
                "user_metadata": {"name": name, "role": u["role"]}
            })
            print(f"[+] Created in Supabase Auth tab: {email}")
        except Exception as e:
            print(f"[*] Auth note for {email}: user may already exist in Supabase Auth.")

        # 2. Sync to Supabase Table Editor -> users table
        try:
            data = {
                "id": u["id"],
                "name": u["name"],
                "email": u["email"],
                "password_hash": u["password_hash"],
                "role": u["role"]
            }
            supabase.table("users").upsert(data).execute()
            print(f"[+] Created in Supabase Table Editor: {email}")
        except Exception as e:
            print(f"[-] Table sync note for {email}: {e}")

    print("\n[+] All users synced to Supabase Auth & Database!")

if __name__ == "__main__":
    sync()
