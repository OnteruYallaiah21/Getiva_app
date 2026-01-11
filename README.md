# GetIVA Tracking System

A comprehensive job application tracking system built with FastAPI backend and vanilla HTML/CSS/JavaScript frontend. Features per-user CSV tracking, Google Drive integration for file storage, and a beautiful orange-themed interface.

## Features

- ✅ **Per-user CSV tracking** - Each user has their own `applications_{username}.csv` file
- ✅ **File Upload to Google Drive** - Upload PDF/DOC files and get download links
- ✅ **Orange-themed UI** - Beautiful GetIVA branded interface
- ✅ **Mobile-Responsive Design** - Fully optimized for mobile devices and tablets
- ✅ **User Portal** - View, add, edit, and delete applications
- ✅ **Admin Portal** - Create, edit, delete users; view any user's applications
- ✅ **Secure Authentication** - Password hashing with SHA256
- ✅ **FastAPI Backend** - RESTful API with CORS support
- ✅ **Render-Ready** - Optimized for deployment on Render.com
- ✅ **Auto-Detecting API URLs** - Works seamlessly in development and production

## Project Structure

```
GetIVA_Tracking_System/
├── frontend/
│   ├── index.html          # Login page
│   ├── user.html           # User portal
│   ├── admin.html          # Admin portal
│   └── style.css           # Orange-themed styles
├── backend/
│   ├── main.py             # FastAPI application
│   ├── service-account.json # Google Drive credentials (you need to add this)
│   └── data/
│       ├── users.csv       # User credentials
│       └── applications_*.csv  # Per-user application files
├── uploads/                # Temporary file storage
└── requirements.txt        # Python dependencies
```

## Setup Instructions

### 1. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

Or using a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Google Drive API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the **Google Drive API**
4. Create a **Service Account**:
   - Go to "IAM & Admin" > "Service Accounts"
   - Click "Create Service Account"
   - Give it a name (e.g., "getiva-drive")
   - Click "Create and Continue"
   - Skip role assignment, click "Done"
5. Create and download credentials:
   - Click on the service account you just created
   - Go to "Keys" tab
   - Click "Add Key" > "Create new key"
   - Choose JSON format
   - Download the JSON file
6. Rename the downloaded file to `service-account.json`
7. Place it in the `backend/` directory

**Note:** If you skip Google Drive setup, the system will still work but files will be stored locally in the `uploads/` folder instead.

### 3. Default Admin Credentials

The system comes with a default admin account:
- **Username:** `admin`
- **Password:** `admin123`

**⚠️ Important:** Change the admin password after first login for security!

### 4. Run the Backend

```bash
cd backend
python main.py
```

Or using uvicorn directly:

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 5. Open the Frontend

1. Open `frontend/index.html` in a web browser
2. Or serve it using a simple HTTP server:

```bash
cd frontend
python -m http.server 8080
```

Then open `http://localhost:8080` in your browser.

**Note:** If you're getting CORS errors, make sure the backend is running and the API_BASE URL in the HTML files matches your backend URL (default: `http://localhost:8000`).

## Usage

### User Portal

1. Login with your user credentials
2. View all your applications in a table
3. Add new applications:
   - Enter company name
   - Enter job description
   - Upload a PDF or DOC file
   - Click "Add Application"
4. Edit applications:
   - Click "Edit" on any row
   - Update company, job description, or replace the file
   - Click "Update"
5. Delete applications:
   - Click "Delete" on any row
   - Confirm deletion

### Admin Portal

1. Login with admin credentials
2. View all users
3. Add new users:
   - Enter username, password, and role (user/admin)
   - Click "Add User"
4. Edit users:
   - Click "Edit" on any user
   - Update password (optional) and role
   - Click "Update"
5. View user applications:
   - Click "View Applications" to see all applications for that user
6. Delete users:
   - Click "Delete" on any user
   - Confirm deletion (this will also delete all their applications)

