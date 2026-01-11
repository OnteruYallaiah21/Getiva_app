# Google Drive Integration - File Upload & Links

## Overview

The GetIVA Tracking System uploads files to Google Drive and stores both **View** and **Download** links for each file.

## How It Works

### 1. File Upload Process

When a user uploads a file (PDF, DOC, or DOCX):

1. File is temporarily saved locally
2. Uploaded to Google Drive using Service Account
3. File is made publicly accessible
4. Both View and Download links are generated
5. Links are saved to the user's CSV file

### 2. Link Types

**View Link:**
- Format: `https://drive.google.com/file/d/{FILE_ID}/view`
- Opens file in Google Drive viewer (browser)
- Best for previewing files

**Download Link:**
- Format: `https://drive.google.com/uc?export=download&id={FILE_ID}`
- Directly downloads the file
- Best for saving files locally

### 3. CSV Storage

Each application entry in `applications_{username}.csv` contains:

```csv
id,company,jobdescription,filename,timestamp,download_link,view_link
1,Company A,Software Engineer,resume.pdf,2026-01-11 14:23,https://drive.google.com/uc?export=download&id=FILE_ID,https://drive.google.com/file/d/FILE_ID/view
```

### 4. Frontend Display

- Both View and Download buttons appear in the applications table
- Users can click "View" to preview in browser
- Users can click "Download" to save the file
- If Drive upload fails, local file path is used as fallback

## Setup Requirements

### Service Account Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project (e.g., `getivaproject`)
3. Enable **Google Drive API** (should already be enabled)
4. Create Service Account:
   - Go to "IAM & Admin" → "Service Accounts"
   - Create new service account
   - Download JSON key
5. Save as `backend/service-account.json`

### File Permissions

Files uploaded to Drive are automatically set to:
- **Public read access** (anyone with the link can view/download)
- This allows direct links to work without authentication

## Fallback Behavior

If Google Drive upload fails:
- Files are stored locally in `uploads/` folder
- Download link uses local path: `/uploads/{filename}`
- View link uses the same local path
- System continues to work without Drive

## Testing

1. Upload a file through the application
2. Check the applications table - you should see View and Download links
3. Click "View" to open in Google Drive viewer
4. Click "Download" to download the file
5. Check `backend/data/applications_{username}.csv` to see stored links

## Troubleshooting

**Files not uploading to Drive:**
- Check `service-account.json` exists in `backend/` folder
- Verify Google Drive API is enabled
- Check backend logs for error messages
- System will fall back to local storage

**Links not working:**
- Verify file permissions in Google Drive
- Check that Service Account has proper access
- Ensure files are set to public read

**CSV missing view_link column:**
- Existing CSV files will be updated on next file upload
- Old entries may not have view_link (download_link still works)
- New entries will have both links

---

**Your files are now saved to Google Drive with both View and Download links! 🚀**

