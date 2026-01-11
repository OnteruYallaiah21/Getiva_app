# Quick Setup: Upload Files to Google Drive ✅

Since you have **Google Drive API enabled** and a Google Cloud project (`getivaproject`), here's how to get file uploads working **NOW**:

## ⚠️ Important: OAuth vs Service Account

You have an **OAuth Client Secret** file, but for **server-side automated uploads**, you need a **Service Account JSON** file.

**Difference:**
- **OAuth Client Secret** (what you have): For user login/authorization
- **Service Account** (what you need): For automated server uploads

## ✅ Step-by-Step: Create Service Account (5 minutes)

### Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Select project: **getivaproject** (your project)

### Step 2: Create Service Account
1. Navigate to: **IAM & Admin** → **Service Accounts**
2. Click: **"Create Service Account"**
3. Fill in:
   - **Service account name:** `getiva-drive-uploader`
   - **Description:** `Service account for GetIVA file uploads to Google Drive`
4. Click: **"Create and Continue"**
5. **Skip role assignment** (click "Continue" or "Done")

### Step 3: Create and Download JSON Key
1. Click on the service account you just created
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Select **JSON** format
5. Click **"Create"**
6. **JSON file downloads automatically**

### Step 4: Place the File
1. **Rename** the downloaded file to: `service-account.json`
2. **Move** it to: `backend/service-account.json`
3. Make sure the path is: `/Users/yonteru/Documents/Getiva_Tracking_System/backend/service-account.json`

### Step 5: Verify File Upload Works
1. Restart your backend server:
   ```bash
   # Stop current server (Ctrl+C)
   cd backend
   python3 main.py
   ```

2. Upload a file through the application
3. Check the CSV file - you should see Google Drive links!

## 📁 File Structure After Setup

```
backend/
├── main.py
├── service-account.json    ← ADD THIS FILE (Service Account JSON)
├── service-account.json.example
└── data/
    └── applications_user1.csv  ← Will contain Google Drive links
```

## 🔍 What the Code Does

1. **User uploads file** → File saved temporarily
2. **Upload to Google Drive** → Using Service Account credentials
3. **Make file public** → Anyone with link can view/download
4. **Generate links:**
   - **View link:** `https://drive.google.com/file/d/{FILE_ID}/view`
   - **Download link:** `https://drive.google.com/uc?export=download&id={FILE_ID}`
5. **Save to CSV** → Both links stored in `applications_{username}.csv`

## ✅ Expected CSV Format

After successful upload, your CSV will look like:

```csv
id,company,jobdescription,filename,timestamp,download_link,view_link
1,Company Name,Job Title,resume.pdf,2026-01-11 15:30,https://drive.google.com/uc?export=download&id=FILE_ID,https://drive.google.com/file/d/FILE_ID/view
```

## 🚀 Test It

1. **Login** to your application
2. **Add new application** with a PDF/DOC file
3. **Check the table** - you should see "View" and "Download" buttons
4. **Click "View"** - file opens in Google Drive viewer
5. **Click "Download"** - file downloads directly

## ❌ If Service Account File Missing

If `service-account.json` is NOT in `backend/` folder:
- Files will be stored **locally** in `uploads/` folder
- Links will use local paths: `/uploads/{filename}`
- System still works, but files aren't in Google Drive

## 📝 Quick Checklist

- [ ] Google Drive API enabled (✅ you have this)
- [ ] Service Account created (need to do this)
- [ ] JSON key downloaded (need to do this)
- [ ] File placed in `backend/service-account.json` (need to do this)
- [ ] Backend server restarted (after adding file)

---

**Once you add `service-account.json`, files will automatically upload to Google Drive! 🎉**

The code is already ready - you just need the Service Account credentials file.