## API Endpoints

### Authentication
- `POST /login` - Login with username and password

### Applications
- `GET /applications?username={username}` - Get all applications for a user
- `POST /applications` - Create new application (with file upload)
- `PUT /applications/{row_id}` - Update application
- `DELETE /applications/{row_id}` - Delete application

### Admin
- `GET /admin/users` - Get all users
- `POST /admin/users` - Create new user
- `PUT /admin/users/{username}` - Update user
- `DELETE /admin/users/{username}` - Delete user
- `GET /admin/applications/{username}` - Get applications for a specific user

## CSV Structure

### users.csv
```csv
username,password,role
admin,8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918,admin
```

Passwords are hashed using SHA256.

### applications_{username}.csv
```csv
id,company,jobdescription,filename,timestamp,download_link
1,Company A,Software Engineer,resume.pdf,2026-01-10 14:23,https://drive.google.com/uc?export=download&id=FILE_ID
```

## Deployment

### Local Development
- Backend: Run `python main.py` from the backend directory
- Frontend: Open HTML files directly or use a simple HTTP server

### Production Deployment

**Option 1: Render (Recommended - Free Tier)**

Render provides a free tier that's perfect for this application.

1. **Push to GitHub:**
   - Create a GitHub repository
   - Push your code to GitHub

2. **Deploy on Render:**
   - Go to [render.com](https://render.com) and sign up/login
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Configure the service:
     - **Name:** getiva-tracking-system (or your choice)
     - **Environment:** Python 3
     - **Build Command:** `cd backend && pip install -r requirements.txt`
     - **Start Command:** `cd backend && python main.py`
     - **Plan:** Free
   - Click "Create Web Service"
   - Render will automatically detect the `render.yaml` file if present, or use the manual settings above

3. **Important Notes for Render:**
   - The app will be available at `https://your-app-name.onrender.com`
   - The backend serves both API and frontend files
   - API automatically detects the Render URL (no configuration needed)
   - Data files are stored on Render's ephemeral disk (persist between deployments but can be cleared)
   - For persistent storage, consider using Render Disk (paid) or external storage (S3, Google Drive)

4. **Environment Variables (Optional):**
   - If you want to use Google Drive, add your `service-account.json` file to the `backend/` directory
   - You can also set environment variables in Render dashboard if needed

5. **First Login:**
   - Visit your Render URL
   - Login with default admin credentials:
     - Username: `admin`
     - Password: `admin123`
   - **⚠️ Change the admin password immediately!**

**Option 2: Replit/Glitch**
- Upload all files to Replit or Glitch
- Install dependencies: `cd backend && pip install -r requirements.txt`
- Run: `cd backend && python main.py`
- The API_BASE is automatically detected (no configuration needed)

**Option 3: Traditional VPS**
- Install Python 3.8+
- Install dependencies
- Use a process manager like systemd or supervisor
- The backend serves frontend files, so no separate web server needed
- Configure reverse proxy (nginx) if needed for SSL/HTTPS

## Security Notes

- Passwords are hashed using SHA256 (better than plain text, but consider bcrypt for production)
- Google Drive files are set to "public read" for download links
- CORS is currently set to allow all origins (restrict in production)
- CSV files are stored on the server filesystem
- Consider adding rate limiting and HTTPS in production

## Troubleshooting

### "Error connecting to server"
- Make sure the backend is running on port 8000
- Check that API_BASE in HTML files matches your backend URL
- Check browser console for CORS errors

### Google Drive upload fails
- Verify `service-account.json` is in the `backend/` directory
- Check that Google Drive API is enabled in your Google Cloud project
- Files will fall back to local storage if Drive fails

### CSV file issues
- Ensure the `backend/data/` directory exists and is writable
- Check file permissions

## License

This project is provided as-is for the GetIVA tracking system.

## Support

For issues or questions, please check the code comments or contact the development team.

# Getiva_app
