# Render Environment Variables Setup Guide

## ⚠️ Important: Render Uses Environment Variables (Not File Uploads)

Render doesn't upload secret files directly. Instead, you configure **Environment Variables** in the Render dashboard.

## Required Environment Variables for GetIVA Tracking System

Based on your application, you need to set these environment variables in Render:

### 1. Supabase Storage (Primary/Secondary File Storage)

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key
SUPABASE_BUCKET=pdfs
```

**Where to find:**
- Go to your Supabase project dashboard
- Settings → API
- Copy the Project URL and anon/public key

### 2. Cloudinary (Tertiary File Storage - Fallback)

```
CLOUDINARY_CLOUD_NAME=dhfecdcyb
CLOUDINARY_API_KEY=261597366946186
CLOUDINARY_API_SECRET=x_W6ii2ACw-1l4fUuKb9U7qVsS0
```

**Where to find:**
- Go to Cloudinary Dashboard
- Settings → Security
- Copy Cloud Name, API Key, and API Secret

### 3. Database URL (If using PostgreSQL)

```
DATABASE_URL=postgresql://postgres:password@host:5432/postgres
```

**Where to find:**
- Supabase Dashboard → Settings → Database
- Copy the Connection String

### 4. Google Drive (Optional - For Google Drive uploads)

For Google Drive, you have **TWO options**:

#### Option A: Use Environment Variable (Recommended)
Set the service account JSON content as an environment variable:

```
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account","project_id":"...","private_key":"...","client_email":"..."}
```

⚠️ **Note:** This is a single-line JSON string (no line breaks)

#### Option B: Upload service-account.json file via Render Shell
1. Go to Render Dashboard → Your Service → Shell
2. Run: `cd backend && nano service-account.json`
3. Paste your service account JSON content
4. Save and exit (Ctrl+X, then Y, then Enter)

### 5. Google OAuth (Optional - For Google Drive integration)

```
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_PROJECT_ID=your-project-id
GOOGLE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
GOOGLE_TOKEN_URI=https://oauth2.googleapis.com/token
GOOGLE_AUTH_PROVIDER_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
```

## 📋 Step-by-Step: Add Environment Variables in Render

### Step 1: Go to Render Dashboard
1. Login to https://render.com
2. Go to your service (or create a new one)
3. Click on your service name

### Step 2: Navigate to Environment Tab
1. Click on **"Environment"** in the left sidebar
2. You'll see the environment variables section

### Step 3: Add Each Variable
For each variable above:
1. Click **"Add Environment Variable"**
2. Enter the **Key** (e.g., `SUPABASE_URL`)
3. Enter the **Value** (e.g., `https://your-project.supabase.co`)
4. Click **"Save Changes"**

### Step 4: Repeat for All Variables
Add all the variables listed above that you want to use.

### Step 5: Redeploy
1. After adding all variables, go to **"Manual Deploy"**
2. Click **"Deploy latest commit"**
3. Wait for deployment to complete

## 🔐 Security Best Practices

### ✅ DO:
- ✅ Use environment variables for all secrets
- ✅ Keep your `.env` file local (never commit to Git)
- ✅ Use different credentials for production
- ✅ Rotate keys periodically

### ❌ DON'T:
- ❌ Don't commit `.env` file to Git
- ❌ Don't share environment variables publicly
- ❌ Don't use production keys in development

## 📝 Quick Reference: Minimum Required Variables

For basic functionality (without Google Drive):

```
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
SUPABASE_BUCKET=pdfs
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

## 🔄 Your Current .env File (For Reference)

Your local `.env` file contains the actual values. **Don't upload this file to Render**, but use it as a reference to copy the values into Render's environment variables.

## 📖 Where to Find Your Secrets

### From Your Local .env File:
1. Open `.env` file on your computer
2. Copy each value
3. Paste into Render's environment variables

### If You Don't Have .env:
1. Check your service dashboards (Supabase, Cloudinary, Google Cloud)
2. Or create new credentials if needed

## 🚀 After Setting Up Environment Variables

1. **Deploy your service:**
   - Render will automatically use the environment variables
   - No code changes needed

2. **Test the deployment:**
   - Visit your Render URL
   - Try uploading a file
   - Check that files are stored correctly

3. **Monitor logs:**
   - Go to Render Dashboard → Logs
   - Check for any errors related to missing environment variables

---

## ❓ Need Help?

- **Missing variable error:** Check that you've added all required variables
- **Authentication errors:** Verify your API keys are correct
- **Upload failures:** Check that storage services (Supabase/Cloudinary) are configured correctly

