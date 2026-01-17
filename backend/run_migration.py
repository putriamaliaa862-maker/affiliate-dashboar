import sys
import os
from sqlalchemy import text

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import engine

def run_migration():
    migration_file = os.path.join(os.path.dirname(__file__), "migrations", "001_ads_center_tables.sql")
    print(f"Reading migration file: {migration_file}")
    
    with open(migration_file, "r") as f:
        sql_commands = f.read()

    with engine.connect() as connection:
        trans = connection.begin()
        try:
            print("Executing SQL...")
            # Split by semicolon to handle multiple statements for SQLite
            statements = [s.strip() for s in sql_commands.split(';') if s.strip()]
            
            for statement in statements:
                print(f"Executing statement: {statement[:50]}...")
                connection.execute(text(statement))
                
            trans.commit()
            print("Migration executed successfully!")
        except Exception as e:
            trans.rollback()
            print(f"Error executing migration: {e}")
            raise e

if __name__ == "__main__":
    run_migration()
