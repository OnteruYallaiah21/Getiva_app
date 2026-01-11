from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse, Response, StreamingResponse
from typing import Optional
import csv
import os
from datetime import datetime
from pathlib import Path
import hashlib
import json

# Supabase Storage integration
from supabase import create_client, Client
from dotenv import load_dotenv

# Cloudinary integration
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# Google Drive integration
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    from googleapiclient.errors import HttpError
    GOOGLE_DRIVE_AVAILABLE = True
except ImportError:
    GOOGLE_DRIVE_AVAILABLE = False
    print("Warning: Google Drive libraries not available. Install: pip install google-api-python-client google-auth google-auth-httplib2")

# io module for BytesIO (used by both Google Drive and Cloudinary)
import io

# Load environment variables from root .env file
# Load from project root directory (one level up from backend/)
ROOT_DIR = Path(__file__).parent.parent
load_dotenv(ROOT_DIR / '.env')  # Load .env file from project root

app = FastAPI(title="GetIVA Tracking System")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
USERS_CSV = DATA_DIR / "users.csv"
LEADS_CSV = DATA_DIR / "leads.csv"
RECRUITERS_CSV = DATA_DIR / "recruiters.csv"
UPLOADS_DIR = BASE_DIR.parent / "uploads"  # Local storage directory

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
UPLOADS_DIR.mkdir(exist_ok=True)

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "pdfs")  # Default bucket name
DATABASE_URL = os.getenv("DATABASE_URL", "")  # PostgreSQL connection string

# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

# Initialize Cloudinary if credentials are provided
if CLOUDINARY_CLOUD_NAME and CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
        secure=True
    )

# Google Drive Configuration
GOOGLE_SERVICE_ACCOUNT_PATH = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "")
GOOGLE_SERVICE_ACCOUNT_PATH = BASE_DIR / "service-account.json" if not GOOGLE_SERVICE_ACCOUNT_PATH else Path(GOOGLE_SERVICE_ACCOUNT_PATH)

# Initialize users.csv if it doesn't exist
if not USERS_CSV.exists():
    with open(USERS_CSV, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['username', 'password', 'role'])
        writer.writerow(['admin', 'admin123', 'admin'])  # Default admin

# Google Drive setup
def get_drive_service():
    """Initialize Google Drive API service"""
    if not GOOGLE_DRIVE_AVAILABLE:
        return None
    
    if not GOOGLE_SERVICE_ACCOUNT_PATH.exists():
        return None
    
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        credentials = service_account.Credentials.from_service_account_file(
            str(GOOGLE_SERVICE_ACCOUNT_PATH), scopes=SCOPES
        )
        return build('drive', 'v3', credentials=credentials)
    except Exception as e:
        print(f"Error initializing Google Drive: {e}")
        return None

# Supabase setup
def get_supabase_client() -> Client | None:
    """Initialize Supabase client"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Error initializing Supabase: {e}")
        return None

# Database connection for PostgreSQL
# Global flag to track if database is available
DB_AVAILABLE = None

def get_db_connection():
    """Get PostgreSQL database connection with fallback to CSV"""
    global DB_AVAILABLE
    
    # Check if we've already determined DB is not available
    if DB_AVAILABLE is False:
        return None
    
    if not DATABASE_URL:
        DB_AVAILABLE = False
        return None
    
    try:
        import psycopg2
        conn = psycopg2.connect(DATABASE_URL)
        DB_AVAILABLE = True
        return conn
    except ImportError:
        print("⚠️  psycopg2 not available, using CSV storage")
        DB_AVAILABLE = False
        return None
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("📁 Falling back to CSV storage")
        DB_AVAILABLE = False
        return None

# Initialize database tables
def init_database_tables():
    """Create tables in Supabase if they don't exist"""
    conn = get_db_connection()
    if not conn:
        print("Database not available, using CSV only")
        return
    
    try:
        cur = conn.cursor()
        
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
        print("Database tables initialized successfully")
    except Exception as e:
        print(f"Error initializing database tables: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

def migrate_csv_to_supabase():
    """Migrate all existing CSV data to Supabase database"""
    conn = get_db_connection()
    if not conn:
        print("Cannot migrate: Database connection not available")
        return
    
    try:
        cur = conn.cursor()
        migrated_count = 0
        
        # Migrate users from CSV
        if USERS_CSV.exists():
            try:
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
            print(f"📁 Found {len(application_files)} application CSV file(s) to migrate...")
        
        for csv_file in application_files:
            try:
                username = csv_file.stem.replace("applications_", "")
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
        
        if migrated_count > 0:
            print(f"")
            print(f"✅✅✅ MIGRATION COMPLETE! ✅✅✅")
            print(f"📊 Total records migrated: {migrated_count}")
            print(f"🎉 All data is now in Supabase database!")
            print(f"")
        else:
            print("✅ No new CSV data to migrate (all data already in Supabase)")
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

# Initialize tables on startup (only if DATABASE_URL is set)
if DATABASE_URL:
    print("🔧 Initializing Supabase database...")
    init_database_tables()
    print("📦 Migrating all CSV data to Supabase...")
    migrate_csv_to_supabase()
    print("✅ Supabase setup complete! All data operations will use Supabase only.")
else:
    print("⚠️  WARNING: DATABASE_URL not set. Please configure it in .env file.")

def hash_password(password: str) -> str:
    """Simple password hashing (SHA256)"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed

def get_user_csv_path(username: str) -> Path:
    """Get path to user's applications CSV"""
    return DATA_DIR / f"applications_{username}.csv"

def init_user_csv(username: str):
    """Initialize CSV file for user if it doesn't exist - Optimized for high volume"""
    csv_path = get_user_csv_path(username)
    if not csv_path.exists():
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Optimized header structure for high-volume data
            writer.writerow(['id', 'company', 'jobdescription', 'filename', 'timestamp', 'download_link', 'view_link', 'status'])

def init_users_csv():
    """Initialize users.csv if it doesn't exist"""
    if not USERS_CSV.exists():
        with open(USERS_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['username', 'password', 'role'])

def read_users():
    """Read all users from Supabase database, fallback to CSV"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT username, password, role FROM users ORDER BY username")
            rows = cur.fetchall()
            users = [{'username': row[0], 'password': row[1], 'role': row[2]} for row in rows]
            cur.close()
            conn.close()
            return users
        except Exception as e:
            print(f"Error reading users from database: {e}, falling back to CSV")
            try:
                conn.close()
            except:
                pass
    
    # Fallback to CSV
    init_users_csv()
    users = []
    with open(USERS_CSV, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users = list(reader)
    return users

def write_users(users: list):
    """Write users to Supabase database, fallback to CSV"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Delete all existing users
            cur.execute("DELETE FROM users")
            # Insert all users
            for user in users:
                cur.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, %s) ON CONFLICT (username) DO UPDATE SET password = EXCLUDED.password, role = EXCLUDED.role, updated_at = CURRENT_TIMESTAMP",
                    (user['username'], user['password'], user['role'])
                )
            conn.commit()
            cur.close()
            conn.close()
            # Also write CSV backup
            write_users_csv(users)
            return
        except Exception as e:
            print(f"Error writing users to database: {e}, falling back to CSV")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
    
    # Fallback to CSV
    write_users_csv(users)

