import sys
from app.db.session import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    res = db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public';"))
    print("Tables in database:")
    tables = [row[0] for row in res]
    print(tables)
    
    # Check if we can query users
    if "users" in tables:
        user_count = db.execute(text("SELECT count(*) FROM users;")).scalar()
        print(f"Users count: {user_count}")
    else:
        print("Users table does not exist!")
except Exception as e:
    print("Error:", e)
finally:
    db.close()
