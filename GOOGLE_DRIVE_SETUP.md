# Google Drive Integration Setup Guide

## Understanding the Difference

**OAuth Client Secret** (what you have):
- Used for user authorization (users log in with their Google account)
- Requires user interaction
- Better for client-side applications

**Service Account** (what we need):
- Used for server-to-server authentication
- No user interaction needed
- Perfect for automated file uploads from your backend

## ✅ Option 1: Create a Service Account (Recommended)

Since you already have a Google Cloud project (`getivaproject`), follow these steps:

### Step 1: Go to Google Cloud Console
1. Visit: https://console.cloud.google.com/
2. Select your project: **getivaproject**

### Step 2: Enable Google Drive API
1. Go to "APIs & Services" → "Library"
2. Search for "Google Drive API"
3. Click "Enable"

### Step 3: Create Service Account
1. Go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Fill in details:
   - **Service account name:** `getiva-drive-uploader`
   - **Description:** `Service account for GetIVA file uploads`
4. Click "Create and Continue"
5. **Skip role assignment** (not needed for Drive API)
6. Click "Done"

### Step 4: Create and Download Key
1. Click on the service account you just created
2. Go to "Keys" tab
3. Click "Add Key" → "Create new key"
4. Choose **JSON** format
5. Click "Create"
6. The JSON file will download automatically

### Step 5: Place the File
1. Rename the downloaded file to: `service-account.json`
2. Place it in: `backend/service-account.json`
3. **Important:** Add `backend/service-account.json` to `.gitignore` (already done)

### Step 6: Grant Drive Access (Optional)
By default, files uploaded by the service account will be in the service account's own Drive.
If you want files in a specific Google Drive folder:

1. Create a folder in Google Drive (or use existing)
2. Share the folder with the service account email
   - The email looks like: `getiva-drive-uploader@getivaproject.iam.gserviceaccount.com`
3. Give it "Editor" permission

## ✅ Option 2: Use OAuth (More Complex - Not Recommended)

If you prefer to use OAuth client secret instead, you'd need to:
1. Implement OAuth flow (redirects, tokens)
2. Store refresh tokens
3. Handle token expiration
4. Requires user interaction for first authorization

**For server-side uploads, Service Account is simpler and recommended.**

## Testing the Setup

Once you have `service-account.json` in place:

1. Start your backend:
   ```bash
   cd backend
   python main.py
   ```

2. Try uploading a file through your application

3. Check the logs - you should see no errors related to Google Drive

4. The file should appear in Google Drive (in the service account's Drive or shared folder)

## File Format Support

The system supports:
- **PDF files** (.pdf)
- **Word Documents** (.doc, .docx)

Files are automatically:
- Uploaded to Google Drive
- Made publicly accessible (via download link)
- Download link stored in your CSV

## Troubleshooting

### "service-account.json not found"
- Make sure the file is in `backend/service-account.json`
- Check file name (must be exactly `service-account.json`)

### "Permission denied" errors
- Make sure Google Drive API is enabled
- Check that the service account key is valid
- Verify the JSON file structure

### Files not appearing in Drive
- Check service account's own Drive (not your personal Drive)
- Or share a folder with the service account email

### Upload fails silently
- Check backend logs for error messages
- System falls back to local storage if Drive fails
- Files will be stored in `uploads/` folder

## Security Notes

- **Never commit** `service-account.json` to Git (already in `.gitignore`)
- The service account has limited permissions (only Drive API)
- Files are made public for download (consider adding authentication if needed)
- For production, consider using environment variables for sensitive data

---

**Ready to upload files to Google Drive! 🚀**