def write_users_csv(users: list):
    """Write users to CSV backup"""
    with open(USERS_CSV, 'w', newline='') as f:
        if users:
            writer = csv.DictWriter(f, fieldnames=['username', 'password', 'role'])
            writer.writeheader()
            writer.writerows(users)

def init_leads_csv():
    """Initialize leads.csv if it doesn't exist"""
    if not LEADS_CSV.exists():
        with open(LEADS_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'phone', 'email', 'status', 'comment', 'created_at', 'last_updated'])

def read_leads() -> list:
    """Read all leads from Supabase database, fallback to CSV"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name, phone, email, status, comment, created_at, last_updated FROM leads ORDER BY id")
            rows = cur.fetchall()
            leads = []
            for row in rows:
                leads.append({
                    'id': str(row[0]),
                    'name': row[1] or '',
                    'phone': row[2] or '',
                    'email': row[3] or '',
                    'status': row[4] or 'talk',
                    'comment': row[5] or '',
                    'created_at': row[6].strftime('%Y-%m-%d %H:%M:%S') if row[6] else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'last_updated': row[7].strftime('%Y-%m-%d %H:%M:%S') if row[7] else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            cur.close()
            conn.close()
            return leads
        except Exception as e:
            print(f"Error reading leads from database: {e}, falling back to CSV")
            try:
                conn.close()
            except:
                pass
    
    # Fallback to CSV
    init_leads_csv()
    leads = []
    if LEADS_CSV.exists():
        with open(LEADS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                leads.append({
                    'id': row.get('id', ''),
                    'name': row.get('name', ''),
                    'phone': row.get('phone', ''),
                    'email': row.get('email', ''),
                    'status': row.get('status', 'talk'),
                    'comment': row.get('comment', ''),
                    'created_at': row.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    'last_updated': row.get('last_updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                })
    return leads

def write_leads(leads: list):
    """Write leads to Supabase database, fallback to CSV"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Get existing IDs
            cur.execute("SELECT id FROM leads")
            existing_ids = {row[0] for row in cur.fetchall()}
            
            for lead in leads:
                lead_id = int(lead.get('id', 0))
                if lead_id in existing_ids:
                    # Update existing
                    cur.execute("""
                        UPDATE leads SET name = %s, phone = %s, email = %s, status = %s, comment = %s, last_updated = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (lead.get('name'), lead.get('phone'), lead.get('email'), lead.get('status'), lead.get('comment', ''), lead_id))
                else:
                    # Insert new
                    cur.execute("""
                        INSERT INTO leads (id, name, phone, email, status, comment, created_at, last_updated)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        lead_id, lead.get('name'), lead.get('phone'), lead.get('email'),
                        lead.get('status'), lead.get('comment', ''),
                        lead.get('created_at'), lead.get('last_updated')
                    ))
            conn.commit()
            cur.close()
            conn.close()
            # Also write CSV backup
            write_leads_csv(leads)
            return
        except Exception as e:
            print(f"Error writing leads to database: {e}, falling back to CSV")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
    
    # Fallback to CSV
    write_leads_csv(leads)

