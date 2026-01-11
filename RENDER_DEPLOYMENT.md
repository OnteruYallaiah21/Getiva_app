# Render Deployment Guide - GetIVA Tracking System

## Quick Deploy to Render (5 minutes)

### Step 1: Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/GetIVA_Tracking_System.git
git push -u origin main
```

### Step 2: Deploy on Render

1. **Sign up/Login to Render:**
   - Go to https://render.com
   - Sign up with GitHub (recommended for easy repo connection)

2. **Create Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository: `GetIVA_Tracking_System`

3. **Configure Service:**
   - **Name:** `getiva-tracking-system` (or your choice)
   - **Environment:** `Python 3`
   - **Region:** Choose closest to you
   - **Branch:** `main` (or your default branch)
   - **Root Directory:** Leave empty (root)
   - **Build Command:** `cd backend && pip install -r requirements.txt`
   - **Start Command:** `cd backend && python main.py`
   - **Plan:** `Free` (or upgrade if needed)

4. **Environment Variables (Optional):**
   - No environment variables required for basic setup
   - If using Google Drive, you'll need to add `service-account.json` file
   - To set PORT manually (not needed, auto-detected):
     - Key: `PORT`
     - Value: `8000`

5. **Create Service:**
   - Click "Create Web Service"
   - Render will start building and deploying

### Step 3: Access Your Application

1. **Wait for Deployment:**
   - Build takes 2-3 minutes
   - First deployment may take longer
   - Watch the logs for any errors

2. **Get Your URL:**
   - Once deployed, you'll see: `https://your-app-name.onrender.com`
   - The app is accessible at this URL

3. **First Login:**
   - Default admin credentials:
     - **Username:** `admin`
     - **Password:** `admin123`
   - ⚠️ **Change password immediately after first login!**

### Step 4: Update Google Drive (Optional)

If you want to use Google Drive for file storage:

1. **Get Service Account JSON:**
   - Follow instructions in `README.md` (Google Drive Setup section)
   - Download `service-account.json` file

2. **Add to Render:**
   - Option A: Upload via Render Shell
     - Go to your service → "Shell"
     - Run: `nano backend/service-account.json`
     - Paste JSON content
     - Save and exit
   
   - Option B: Add via Git (not recommended for security)
     - Add file to `backend/` directory
     - Push to GitHub
     - Render will redeploy

3. **Restart Service:**
   - Go to "Manual Deploy" → "Deploy latest commit"
   - Or push a new commit to trigger redeploy

## Render-Specific Notes

### Free Tier Limitations
- **Sleep after inactivity:** Free tier services sleep after 15 minutes of inactivity
- **First request after sleep:** Takes 30-60 seconds to wake up
- **Disk storage:** Ephemeral (cleared on redeploy for free tier)
- **Bandwidth:** 100 GB/month (usually sufficient)

### Persistent Storage Options

**Option 1: Render Disk (Paid)**
- Add persistent disk in Render dashboard
- Mount to `/opt/render/project/src/backend/data`
- Data persists across deployments

**Option 2: External Storage**
- Use Google Drive (already implemented)
- Use AWS S3
- Use other cloud storage

**Option 3: Database (Future Upgrade)**
- Migrate from CSV to PostgreSQL (Render provides free PostgreSQL)
- More robust for production

### Troubleshooting

**Service won't start:**
- Check build logs for errors
- Verify Python version (3.8+)
- Check that all dependencies installed correctly

**404 errors:**
- Verify frontend files are in `frontend/` directory
- Check that static file serving is working
- Review backend logs

**API errors:**
- Check that PORT environment variable is set (auto-set by Render)
- Verify CORS settings
- Check browser console for errors

**File upload issues:**
- Verify `uploads/` directory exists and is writable
- Check disk space (free tier has limits)
- Review file size limits

**Sleep/Wake Issues:**
- Free tier services sleep after inactivity
- First request takes time to wake up
- Consider upgrading to paid plan for always-on service

## Monitoring

- **Logs:** View real-time logs in Render dashboard
- **Metrics:** Monitor CPU, memory, and response times
- **Alerts:** Set up email alerts for service issues (paid plans)

## SSL/HTTPS

- Render automatically provides SSL certificates
- HTTPS is enabled by default
- No configuration needed

## Custom Domain

1. Go to service settings
2. Click "Add Custom Domain"
3. Follow DNS configuration instructions
4. SSL certificate auto-provisioned

## Updating Your App

1. Make changes locally
2. Commit and push to GitHub
3. Render automatically detects changes
4. Triggers new deployment
5. Service updates automatically (zero downtime)

## Backup Strategy

For production use, consider:
- Regular backups of CSV files
- Use Google Drive for file storage (already implemented)
- Consider migrating to database (PostgreSQL) for better backup options

---

**Your app is now live! 🎉**

Visit your Render URL and start tracking job applications!

