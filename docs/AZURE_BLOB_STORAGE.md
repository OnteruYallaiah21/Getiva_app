# Azure Blob Storage Configuration

## Overview
All files (resumes, job descriptions) are stored in Azure Blob Storage, with links saved in the Supabase database. Only PDF, DOCX, and TXT files are supported.

## File Organization Structure

Files are organized by username in Azure Blob Storage containers:

```
Azure Blob Storage Container: getivastudentfiles
├── {username1}/
│   ├── resumes/
│   │   ├── resume_company1_20240111.pdf
│   │   ├── resume_company2_20240112.docx
│   │   └── ...
│   └── job_descriptions/
│       ├── jd_company1_20240111.pdf
│       ├── jd_company2_20240112.docx
│       ├── jd_company3_20240113.txt
│       └── ...
├── {username2}/
│   ├── resumes/
│   └── job_descriptions/
└── ...
```

## Blob Path Format

- **Resume**: `{username}/resumes/resume_{company}_{timestamp}.{ext}` (PDF, DOCX only)
- **Job Description**: `{username}/job_descriptions/jd_{company}_{timestamp}.{ext}` (PDF, DOCX, TXT only)

## Azure Blob Storage Setup

### 1. Storage Account ✅ (Already Configured)
- **Account name**: `getivablob`
- **Status**: Active and ready to use

### 2. Container ✅ (Already Created)
- **Container name**: `getivastudentfiles`
- **Public access level**: Private (we'll use SAS tokens or pre-signed URLs)

### 3. Get Connection String
1. Storage Account → Access Keys
2. Copy **Connection string** (or use Account name + Account key)

### 4. Environment Variables

Add to your `.env` file:

```env
# Azure Blob Storage Configuration
AZURE_STORAGE_ACCOUNT_NAME=getivablob
AZURE_STORAGE_ACCOUNT_KEY=your_azure_account_key_here
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=getivablob;AccountKey=your_azure_account_key_here;EndpointSuffix=core.windows.net
AZURE_STORAGE_CONTAINER_NAME=getivastudentfiles

# Supabase PostgreSQL Database
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@db.your-project.supabase.co:5432/postgres
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_key_here
```

## File Upload Flow

1. **User uploads file** → Frontend sends to backend API
2. **Backend receives file** → Validates file type and size
3. **Generate blob path** → `{username}/{file_type}/{filename}_{timestamp}.{ext}`
4. **Upload to Azure Blob** → Use Azure SDK to upload file
5. **Get blob URL** → Generate SAS token or public URL
6. **Save to Supabase** → Store URL in `applications` table or `file_metadata` table
7. **Return success** → Frontend receives confirmation and displays file

## File Access

- **Private Access**: Use SAS (Shared Access Signature) tokens with expiration
- **Pre-signed URLs**: Generate temporary URLs for file downloads
- **Public Access**: Not recommended for sensitive documents

## Python Azure SDK Example

```python
from azure.storage.blob import BlobServiceClient, BlobClient, generate_container_sas
from azure.storage.blob import ContainerSasPermissions
from datetime import datetime, timedelta

# Initialize client
connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_name = os.getenv("AZURE_STORAGE_CONTAINER_NAME")

# Upload file
def upload_file_to_azure(username: str, file_type: str, file_content: bytes, filename: str):
    # Generate blob path
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    blob_path = f"{username}/{file_type}/{file_type}_{timestamp}_{filename}"
    
    # Upload
    blob_client = blob_service_client.get_blob_client(
        container=container_name,
        blob=blob_path
    )
    blob_client.upload_blob(file_content, overwrite=True)
    
    # Generate SAS URL (valid for 1 hour)
    sas_token = generate_container_sas(
        account_name=os.getenv("AZURE_STORAGE_ACCOUNT_NAME"),
        container_name=container_name,
        account_key=os.getenv("AZURE_STORAGE_ACCOUNT_KEY"),
        permission=ContainerSasPermissions(read=True),
        expiry=datetime.utcnow() + timedelta(hours=1)
    )
    
    blob_url = f"https://getivablob.blob.core.windows.net/{container_name}/{blob_path}?{sas_token}"
    
    return blob_url, blob_path
```

## Supported File Types

- **Resumes**: PDF (.pdf), DOCX (.docx) only
- **Job Descriptions**: PDF (.pdf), DOCX (.docx), TXT (.txt) only
- All other file types will be rejected

## Security Best Practices

1. **Never expose account keys** in frontend code
2. **Use SAS tokens** with short expiration times
3. **Validate file types** before upload (only PDF, DOCX, TXT allowed)
4. **Set file size limits** (e.g., max 10MB per file)
5. **Use private containers** with SAS-based access
6. **Reject unsupported file types** immediately
7. **Implement virus scanning** for uploaded files (optional)