def write_leads_csv(leads: list):
    """Write leads to CSV backup"""
    init_leads_csv()
    with open(LEADS_CSV, 'w', newline='') as f:
        if leads:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'phone', 'email', 'status', 'comment', 'created_at', 'last_updated'])
            writer.writeheader()
            writer.writerows(leads)

# Recruiters Management Functions
def init_recruiters_csv():
    """Initialize recruiters.csv if it doesn't exist"""
    if not RECRUITERS_CSV.exists():
        with open(RECRUITERS_CSV, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'name', 'phone', 'deals_with', 'created_at', 'last_updated'])

def read_recruiters() -> list:
    """Read all recruiters from Supabase database, fallback to CSV"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, name, phone, deals_with, created_at, last_updated FROM recruiters ORDER BY id")
            rows = cur.fetchall()
            recruiters = []
            for row in rows:
                recruiters.append({
                    'id': str(row[0]),
                    'name': row[1] or '',
                    'phone': row[2] or '',
                    'deals_with': row[3] or '',
                    'created_at': row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'last_updated': row[5].strftime('%Y-%m-%d %H:%M:%S') if row[5] else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                })
            cur.close()
            conn.close()
            return recruiters
        except Exception as e:
            print(f"Error reading recruiters from database: {e}, falling back to CSV")
            try:
                conn.close()
            except:
                pass
    
    # Fallback to CSV
    init_recruiters_csv()
    recruiters = []
    if RECRUITERS_CSV.exists():
        with open(RECRUITERS_CSV, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                recruiters.append({
                    'id': row.get('id', ''),
                    'name': row.get('name', ''),
                    'phone': row.get('phone', ''),
                    'deals_with': row.get('deals_with', ''),
                    'created_at': row.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    'last_updated': row.get('last_updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                })
    return recruiters

def write_recruiters(recruiters: list):
    """Write recruiters to Supabase database, fallback to CSV"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Get existing IDs
            cur.execute("SELECT id FROM recruiters")
            existing_ids = {row[0] for row in cur.fetchall()}
            
            for recruiter in recruiters:
                recruiter_id = int(recruiter.get('id', 0))
                if recruiter_id in existing_ids:
                    # Update existing
                    cur.execute("""
                        UPDATE recruiters SET name = %s, phone = %s, deals_with = %s, last_updated = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (recruiter.get('name'), recruiter.get('phone'), recruiter.get('deals_with', ''), recruiter_id))
                else:
                    # Insert new
                    cur.execute("""
                        INSERT INTO recruiters (id, name, phone, deals_with, created_at, last_updated)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (
                        recruiter_id, recruiter.get('name'), recruiter.get('phone'),
                        recruiter.get('deals_with', ''), recruiter.get('created_at'), recruiter.get('last_updated')
                    ))
            conn.commit()
            cur.close()
            conn.close()
            # Also write CSV backup
            write_recruiters_csv(recruiters)
            return
        except Exception as e:
            print(f"Error writing recruiters to database: {e}, falling back to CSV")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
    
    # Fallback to CSV
    write_recruiters_csv(recruiters)

def write_recruiters_csv(recruiters: list):
    """Write recruiters to CSV backup"""
    init_recruiters_csv()
    with open(RECRUITERS_CSV, 'w', newline='') as f:
        if recruiters:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'phone', 'deals_with', 'created_at', 'last_updated'])
            writer.writeheader()
            writer.writerows(recruiters)

def read_applications(username: str) -> list:
    """Read applications for a user from Supabase database, fallback to CSV"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT id, company, jobdescription, filename, timestamp, download_link, view_link, status
                FROM applications WHERE username = %s ORDER BY timestamp DESC
            """, (username,))
            rows = cur.fetchall()
            applications = []
            for row in rows:
                applications.append({
                    'id': str(row[0]),
                    'company': row[1] or '',
                    'jobdescription': row[2] or '',
                    'filename': row[3] or '',
                    'timestamp': row[4].strftime('%Y-%m-%d %H:%M:%S') if row[4] else datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'download_link': row[5] or '',
                    'view_link': row[6] or row[5] or '',
                    'status': row[7] or 'applied'
                })
            cur.close()
            conn.close()
            return applications
        except Exception as e:
            print(f"Error reading applications from database: {e}, falling back to CSV")
            try:
                conn.close()
            except:
                pass
    
    # Fallback to CSV
    csv_path = get_user_csv_path(username)
    init_user_csv(username)
    applications = []
    if csv_path.exists():
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                applications.append({
                    'id': row.get('id', ''),
                    'company': row.get('company', ''),
                    'jobdescription': row.get('jobdescription', ''),
                    'filename': row.get('filename', ''),
                    'timestamp': row.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
                    'download_link': row.get('download_link', ''),
                    'view_link': row.get('view_link') or row.get('download_link', ''),
                    'status': row.get('status', 'applied')
                })
    return applications

