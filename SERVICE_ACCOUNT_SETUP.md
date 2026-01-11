# Service Account Setup Guide

## Important: OAuth vs Service Account

**You currently have:** OAuth Client Secret (`client_secret_*.json`)
- Used for user authentication flows
- Users must log in and grant permissions
- Not suitable for automated server-side uploads

**You need:** Service Account JSON (`service-account.json`)
- Used for server-to-server authentication
- No user interaction required
- Perfect for automated file uploads

## Step-by-Step: Create Service Account

Since you already have a Google Cloud Project (`getivaproject`), follow these steps:

### 1. Go to Google Cloud Console
- Visit: https://console.cloud.google.com/
- Select your project: **getivaproject**

### 2. Enable Google Drive API (if not already enabled)
- Go to **APIs & Services** → **Library**
- Search for "Google Drive API"
- Click **Enable** (if not already enabled)

### 3. Create Service Account
1. Go to **IAM & Admin** → **Service Accounts**
2. Click **+ CREATE SERVICE ACCOUNT**
3. Fill in details:
   - **Service account name**: `getiva-drive-uploader` (or any name)
   - **Service account ID**: Auto-generated (keep default)
   - **Description**: `Service account for GetIVA file uploads`
4. Click **CREATE AND CONTINUE**

### 4. Grant Permissions
- Skip for now (click **CONTINUE**)
- Click **DONE**

### 5. Create and Download JSON Key
1. Click on the service account you just created
2. Go to **KEYS** tab
3. Click **ADD KEY** → **Create new key**
4. Select **JSON** format
5. Click **CREATE**
6. A JSON file will be downloaded automatically

### 6. Save the JSON File
1. Rename the downloaded file to: `service-account.json`
2. Move it to: `backend/service-account.json`
3. Make sure the file structure looks like:
   ```json
   {
     "type": "service_account",
     "project_id": "getivaproject",
     "private_key_id": "...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
     "client_email": "...@getivaproject.iam.gserviceaccount.com",
     "client_id": "...",
     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
     "token_uri": "https://oauth2.googleapis.com/token",
     ...
   }
   ```

### 7. Grant Drive Access (Optional but Recommended)
- The Service Account will create files in its own Drive
- Files will be accessible via direct links (we make them public in code)
- If you want files in a specific folder, share a Drive folder with the service account email

## Verify Setup

After saving `service-account.json`:

1. Restart your backend server
2. Try uploading a file through the application
3. Check the backend logs - should not see "service-account.json not found" warning

## Security Note

⚠️ **IMPORTANT:** 
- Never commit `service-account.json` to version control (it's in `.gitignore`)
- Keep the JSON file secure
- If compromised, delete the service account and create a new one

---

**Once you have `service-account.json` in the `backend/` folder, Google Drive uploads will work! 🚀**

