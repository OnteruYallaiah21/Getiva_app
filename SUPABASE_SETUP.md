# Supabase Storage Setup Guide

## Overview

GetIVA Tracking System now uses **Supabase Storage** for file uploads instead of Google Drive. Supabase is free, easy to set up, and doesn't require complex authentication.

## Benefits

✅ **Free**: 1 GB storage included  
✅ **No credit card required**  
✅ **Simple REST API**  
✅ **Works great with Python & FastAPI**  
✅ **Public URLs** for easy file access  

## Step-by-Step Setup

### 1. Create Supabase Project

1. Go to [https://supabase.com](https://supabase.com)
2. Sign up or log in
3. Click **"New Project"**
4. Fill in:
   - **Name**: `getiva-tracking` (or any name)
   - **Database Password**: Choose a strong password (save it!)
   - **Region**: Choose closest to you
5. Click **"Create new project"**
6. Wait 2-3 minutes for project to be created

### 2. Create Storage Bucket

1. In your Supabase project, go to **Storage** (left sidebar)
2. Click **"Create bucket"**
3. Fill in:
   - **Name**: `pdfs` (or any name you prefer)
   - **Public bucket**: ✅ **Enable this** (important for public URLs)
4. Click **"Create bucket"**

### 3. Get Your Credentials

1. Go to **Settings** → **API** (left sidebar)
2. Find these values:
   - **Project URL**: `https://YOUR_PROJECT_ID.supabase.co`
   - **anon public key**: Long string starting with `eyJ...`

### 4. Configure Backend

1. Copy `.env.example` to `.env`:
   ```bash
   cp backend/.env.example backend/.env
   ```

2. Edit `backend/.env` and add your credentials:
   ```env
   SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
   SUPABASE_KEY=your_anon_public_key_here
   SUPABASE_BUCKET=pdfs
   ```

3. Save the file

### 5. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 6. Test the Setup

1. Start your backend server
2. Try uploading a file through the application
3. Check the Supabase Storage dashboard - you should see your file
4. The file should have a public URL that works

## Environment Variables

Create `backend/.env` file with:

```env
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
SUPABASE_BUCKET=pdfs
```

**Important**: 
- Never commit `.env` file to Git (it's in `.gitignore`)
- The `.env` file should be in the `backend/` directory
- On production (Render), set these as environment variables

## Production Deployment (Render)

When deploying to Render, add these environment variables:

1. Go to your Render service settings
2. Navigate to **Environment** tab
3. Add these variables:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_KEY`: Your Supabase anon key
   - `SUPABASE_BUCKET`: Your bucket name (default: `pdfs`)

## File URLs

After upload, files are accessible via:
- **Public URL**: `https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/pdfs/filename.pdf`
- Both **View** and **Download** links use the same public URL
- Files are accessible to anyone with the link (since bucket is public)

## Troubleshooting

**"Supabase service not available" error:**
- Check that `.env` file exists in `backend/` directory
- Verify `SUPABASE_URL` and `SUPABASE_KEY` are set correctly
- Make sure no extra spaces or quotes in `.env` file

**"Failed to upload file" error:**
- Verify bucket name matches `SUPABASE_BUCKET` in `.env`
- Check that bucket is set to **Public** in Supabase dashboard
- Verify your Supabase project is active

**Files not accessible:**
- Ensure bucket is set to **Public** in Supabase Storage settings
- Check file path in Supabase Storage dashboard

---

**Your files are now saved to Supabase Storage with public URLs! 🚀**

