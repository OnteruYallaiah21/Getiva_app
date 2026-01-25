# Configuration Guide - Azure Blob Storage & Supabase

## ✅ Current Configuration

### Azure Blob Storage
- **Storage Account Name**: `getivablob`
- **Container Name**: `getivastudentfiles`
- **Account Key**: `your_azure_account_key_here`

### Supabase PostgreSQL
- **Database URL**: `postgresql://postgres:YOUR_PASSWORD@db.your-project.supabase.co:5432/postgres`
- **Host**: `db.arsvmvrviffsdrzrlhbx.supabase.co`
- **Port**: `5432`
- **Database**: `postgres`
- **Username**: `postgres`
- **Password**: `Yallaiah@123` (URL-encoded: `Yallaiah%40123`)

## 📝 Update Your .env File

Add or update these variables in your `.env` file:

```env
# Azure Blob Storage Configuration
AZURE_STORAGE_ACCOUNT_NAME=getivablob
AZURE_STORAGE_ACCOUNT_KEY=your_azure_account_key_here
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=getivablob;AccountKey=your_azure_account_key_here;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER_NAME=getivastudentfiles

# Supabase PostgreSQL Database
DATABASE_URL=postgresql://postgres:Yallaiah%40123@db.arsvmvrviffsdrzrlhbx.supabase.co:5432/postgres?sslmode=require
SUPABASE_URL=https://arsvmvrviffsdrzrlhbx.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

## 🔐 Security Notes

⚠️ **Important**: 
- Never commit the `.env` file to Git
- Keep account keys secure
- The `.env` file should be in `.gitignore`

## 📦 File Structure in Azure Blob Storage

Files will be organized as:
```
getivastudentfiles/
├── {username1}/
│   ├── resumes/
│   │   ├── resume_company1_20240111.pdf
│   │   └── resume_company2_20240112.docx
│   └── job_descriptions/
│       ├── jd_company1_20240111.pdf
│       └── jd_company2_20240112.txt
├── {username2}/
│   ├── resumes/
│   └── job_descriptions/
└── ...
```

## 🚀 Next Steps

1. Update your `.env` file with the above configuration
2. Run the Supabase schema: `supabase_schema.sql` in your Supabase SQL Editor
3. Install Azure Blob Storage SDK: `pip install azure-storage-blob`
4. Test the connection by uploading a test file

## 📚 Additional Resources

- See `AZURE_BLOB_STORAGE.md` for detailed setup instructions
- See `supabase_schema.sql` for database schema
- See `ADMIN_USER_FLOW.md` for application flow documentation

