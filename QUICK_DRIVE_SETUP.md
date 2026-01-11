# 🚀 Quick Setup: Google Drive File Upload

Your application is **ready** to upload files to Google Drive and save download/view links!

## ⚠️ Important: OAuth Client Secret vs Service Account

You have: `client_secret_*.json` (OAuth Client Secret)  
You need: `service-account.json` (Service Account JSON)

**Why?**
- **OAuth Client Secret** = For user login/authorization (interactive)
- **Service Account** = For automated server uploads (what we need)

**You CANNOT use the OAuth client secret for server-side uploads.**

## ✅ Quick Setup Steps (5 minutes)

### 1. Go to Google Cloud Console
- Visit: https://console.cloud.google.com/
- Project: **getivaproject**

### 2. Create Service Account
1. **IAM & Admin** → **Service Accounts**
2. Click **"Create Service Account"**
3. Name: `getiva-drive-uploader`
4. Click **"Create and Continue"**
5. **Skip role assignment** → Click **"Done"**

### 3. Download JSON Key
1. Click on the service account you created
2. Go to **"Keys"** tab
3. Click **"Add Key"** → **"Create new key"**
4. Choose **JSON**
5. Click **"Create"** (file downloads automatically)

### 4. Place the File
1. **Rename** downloaded file to: `service-account.json`
2. **Move** to: `backend/service-account.json`
3. Verify path: `/Users/yonteru/Documents/Getiva_Tracking_System/backend/service-account.json`

### 5. Test Upload
1. Restart backend: `cd backend && python3 main.py`
2. Login to application
3. Upload a file
4. Check CSV - you'll see Google Drive links!

## 📊 What Happens After Setup

**Before (without service-account.json):**
```csv
id,company,filename,download_link,view_link
1,Company,resume.pdf,/uploads/file.pdf,/uploads/file.pdf
```

**After (with service-account.json):**
```csv
id,company,filename,download_link,view_link
1,Company,resume.pdf,https://drive.google.com/uc?export=download&id=FILE_ID,https://drive.google.com/file/d/FILE_ID/view
```

## 🎯 Current Status

✅ **Code is ready** - Upload function implemented  
✅ **Google Drive API enabled** - You have this  
✅ **Links generated** - View & Download links  
❌ **Service Account JSON missing** - Need to create this  

## 📝 Checklist

- [ ] Service Account created in Google Cloud
- [ ] JSON key downloaded
- [ ] File renamed to `service-account.json`
- [ ] File placed in `backend/` folder
- [ ] Backend restarted
- [ ] Test upload works

---

**Once you add `backend/service-account.json`, files will automatically upload to Google Drive with view and download links! 🎉**

