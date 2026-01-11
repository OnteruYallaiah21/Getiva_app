from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
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

def read_users():
    """Read all users from users.csv"""
    users = []
    if USERS_CSV.exists():
        with open(USERS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            users = list(reader)
    return users

def write_users(users: list):
    """Write users to users.csv"""
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
    """Read all leads from leads.csv"""
    init_leads_csv()
    leads = []
    if LEADS_CSV.exists():
        with open(LEADS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for lead in reader:
                # Migrate old records: if timestamp exists but created_at/last_updated don't, use timestamp
                if 'timestamp' in lead and lead.get('timestamp'):
                    if 'created_at' not in lead or not lead.get('created_at'):
                        lead['created_at'] = lead['timestamp']
                    if 'last_updated' not in lead or not lead.get('last_updated'):
                        lead['last_updated'] = lead['timestamp']
                # Ensure both fields exist
                if 'created_at' not in lead or not lead.get('created_at'):
                    lead['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if 'last_updated' not in lead or not lead.get('last_updated'):
                    lead['last_updated'] = lead.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                # Ensure comment field exists (for old records)
                if 'comment' not in lead:
                    lead['comment'] = ''
                leads.append(lead)
    return leads

def write_leads(leads: list):
    """Write leads to leads.csv"""
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
    """Read all recruiters from recruiters.csv"""
    init_recruiters_csv()
    recruiters = []
    if RECRUITERS_CSV.exists():
        with open(RECRUITERS_CSV, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for recruiter in reader:
                # Ensure both fields exist
                if 'created_at' not in recruiter or not recruiter.get('created_at'):
                    recruiter['created_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if 'last_updated' not in recruiter or not recruiter.get('last_updated'):
                    recruiter['last_updated'] = recruiter.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                # Ensure deals_with exists
                if 'deals_with' not in recruiter:
                    recruiter['deals_with'] = ''
                recruiters.append(recruiter)
    return recruiters

def write_recruiters(recruiters: list):
    """Write recruiters to recruiters.csv"""
    init_recruiters_csv()
    with open(RECRUITERS_CSV, 'w', newline='') as f:
        if recruiters:
            writer = csv.DictWriter(f, fieldnames=['id', 'name', 'phone', 'deals_with', 'created_at', 'last_updated'])
            writer.writeheader()
            writer.writerows(recruiters)

def read_applications(username: str) -> list:
    """Read applications for a user"""
    csv_path = get_user_csv_path(username)
    applications = []
    if csv_path.exists():
        with open(csv_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Ensure all required fields exist with defaults for old CSV files
                if 'status' not in row or not row['status']:
                    row['status'] = 'Applied'
                if 'view_link' not in row:
                    row['view_link'] = row.get('download_link', '')
                applications.append(row)
    return applications

def write_applications(username: str, applications: list):
    """Write applications for a user - Optimized for high volume"""
    csv_path = get_user_csv_path(username)
    init_user_csv(username)
    try:
        # Sort by timestamp (newest first) before writing
        applications_sorted = sorted(applications, key=lambda x: x.get('timestamp', ''), reverse=True)
        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            if applications_sorted:
                writer = csv.DictWriter(f, fieldnames=['id', 'company', 'jobdescription', 'filename', 'timestamp', 'download_link', 'view_link', 'status'])
                writer.writeheader()
                writer.writerows(applications_sorted)
    except Exception as e:
        print(f"Error writing applications for {username}: {e}")
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

