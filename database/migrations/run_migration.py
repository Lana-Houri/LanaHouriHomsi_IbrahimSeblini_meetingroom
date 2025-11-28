"""
Migration script to add is_hidden column to Reviews table.
Run this script to update your database schema.
"""
import os
import sys
import psycopg2

# Database connection parameters
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "meetingroom")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

def run_migration():
    """Add is_hidden column to Reviews table if it doesn't exist."""
    try:
        print(f"Connecting to database at {DB_HOST}...")
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cur = conn.cursor()
        
        # Check if column exists
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'reviews' 
            AND column_name = 'is_hidden'
        """)
        
        if cur.fetchone():
            print("Column 'is_hidden' already exists in Reviews table.")
        else:
            print("Adding 'is_hidden' column to Reviews table...")
            cur.execute("""
                ALTER TABLE Reviews 
                ADD COLUMN is_hidden BOOLEAN DEFAULT FALSE
            """)
            
            # Update existing reviews
            cur.execute("UPDATE Reviews SET is_hidden = FALSE WHERE is_hidden IS NULL")
            
            conn.commit()
            print("[SUCCESS] Successfully added 'is_hidden' column to Reviews table!")
            print("[SUCCESS] Updated existing reviews to have is_hidden = FALSE")
        
        cur.close()
        conn.close()
        print("\nMigration completed successfully!")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"[ERROR] Database connection error: {e}")
        print("\nMake sure:")
        print("  1. PostgreSQL is running")
        print("  2. Database credentials are correct")
        print("  3. Database 'meetingroom' exists")
        return False
    except Exception as e:
        print(f"[ERROR] Error during migration: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Reviews Table Migration: Add is_hidden column")
    print("=" * 60)
    print()
    
    success = run_migration()
    
    if success:
        print("\n" + "=" * 60)
        print("You can now run the profiler without errors!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("Migration failed. Please check the errors above.")
        print("=" * 60)
        sys.exit(1)

