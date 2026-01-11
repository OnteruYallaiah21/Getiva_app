# Environment Files Guide

## Overview

GetIVA Tracking System uses separate `.env` files for different services and configuration to keep sensitive information organized and secure.

## Environment File Structure

```
backend/
├── .env                    # Main configuration file (master)
├── .env.supabase          # Supabase-specific configuration
├── .env.google            # Google Drive configuration (optional)
├── .env.firebase          # Firebase configuration (optional)
└── .env.links             # Application links & sensitive info
```

## Loading Priority

Environment files are loaded in this order (later files override earlier ones):
1. `.env.links` - Application URLs and sensitive info
2. `.env.supabase` - Supabase configuration
3. `.env.google` - Google Drive configuration
4. `.env.firebase` - Firebase configuration
5. `.env` - Main configuration file (lowest priority)

## Setup Instructions

### 1. Copy Example Files

```bash
cd backend
cp .env.example .env
cp .env.supabase.example .env.supabase
cp .env.google.example .env.google
cp .env.firebase.example .env.firebase
cp .env.links.example .env.links
```

### 2. Configure Each File

#### `.env.links` - Application Links & Sensitive Info
Contains:
- Application URLs (development/production)
- Database connection strings
- Secret keys and tokens
- API keys
- Email configuration
- Application settings

**Required for:** All environments

#### `.env.supabase` - Supabase Configuration
Contains:
- `SUPABASE_URL` - Your Supabase project URL
- `SUPABASE_KEY` - Your Supabase anon key
- `SUPABASE_BUCKET` - Storage bucket name

**Required for:** File uploads (currently in use)

#### `.env.google` - Google Drive Configuration
Contains:
- `GOOGLE_SERVICE_ACCOUNT_PATH` - Path to service account JSON
- `GOOGLE_DRIVE_FOLDER_ID` - Optional folder ID

**Required for:** If using Google Drive (currently not in use)

#### `.env.firebase` - Firebase Configuration
Contains:
- `FIREBASE_PROJECT_ID` - Firebase project ID
- `FIREBASE_CREDENTIALS_PATH` - Path to Firebase credentials
- `FIREBASE_STORAGE_BUCKET` - Firebase storage bucket

**Required for:** If using Firebase (optional)

#### `.env` - Main Configuration File
Contains:
- Master configuration
- Can override values from other files
- Use as fallback or for general settings

**Required for:** All environments

## Recommended Setup

### For Development:
```bash
# Create all environment files
cp .env.example .env
cp .env.supabase.example .env.supabase
cp .env.links.example .env.links

# Edit and fill in your values
nano .env.supabase  # Add Supabase credentials
nano .env.links     # Add application URLs and settings
```

### For Production (Render/Deploy):
Set environment variables in your hosting platform:
- Go to your service settings
- Navigate to Environment tab
- Add all variables from `.env.supabase` and `.env.links`

## Security Notes

⚠️ **IMPORTANT:**
- Never commit `.env` files to Git (they're in `.gitignore`)
- Only commit `.env.example` files as templates
- Keep all `.env` files secure and private
- Use different credentials for development and production
- Rotate keys periodically

## File Purpose Summary

| File | Purpose | Required | Contains |
|------|---------|----------|----------|
| `.env.links` | Application URLs, secrets, API keys | ✅ Yes | URLs, keys, tokens, settings |
| `.env.supabase` | Supabase storage configuration | ✅ Yes (if using Supabase) | Supabase credentials |
| `.env.google` | Google Drive configuration | ❌ Optional | Google service account path |
| `.env.firebase` | Firebase configuration | ❌ Optional | Firebase credentials |
| `.env` | Main/master configuration | ✅ Yes | General settings, fallback values |

## Example Setup

### Minimal Setup (Current - Using Supabase)
```bash
# Required files
.env.supabase  # Supabase credentials
.env.links     # Application URLs and settings
```

### Full Setup (Multiple Services)
```bash
# All files
.env           # Master config
.env.supabase  # Supabase (active)
.env.google    # Google Drive (optional)
.env.firebase  # Firebase (optional)
.env.links     # URLs and sensitive info
```

---

**Your environment is now organized and secure! 🔒**

