import sqlite3
import psycopg2
from config import SUPABASE_URL

SQLITE_DB = "curve_data.db"

def migrate():
    print("Starting migration from SQLite to Supabase...")
    
    # Connect to both
    try:
        sqlite_conn = sqlite3.connect(SQLITE_DB)
        pg_conn = psycopg2.connect(SUPABASE_URL)
        
        sqlite_cur = sqlite_conn.cursor()
        pg_cur = pg_conn.cursor()
        
        tables = [
            "pool_balances", "gauge_weights", "fee_velocity", 
            "lending_markets", "bribe_efficiency", "arbi_opportunities"
        ]
        
        for table in tables:
            print(f"  Migrating {table}...")
            # Get columns
            sqlite_cur.execute(f"PRAGMA table_info({table})")
            cols = [col[1] for col in sqlite_cur.fetchall()]
            col_names = ", ".join(cols)
            placeholders = ", ".join(["%s"] * len(cols))
            
            # Fetch all rows
            sqlite_cur.execute(f"SELECT {col_names} FROM {table}")
            rows = sqlite_cur.fetchall()
            
            if rows:
                insert_query = f"INSERT INTO {table} ({col_names}) VALUES ({placeholders})"
                pg_cur.executemany(insert_query, rows)
                print(f"    Done: {len(rows)} rows.")
            else:
                print(f"    Table {table} is empty.")
                
        pg_conn.commit()
        print("Migration COMPLETED successfully.")
        
    except Exception as e:
        print(f"Migration FAILED: {e}")
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == "__main__":
    migrate()