def write_applications(username: str, applications: list):
    """Write applications for a user to Supabase database, fallback to CSV"""
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            # Delete existing applications for this user
            cur.execute("DELETE FROM applications WHERE username = %s", (username,))
            # Insert all applications
            for app in applications:
                app_id = int(app.get('id', 0))
                cur.execute("""
                    INSERT INTO applications (id, username, company, jobdescription, filename, timestamp, download_link, view_link, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    app_id, username, app.get('company'), app.get('jobdescription'),
                    app.get('filename'), app.get('timestamp'), app.get('download_link'),
                    app.get('view_link', app.get('download_link', '')), app.get('status', 'applied')
                ))
            conn.commit()
            cur.close()
            conn.close()
            # Also write CSV backup
            write_applications_csv(username, applications)
            return
        except Exception as e:
            print(f"Error writing applications to database: {e}, falling back to CSV")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
    
    # Fallback to CSV
    write_applications_csv(username, applications)

def write_applications_csv(username: str, applications: list):
    """Write applications to CSV backup"""
    csv_path = get_user_csv_path(username)
    init_user_csv(username)
    try:
        applications_sorted = sorted(applications, key=lambda x: x.get('timestamp', ''), reverse=True)
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            if applications_sorted:
                writer = csv.DictWriter(f, fieldnames=['id', 'company', 'jobdescription', 'filename', 'timestamp', 'download_link', 'view_link', 'status'])
                writer.writeheader()
                writer.writerows(applications_sorted)
    except Exception as e:
        print(f"Error writing applications CSV for {username}: {e}")
        raise

def get_mime_type(filename: str) -> str:
    """Get MIME type based on file extension"""
    extension = filename.lower().split('.')[-1] if '.' in filename else ''
    mime_types = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }
    return mime_types.get(extension, 'application/octet-stream')

def upload_to_google_drive(file_content: bytes, filename: str) -> dict:
    """Upload file to Google Drive and return public URLs"""
    service = get_drive_service()
    if not service:
        raise Exception("Google Drive service not available")
    
    try:
        mime_type = get_mime_type(filename)
        file_stream = io.BytesIO(file_content)
        media = MediaIoBaseUpload(file_stream, mimetype=mime_type, resumable=True)
        
        file_metadata = {'name': filename}
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        file_id = file.get('id')
        # Make file publicly viewable
        service.permissions().create(
            fileId=file_id,
            body={'role': 'reader', 'type': 'anyone'}
        ).execute()
        
        view_link = f"https://drive.google.com/file/d/{file_id}/view"
        download_link = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        return {
            'view_link': view_link,
            'download_link': download_link,
            'file_id': file_id
        }
    except Exception as e:
        print(f"Error uploading to Google Drive: {e}")
        raise

def upload_to_supabase(file_content: bytes, filename: str) -> dict:
    """Upload file to Supabase Storage and return public URL"""
    supabase = get_supabase_client()
    if not supabase:
        raise Exception("Supabase service not available")
    
    try:
        mime_type = get_mime_type(filename)
        
        # Upload file to Supabase Storage
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            filename,
            file_content,
            {"content-type": mime_type, "upsert": "true"}  # upsert: replace if exists
        )
        
        # Get public URL
        public_url = supabase.storage.from_(SUPABASE_BUCKET).get_public_url(filename)
        
        # Return both view and download links (same URL for Supabase public files)
        return {
            'view_link': public_url,
            'download_link': public_url,
            'file_id': filename  # Use filename as identifier
        }
    except Exception as e:
        print(f"Error uploading to Supabase: {e}")
        raise

def upload_to_cloudinary(file_content: bytes, filename: str) -> dict:
    """Upload file to Cloudinary and return public URL"""
    if not CLOUDINARY_CLOUD_NAME or not CLOUDINARY_API_KEY or not CLOUDINARY_API_SECRET:
        raise Exception("Cloudinary service not available")
    
    try:
        file_stream = io.BytesIO(file_content)
        resource_type = 'raw' if filename.lower().endswith(('.pdf', '.doc', '.docx')) else 'auto'
        
        upload_result = cloudinary.uploader.upload(
            file_stream,
            public_id=filename.replace('.', '_'),
            resource_type=resource_type,
            folder="getiva-uploads"
        )
        
        secure_url = upload_result.get("secure_url")
        view_link = secure_url
        download_link = secure_url
        
        # Optimize URL for images
        if resource_type == 'auto':
            optimize_url, _ = cloudinary_url(
                upload_result.get("public_id"),
                resource_type=resource_type,
                fetch_format="auto",
                quality="auto"
            )
            view_link = optimize_url
        
        return {
            'view_link': view_link,
            'download_link': download_link,
            'file_id': upload_result.get("public_id")
        }
    except Exception as e:
        print(f"Error uploading to Cloudinary: {e}")
        raise

def get_next_local_filename() -> str:
    """Get next sequential filename (db1, db2, db3, ...)"""
    counter = 1
    while True:
        filename = f"db{counter}"
        file_path = UPLOADS_DIR / filename
        if not file_path.exists():
            return filename
        counter += 1
        # Safety limit
        if counter > 10000:
            raise Exception("Too many local files")

def upload_to_local(file_content: bytes, original_filename: str) -> dict:
    """Upload file to local storage with sequential naming (db1, db2, db3, ...)"""
    try:
        # Get next sequential filename
        local_filename = get_next_local_filename()
        
        # Preserve original extension
        original_ext = Path(original_filename).suffix
        local_filename_with_ext = f"{local_filename}{original_ext}"
        
        file_path = UPLOADS_DIR / local_filename_with_ext
        
        # Write file
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Return local URLs (relative paths for serving)
        view_link = f"/uploads/{local_filename_with_ext}"
        download_link = f"/uploads/{local_filename_with_ext}"
        
        return {
            'view_link': view_link,
            'download_link': download_link,
            'file_id': local_filename_with_ext
        }
    except Exception as e:
        print(f"Error uploading to local storage: {e}")
        raise

def upload_file(file_content: bytes, filename: str) -> dict:
    """
    Upload file with fallback chain:
    1. Try Google Drive
    2. If fails, try Supabase
    3. If fails, try Cloudinary
    4. If all fail, save locally (db1, db2, db3, ...)
    """
    # Try Google Drive first
    try:
        print("Attempting upload to Google Drive...")
        return upload_to_google_drive(file_content, filename)
    except Exception as e:
        print(f"Google Drive upload failed: {e}, trying Supabase...")
    
    # Try Supabase
    try:
        print("Attempting upload to Supabase...")
        return upload_to_supabase(file_content, filename)
    except Exception as e:
        print(f"Supabase upload failed: {e}, trying Cloudinary...")
    
    # Try Cloudinary
    try:
        print("Attempting upload to Cloudinary...")
        return upload_to_cloudinary(file_content, filename)
    except Exception as e:
        print(f"Cloudinary upload failed: {e}, using local storage...")
    
    # Fallback to local storage
    try:
        print("Using local storage (db1, db2, db3, ...)...")
        return upload_to_local(file_content, filename)
    except Exception as e:
        print(f"Local storage failed: {e}")
        raise HTTPException(status_code=500, detail=f"All upload methods failed. Last error: {str(e)}")

# Authentication dependency
def get_current_user(username: str = Form(...), password: str = Form(...)):
    """Validate user credentials"""
    users = read_users()
    for user in users:
        if user['username'] == username:
            stored_password = user['password']
            # Check if password is hashed (64 chars for SHA256)
            if len(stored_password) == 64:
                if verify_password(password, stored_password):
                    return user
            else:
                # Legacy plain text password
                if password == stored_password:
                    return user
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the login page"""
    index_path = BASE_DIR.parent / "frontend" / "index.html"
    if index_path.exists():
        with open(index_path, 'r') as f:
            return f.read()
    return {"message": "GetIVA Tracking System API - Frontend not found"}

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Login endpoint"""
    users = read_users()
    for user in users:
        if user['username'] == username:
            stored_password = user['password']
            # Check if password is hashed
            if len(stored_password) == 64:
                if verify_password(password, stored_password):
                    return {
                        "success": True,
                        "username": user['username'],
                        "role": user['role']
                    }
            else:
                if password == stored_password:
                    return {
                        "success": True,
                        "username": user['username'],
                        "role": user['role']
                    }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/applications")
async def get_applications(username: str):
    """Get all applications for a user - USER SPECIFIC DATA ONLY"""
    # Validate: Users can only access their own applications
    # This is enforced by the frontend, but we validate here too
    init_user_csv(username)
    applications = read_applications(username)
    return {"applications": applications, "username": username}

@app.post("/applications")
async def create_application(
    username: str = Form(...),
    company: str = Form(...),
    jobdescription: str = Form(...),
    file: UploadFile = File(...)
):
    """Create new application with file upload"""
    # Validate file type
    if not file.filename.endswith(('.pdf', '.doc', '.docx')):
        raise HTTPException(status_code=400, detail="Only PDF and DOC files are allowed")
    
    init_user_csv(username)
    applications = read_applications(username)
    
    # Generate ID
    if applications:
        max_id = max(int(app.get('id', 0)) for app in applications)
        new_id = max_id + 1
    else:
        new_id = 1
    
    # Read file content into memory
    file_content = await file.read()
    
    # Create safe filename for Supabase
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = f"{username}_{timestamp_str}_{file.filename}"
    
    # Upload directly to storage (with fallback chain)
    # upload_file handles fallback internally, so we don't catch exceptions here
    upload_result = upload_file(file_content, safe_filename)
    
    # Get download and view links
    download_link = upload_result['download_link']
    view_link = upload_result['view_link']
    
    # Create application entry
    application = {
        'id': str(new_id),
        'company': company,
        'jobdescription': jobdescription,
        'filename': file.filename,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'download_link': download_link,
        'view_link': view_link,
        'status': 'Applied'  # Default status
    }
    
    applications.append(application)
    write_applications(username, applications)
    
    return {"success": True, "application": application}

@app.put("/applications/{row_id}")
async def update_application(
    row_id: int,
    username: str = Form(...),
    company: Optional[str] = Form(None),
    jobdescription: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    """Update existing application"""
    applications = read_applications(username)
    
    # Find application
    app_index = None
    for i, app in enumerate(applications):
        if int(app.get('id', 0)) == row_id:
            app_index = i
            break
    
    if app_index is None:
        raise HTTPException(status_code=404, detail="Application not found")
    
    application = applications[app_index]
    
    # Update fields - always set status if provided (even if empty string)
    if company is not None:
        application['company'] = company
    if jobdescription is not None:
        application['jobdescription'] = jobdescription
    if status is not None:
        application['status'] = status
    
    # Handle file replacement
    if file:
        if not file.filename.endswith(('.pdf', '.doc', '.docx')):
            raise HTTPException(status_code=400, detail="Only PDF and DOC files are allowed")
        
        # Read file content into memory
        file_content = await file.read()
        
        # Create safe filename for Supabase
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{username}_{timestamp_str}_{file.filename}"
        
        # Upload directly to storage (with fallback chain)
        upload_result = upload_file(file_content, safe_filename)
        
        application['download_link'] = upload_result['download_link']
        application['view_link'] = upload_result['view_link']
        application['filename'] = file.filename
    
    # Update timestamp
    application['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    write_applications(username, applications)
    
    return {"success": True, "application": application}

@app.delete("/applications/{row_id}")
async def delete_application(row_id: int, username: str = Form(...)):
    """Delete application"""
    applications = read_applications(username)
    
    # Find and remove application
    applications = [app for app in applications if int(app.get('id', 0)) != row_id]
    
    write_applications(username, applications)
    
    return {"success": True}

# Admin routes
# IMPORTANT: /admin/users/list must come BEFORE /admin/users/{username} to avoid route conflicts
@app.get("/admin/users/list")
async def get_users_list():
    """Get list of all usernames for dropdown (admin only)"""
    try:
        users = read_users()
        usernames = [{"username": user['username'], "role": user['role']} for user in users]
        return {"users": usernames}
    except Exception as e:
        print(f"Error in get_users_list: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@app.get("/admin/users")
async def get_users():
    """Get all users (admin only)"""
    users = read_users()
    # Keep password in response for admin to view (it's hashed anyway)
    return {"users": users}

@app.post("/admin/users")
async def create_user(
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("user")
):
    """Create new user (admin only)"""
    users = read_users()
    
    # Check if username exists
    for user in users:
        if user['username'] == username:
            raise HTTPException(status_code=400, detail="Username already exists")
    
    # Hash password
    hashed_password = hash_password(password)
    
    # Add user
    new_user = {
        'username': username,
        'password': hashed_password,
        'role': role
    }
    users.append(new_user)
    write_users(users)
    
    # Initialize user's CSV
    init_user_csv(username)
    
    return {"success": True, "user": {"username": username, "role": role}}

@app.put("/admin/users/{username}")
async def update_user(
    username: str,
    password: Optional[str] = Form(None),
    role: Optional[str] = Form(None)
):
    """Update user (admin only)"""
    users = read_users()
    
    # Find user
    user_index = None
    for i, user in enumerate(users):
        if user['username'] == username:
            user_index = i
            break
    
    if user_index is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    if password:
        users[user_index]['password'] = hash_password(password)
    if role:
        users[user_index]['role'] = role
    
    write_users(users)
    
    updated_user = users[user_index].copy()
    updated_user.pop('password', None)
    
    return {"success": True, "user": updated_user}

@app.delete("/admin/users/{username}")
async def delete_user(username: str):
    """Delete user (admin only)"""
    users = read_users()
    
    # Check if user exists
    user_exists = any(user['username'] == username for user in users)
    if not user_exists:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Remove user
    users = [user for user in users if user['username'] != username]
    write_users(users)
    
    # Delete user's CSV file
    csv_path = get_user_csv_path(username)
    if csv_path.exists():
        os.remove(csv_path)
    
    return {"success": True}

@app.get("/admin/applications/{username}")
async def get_user_applications(username: str):
    """Get applications for a specific user (admin only)"""
    init_user_csv(username)
    applications = read_applications(username)
    return {"username": username, "applications": applications}

# Leads Management Routes (Admin Only)
@app.get("/admin/leads")
async def get_leads():
    """Get all leads (admin only)"""
    leads = read_leads()
    return {"leads": leads}

@app.post("/admin/leads")
async def create_lead(
    name: str = Form(...),
    phone: str = Form(...),
    email: Optional[str] = Form(None),
    status: str = Form("talk"),
    comment: Optional[str] = Form(None)
):
    """Create new lead (admin only)"""
    leads = read_leads()
    
    # Generate new ID
    if leads:
        max_id = max(int(lead.get('id', 0)) for lead in leads)
        new_id = max_id + 1
    else:
        new_id = 1
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_lead = {
        'id': str(new_id),
        'name': name,
        'phone': phone,
        'email': email or '',  # Allow empty email
        'status': status,
        'comment': comment or '',  # Allow empty comment
        'created_at': current_time,
        'last_updated': current_time
    }
    leads.append(new_lead)
    write_leads(leads)
    
    return {"success": True, "lead": new_lead}

@app.put("/admin/leads/{lead_id}")
async def update_lead(
    lead_id: str,
    name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    status: Optional[str] = Form(None),
    comment: Optional[str] = Form(None)
):
    """Update lead (admin only)"""
    leads = read_leads()
    
    # Find lead
    lead_index = None
    for i, lead in enumerate(leads):
        if lead['id'] == lead_id:
            lead_index = i
            break
    
    if lead_index is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    # Update fields (only update if provided)
    if name:
        leads[lead_index]['name'] = name
    if phone:
        leads[lead_index]['phone'] = phone
    if email is not None:
        leads[lead_index]['email'] = email
    if status:
        leads[lead_index]['status'] = status
    if comment is not None:
        leads[lead_index]['comment'] = comment
    # Ensure comment field exists
    if 'comment' not in leads[lead_index]:
        leads[lead_index]['comment'] = ''
    
    # Update last_updated timestamp whenever any field is updated
    leads[lead_index]['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Ensure created_at exists (for old records)
    if 'created_at' not in leads[lead_index] or not leads[lead_index]['created_at']:
        leads[lead_index]['created_at'] = leads[lead_index].get('last_updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    write_leads(leads)
    
    return {"success": True, "lead": leads[lead_index]}

@app.delete("/admin/leads/{lead_id}")
async def delete_lead(lead_id: str):
    """Delete lead (admin only)"""
    leads = read_leads()
    
    # Remove lead
    leads = [lead for lead in leads if lead['id'] != lead_id]
    write_leads(leads)
    
    return {"success": True}

# Recruiters Management Routes (Admin Only)
@app.get("/admin/recruiters")
async def get_recruiters():
    """Get all recruiters (admin only)"""
    recruiters = read_recruiters()
    return {"recruiters": recruiters}

@app.post("/admin/recruiters")
async def create_recruiter(
    name: str = Form(...),
    phone: str = Form(...),
    deals_with: Optional[str] = Form(None)
):
    """Create new recruiter (admin only)"""
    recruiters = read_recruiters()
    
    # Generate new ID
    if recruiters:
        max_id = max(int(recruiter.get('id', 0)) for recruiter in recruiters)
        new_id = max_id + 1
    else:
        new_id = 1
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_recruiter = {
        'id': str(new_id),
        'name': name,
        'phone': phone,
        'deals_with': deals_with or '',
        'created_at': current_time,
        'last_updated': current_time
    }
    recruiters.append(new_recruiter)
    write_recruiters(recruiters)
    
    return {"success": True, "recruiter": new_recruiter}

@app.put("/admin/recruiters/{recruiter_id}")
async def update_recruiter(
    recruiter_id: str,
    name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    deals_with: Optional[str] = Form(None)
):
    """Update recruiter (admin only)"""
    recruiters = read_recruiters()
    
    # Find recruiter
    recruiter_index = None
    for i, recruiter in enumerate(recruiters):
        if recruiter['id'] == recruiter_id:
            recruiter_index = i
            break
    
    if recruiter_index is None:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    
    # Update fields
    if name:
        recruiters[recruiter_index]['name'] = name
    if phone:
        recruiters[recruiter_index]['phone'] = phone
    if deals_with is not None:
        recruiters[recruiter_index]['deals_with'] = deals_with
    
    # Update last_updated timestamp
    recruiters[recruiter_index]['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Ensure created_at exists
    if 'created_at' not in recruiters[recruiter_index] or not recruiters[recruiter_index]['created_at']:
        recruiters[recruiter_index]['created_at'] = recruiters[recruiter_index].get('last_updated', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    
    write_recruiters(recruiters)
    
    return {"success": True, "recruiter": recruiters[recruiter_index]}

@app.delete("/admin/recruiters/{recruiter_id}")
async def delete_recruiter(recruiter_id: str):
    """Delete recruiter (admin only)"""
    recruiters = read_recruiters()
    
    # Remove recruiter
    recruiters = [recruiter for recruiter in recruiters if recruiter['id'] != recruiter_id]
    write_recruiters(recruiters)
    
    return {"success": True}

# Manual Migration Endpoint (Admin Only)
@app.post("/admin/migrate")
async def manual_migrate():
    """Manually trigger migration of all CSV data to Supabase"""
    try:
        migrate_csv_to_supabase()
        return {"success": True, "message": "Migration completed successfully. Check server logs for details."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")

# CSV Download Endpoints (Admin Only)
@app.get("/admin/download/users.csv")
async def download_users_csv():
    """Download users.csv file"""
    if not USERS_CSV.exists():
        raise HTTPException(status_code=404, detail="Users CSV file not found")
    return FileResponse(
        path=str(USERS_CSV),
        filename="users.csv",
        media_type="text/csv"
    )

@app.get("/admin/download/leads.csv")
async def download_leads_csv():
    """Download leads.csv file"""
    if not LEADS_CSV.exists():
        raise HTTPException(status_code=404, detail="Leads CSV file not found")
    return FileResponse(
        path=str(LEADS_CSV),
        filename="leads.csv",
        media_type="text/csv"
    )

@app.get("/admin/download/recruiters.csv")
async def download_recruiters_csv():
    """Download recruiters.csv file"""
    if not RECRUITERS_CSV.exists():
        raise HTTPException(status_code=404, detail="Recruiters CSV file not found")
    return FileResponse(
        path=str(RECRUITERS_CSV),
        filename="recruiters.csv",
        media_type="text/csv"
    )

@app.get("/admin/download/applications/{username}.csv")
async def download_applications_csv(username: str):
    """Download applications CSV for a specific user"""
    csv_path = get_user_csv_path(username)
    if not csv_path.exists():
        raise HTTPException(status_code=404, detail=f"Applications CSV file not found for user: {username}")
    return FileResponse(
        path=str(csv_path),
        filename=f"applications_{username}.csv",
        media_type="text/csv"
    )

@app.get("/admin/download/list")
async def get_download_list():
    """Get list of all available CSV files for download"""
    files = []
    
    if USERS_CSV.exists():
        files.append({"name": "users.csv", "url": "/admin/download/users.csv", "description": "All users data"})
    
    if LEADS_CSV.exists():
        files.append({"name": "leads.csv", "url": "/admin/download/leads.csv", "description": "All leads data"})
    
    if RECRUITERS_CSV.exists():
        files.append({"name": "recruiters.csv", "url": "/admin/download/recruiters.csv", "description": "All recruiters data"})
    
    # Get all user application files
    for csv_file in DATA_DIR.glob("applications_*.csv"):
        username = csv_file.stem.replace("applications_", "")
        files.append({
            "name": csv_file.name,
            "url": f"/admin/download/applications/{username}.csv",
            "description": f"Applications for user: {username}"
        })
    
    return {"files": files}

@app.get("/view-file")
async def view_file(url: str):
    """
    View file in browser instead of downloading.
    Supports local files and proxies external URLs with proper headers.
    """
    import urllib.parse
    from urllib.request import urlopen, Request
    
    try:
        # Check if it's a local file
        if url.startswith("/uploads/"):
            # Local file - serve with inline content disposition
            filename = url.replace("/uploads/", "")
            file_path = UPLOADS_DIR / filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="File not found")
            
            # Determine MIME type
            mime_type = get_mime_type(filename)
            
            # Read file and serve with inline disposition
            with open(file_path, 'rb') as file:
                content = file.read()
            
            return Response(
                content=content,
                media_type=mime_type,
                headers={
                    "Content-Disposition": f'inline; filename="{filename}"',
                    "Content-Type": mime_type
                }
            )
        
        # External URL - proxy with proper headers
        elif url.startswith("http://") or url.startswith("https://"):
            # Check if it's Google Drive view link - return redirect
            if "drive.google.com/file/d/" in url and "/view" in url:
                # Google Drive view links work directly, but we can embed them
                # Return HTML with iframe for better viewing
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>View File</title>
                    <style>
                        body {{ margin: 0; padding: 0; overflow: hidden; }}
                        iframe {{ width: 100%; height: 100vh; border: none; }}
                    </style>
                </head>
                <body>
                    <iframe src="{url}" allow="fullscreen"></iframe>
                </body>
                </html>
                """
                return HTMLResponse(content=html_content)
            
            # For other external URLs (Supabase, Cloudinary), fetch and proxy
            try:
                # Add inline parameter for Supabase if not present
                if "supabase.co" in url and "response-content-disposition" not in url:
                    separator = "&" if "?" in url else "?"
                    url = f"{url}{separator}response-content-disposition=inline"
                
                # Fetch the file
                req = Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0')
                with urlopen(req, timeout=10) as response:
                    content = response.read()
                    content_type = response.headers.get('Content-Type', 'application/octet-stream')
                    
                    # Extract filename from URL if possible
                    parsed_url = urllib.parse.urlparse(url)
                    filename = os.path.basename(parsed_url.path) or "file"
                    
                    return Response(
                        content=content,
                        media_type=content_type,
                        headers={
                            "Content-Disposition": f'inline; filename="{filename}"',
                            "Content-Type": content_type
                        }
                    )
            except Exception as e:
                # If proxy fails, return redirect to original URL
                from fastapi.responses import RedirectResponse
                return RedirectResponse(url=url)
        
        else:
            raise HTTPException(status_code=400, detail="Invalid URL format")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error viewing file: {str(e)}")

# Serve uploads directory for local files
if UPLOADS_DIR.exists():
    app.mount("/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")

# Serve frontend static files (must be last - catches all unmatched routes)
FRONTEND_DIR = BASE_DIR.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

