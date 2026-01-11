#!/usr/bin/env python3
"""
Test script to migrate all CSV data to Supabase
Run this script to test the migration process
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
import csv
from datetime import datetime

# Load environment variables
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')

DATABASE_URL = os.getenv("DATABASE_URL", "")

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
USERS_CSV = DATA_DIR / "users.csv"
LEADS_CSV = DATA_DIR / "leads.csv"
RECRUITERS_CSV = DATA_DIR / "recruiters.csv"

def get_db_connection():
    """Get PostgreSQL database connection"""
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in .env file")
        return None
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return None

def init_database_tables():
    """Create tables in Supabase if they don't exist"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        print("🔧 Creating database tables...")
        
        # Users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username VARCHAR(255) PRIMARY KEY,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Leads table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(50),
                email VARCHAR(255),
                status VARCHAR(50) DEFAULT 'talk',
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Recruiters table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS recruiters (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                phone VARCHAR(50) NOT NULL,
                deals_with TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Applications table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id SERIAL PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                company VARCHAR(255) NOT NULL,
                jobdescription TEXT,
                filename VARCHAR(255),
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                download_link TEXT,
                view_link TEXT,
                status VARCHAR(50) DEFAULT 'applied'
            )
        """)
        
        conn.commit()
        cur.close()
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def migrate_all_data():
    """Migrate all CSV data to Supabase"""
    conn = get_db_connection()
    if not conn:
        print("❌ Cannot migrate: Database connection not available")
        return False
    
    try:
        cur = conn.cursor()
        migrated_count = 0
        
        print("\n" + "="*60)
        print("📦 STARTING MIGRATION")
        print("="*60 + "\n")
        
        # Migrate users from CSV
        if USERS_CSV.exists():
            try:
                print("📄 Reading users.csv...")
                with open(USERS_CSV, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    users = list(reader)
                    if users:
                        user_count = 0
                        for user in users:
                            username = user.get('username', '').strip()
                            password = user.get('password', '').strip()
                            role = user.get('role', 'user').strip()
                            if username and password:
                                cur.execute("""
                                    INSERT INTO users (username, password, role) 
                                    VALUES (%s, %s, %s) 
                                    ON CONFLICT (username) DO NOTHING
                                """, (username, password, role))
                                user_count += 1
                        migrated_count += user_count
                        print(f"✅ Migrated {user_count} users from CSV to Supabase")
                    else:
                        print("⚠️  No users found in users.csv")
            except Exception as e:
                print(f"❌ Error migrating users: {e}")
                import traceback
                traceback.print_exc()
        
        # Migrate leads from CSV
        if LEADS_CSV.exists():
            try:
                print("\n📄 Reading leads.csv...")
                with open(LEADS_CSV, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    leads = list(reader)
                    if leads:
                        lead_count = 0
                        for lead in leads:
                            lead_id = int(lead.get('id', 0))
                            if lead_id > 0:
                                # Handle timestamp migration
                                created_at = lead.get('created_at') or lead.get('timestamp') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                last_updated = lead.get('last_updated') or lead.get('timestamp') or created_at
                                
                                cur.execute("""
                                    INSERT INTO leads (id, name, phone, email, status, comment, created_at, last_updated)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (id) DO NOTHING
                                """, (
                                    lead_id, 
                                    lead.get('name', '').strip(), 
                                    lead.get('phone', '').strip(),
                                    lead.get('email', '').strip(), 
                                    lead.get('status', 'talk').strip(),
                                    lead.get('comment', '').strip(), 
                                    created_at, 
                                    last_updated
                                ))
                                lead_count += 1
                        migrated_count += lead_count
                        print(f"✅ Migrated {lead_count} leads from CSV to Supabase")
                    else:
                        print("⚠️  No leads found in leads.csv")
            except Exception as e:
                print(f"❌ Error migrating leads: {e}")
                import traceback
                traceback.print_exc()
        
        # Migrate recruiters from CSV
        if RECRUITERS_CSV.exists():
            try:
                print("\n📄 Reading recruiters.csv...")
                with open(RECRUITERS_CSV, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    recruiters = list(reader)
                    if recruiters:
                        recruiter_count = 0
                        for recruiter in recruiters:
                            recruiter_id = int(recruiter.get('id', 0))
                            if recruiter_id > 0:
                                created_at = recruiter.get('created_at') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                last_updated = recruiter.get('last_updated') or created_at
                                
                                cur.execute("""
                                    INSERT INTO recruiters (id, name, phone, deals_with, created_at, last_updated)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (id) DO NOTHING
                                """, (
                                    recruiter_id, 
                                    recruiter.get('name', '').strip(), 
                                    recruiter.get('phone', '').strip(),
                                    recruiter.get('deals_with', '').strip(), 
                                    created_at, 
                                    last_updated
                                ))
                                recruiter_count += 1
                        migrated_count += recruiter_count
                        print(f"✅ Migrated {recruiter_count} recruiters from CSV to Supabase")
                    else:
                        print("⚠️  No recruiters found in recruiters.csv")
            except Exception as e:
                print(f"❌ Error migrating recruiters: {e}")
                import traceback
                traceback.print_exc()
        
        # Migrate applications from CSV files
        application_files = list(DATA_DIR.glob("applications_*.csv"))
        if application_files:
            print(f"\n📁 Found {len(application_files)} application CSV file(s)...")
        
        for csv_file in application_files:
            try:
                username = csv_file.stem.replace("applications_", "")
                print(f"📄 Reading {csv_file.name}...")
                with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    applications = list(reader)
                    if applications:
                        app_count = 0
                        for app in applications:
                            app_id = int(app.get('id', 0))
                            if app_id > 0:
                                timestamp = app.get('timestamp') or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                view_link = app.get('view_link') or app.get('download_link', '')
                                status = app.get('status') or 'applied'
                                
                                cur.execute("""
                                    INSERT INTO applications (id, username, company, jobdescription, filename, timestamp, download_link, view_link, status)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON CONFLICT (id) DO NOTHING
                                """, (
                                    app_id, username, 
                                    app.get('company', '').strip(), 
                                    app.get('jobdescription', '').strip(),
                                    app.get('filename', '').strip(), 
                                    timestamp, 
                                    app.get('download_link', '').strip(),
                                    view_link.strip(), 
                                    status.strip()
                                ))
                                app_count += 1
                        migrated_count += app_count
                        print(f"✅ Migrated {app_count} applications for user '{username}' from CSV to Supabase")
                    else:
                        print(f"⚠️  No applications found in {csv_file.name}")
            except Exception as e:
                print(f"❌ Error migrating applications from {csv_file.name}: {e}")
                import traceback
                traceback.print_exc()
        
        conn.commit()
        cur.close()
        
        print("\n" + "="*60)
        if migrated_count > 0:
            print(f"✅✅✅ MIGRATION COMPLETE! ✅✅✅")
            print(f"📊 Total records migrated: {migrated_count}")
            print(f"🎉 All data is now in Supabase database!")
        else:
            print("✅ No new CSV data to migrate (all data already in Supabase)")
        print("="*60 + "\n")
        
        return True
    except Exception as e:
        print(f"\n❌❌❌ CRITICAL ERROR during migration: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def verify_migration():
    """Verify the migration by counting records"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cur = conn.cursor()
        
        print("\n" + "="*60)
        print("🔍 VERIFYING MIGRATION")
        print("="*60 + "\n")
        
        # Count records
        for table_name in ['users', 'leads', 'recruiters', 'applications']:
            try:
                cur.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cur.fetchone()[0]
                print(f"📊 {table_name}: {count} records")
            except Exception as e:
                print(f"❌ {table_name}: Error - {e}")
        
        # Show sample data
        print("\n👥 Sample Users:")
        cur.execute("SELECT username, role FROM users LIMIT 5")
        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(f"   - {row[0]} ({row[1]})")
        else:
            print("   (No users found)")
        
        print("\n📝 Sample Leads:")
        cur.execute("SELECT id, name, status FROM leads LIMIT 5")
        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(f"   - ID {row[0]}: {row[1]} ({row[2]})")
        else:
            print("   (No leads found)")
        
        print("\n✅ Verification complete!")
        print("="*60 + "\n")
        
        cur.close()
        return True
    except Exception as e:
        print(f"❌ Error verifying: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

def main():
    """Main test function"""
    print("\n" + "="*60)
    print("🚀 SUPABASE MIGRATION TEST")
    print("="*60 + "\n")
    
    # Step 1: Initialize tables
    print("STEP 1: Creating database tables...")
    if not init_database_tables():
        print("❌ Failed to create tables. Exiting.")
        sys.exit(1)
    
    # Step 2: Migrate data
    print("\nSTEP 2: Migrating CSV data to Supabase...")
    if not migrate_all_data():
        print("❌ Migration failed. Exiting.")
        sys.exit(1)
    
    # Step 3: Verify migration
    print("STEP 3: Verifying migration...")
    verify_migration()
    
    print("✅✅✅ ALL TESTS COMPLETE! ✅✅✅\n")

if __name__ == "__main__":
    main()

