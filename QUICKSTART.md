# GetIVA Tracking System - Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Set Up Google Drive (Optional)
If you want to use Google Drive for file storage:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project and enable Google Drive API
3. Create a Service Account and download the JSON key
4. Rename it to `service-account.json` and place it in the `backend/` folder

**Note:** If you skip this step, files will be stored locally in the `uploads/` folder instead.

### Step 3: Start the Backend
```bash
cd backend
python main.py
```
The backend will run on `http://localhost:8000`

### Step 4: Open the Frontend
1. Open `frontend/index.html` in your web browser
2. Or use a simple HTTP server:
   ```bash
   cd frontend
   python -m http.server 8080
   ```
   Then visit `http://localhost:8080`

### Step 5: Login
- **Default Admin:**
  - Username: `admin`
  - Password: `admin123`

⚠️ **Important:** Change the admin password after first login!

---

## 📋 What You Get

✅ **User Portal:**
- View all your job applications
- Add new applications with file upload
- Edit existing applications
- Delete applications

✅ **Admin Portal:**
- Create/edit/delete users
- View any user's applications
- Manage user roles (user/admin)

✅ **Features:**
- Per-user CSV tracking (each user has their own file)
- Google Drive integration for file storage
- Beautiful orange-themed UI matching GetIVA branding
- Secure password hashing
- File upload validation (PDF/DOC only)

---

## 🔧 Troubleshooting

**"Error connecting to server"**
- Make sure the backend is running on port 8000
- Check the browser console for errors
- Verify API_BASE in HTML files matches `http://localhost:8000`

**Google Drive not working**
- Verify `service-account.json` is in `backend/` folder
- Files will fall back to local storage if Drive fails
- Check that Google Drive API is enabled in your project

**Can't find files**
- Make sure `backend/data/` directory exists
- Check file permissions (should be writable)

---

## 📁 Project Structure

```
GetIVA_Tracking_System/
├── frontend/              # HTML/CSS/JS files
│   ├── index.html        # Login page
│   ├── user.html         # User portal
│   ├── admin.html        # Admin portal
│   └── style.css         # Orange-themed styles
├── backend/              # FastAPI backend
│   ├── main.py          # Main application
│   ├── requirements.txt  # Python dependencies
│   ├── data/            # CSV files stored here
│   └── service-account.json  # Google Drive credentials (you add this)
├── uploads/             # Temporary file storage
└── README.md            # Full documentation
```

---

## 🎨 Customization

### Change API URL
If your backend runs on a different URL, update `API_BASE` in:
- `frontend/index.html`
- `frontend/user.html`
- `frontend/admin.html`

Look for: `const API_BASE = 'http://localhost:8000';`

### Change Port
Edit `backend/main.py` and change:
```python
uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## 📚 Need More Help?

See `README.md` for detailed documentation including:
- Full API endpoint documentation
- Deployment instructions
- Security best practices
- CSV structure details

---

**Ready to track your applications! 🎉**

