import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from decouple import config

# Connect to PostgreSQL server using environment variables
try:
    conn = psycopg2.connect(
        dbname='postgres',  # Connect to default postgres DB first
        user=config('DB_USER', default='postgres'),
        password=config('DB_PASSWORD', default='1230'),
        host=config('DB_HOST', default='localhost'),
        port=config('DB_PORT', default='5432')
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Get the target database name from environment
    target_db = config('DB_NAME', default='misoft_db')
    
    # Check if database exists (using parameterized query for security)
    cursor.execute("SELECT 1 FROM pg_database WHERE datname=%s", (target_db,))
    exists = cursor.fetchone()
    
    if not exists:
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(target_db)
        ))
        print(f"✅ Database '{target_db}' created successfully!")
    else:
        print(f"ℹ️  Database '{target_db}' already exists.")
    
    cursor.close()
    conn.close()
    
except psycopg2.Error as e:
    print(f"❌ Error: {e}")
    print("\n⚠️  Please ensure PostgreSQL is running and credentials are correct.")
