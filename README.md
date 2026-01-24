# GetIVA Tracking System

## Business Requirements

GetIVA Tracking System is a comprehensive web application designed to help manage and track job applications, leads, and recruiter relationships for the GetIVA business.

### What We Need

1. **Unified Login System**
   - Single login system for all users (admin and regular users)
   - Secure authentication for accessing the system
   - Role-based access control (Admin vs Regular User)

2. **User Management**
   - Create, view, update, and delete user accounts
   - Differentiate between admin users and regular users
   - Track user information and access levels

3. **Leads Management**
   - Track potential clients and business leads
   - Manage lead information (name, phone, email, status, comments)
   - Categorize leads by status: Paid, Opportunity, Follow Up, Talk
   - Search and filter leads by name
   - Group leads by status for better organization

4. **Recruiters Management**
   - Manage recruiter information (name, phone, deals with)
   - Link recruiters to specific users
   - Track which users each recruiter works with
   - Search and filter recruiters by name

5. **Job Application Tracking**
   - Allow users to upload job application documents (resumes, CVs)
   - Track applications by company name and job description
   - Upload and store audio recordings/notes for each application
   - Store application files securely in S3 bucket
   - Organize files in user-specific folders: `{username}/resumes/`, `{username}/job_descriptions/`, `{username}/audio/`
   - View, update, and delete application records
   - Update application status (Applied, Interview, Rejected, etc.)
   - Lazy loading: Load 2 records initially, then "Load More" button for additional records
   - Each user can only see and manage their own applications

6. **User Experience Features**
   - Modern, clean interface with glassmorphism design
   - Search functionality on all management pages
   - Loading indicators and status messages for all operations
   - Responsive design that works on different screen sizes
   - Clear visual feedback for add, update, and delete operations

## Project Goals

### To Complete This Project, We Need:

1. ✅ **Backend API Development**
   - RESTful API endpoints for all CRUD operations
   - Secure authentication and authorization
   - File upload and storage functionality
   - Efficient data retrieval with pagination support

2. ✅ **Frontend Development**
   - Login page with unified authentication
   - Admin portal for user management
   - Leads management interface
   - Recruiters management interface
   - User portal for job application tracking
   - Search and filter functionality
   - Loading spinners and status notifications

3. ✅ **Data Management**
   - Store all data securely
   - Ensure data integrity and relationships
   - Support efficient queries and operations
   - **S3 Bucket Storage**: Store all resumes, job descriptions, and audio files in AWS S3
   - **User-Specific Organization**: Each user's files stored in separate folders:
     - `{username}/resumes/` - Resume and CV files
     - `{username}/job_descriptions/` - Job description documents
     - `{username}/audio/` - Audio recordings and notes
   - Secure file access with proper permissions

4. ✅ **Performance Optimization** (Critical for Non-Dedicated Servers)
   - **Lazy Loading Strategy**: Load only 2 records initially, then "Load More" button to fetch additional records
   - Optimize database queries with proper indexing
   - Minimize data transfer by loading only what's needed
   - Implement efficient caching strategies
   - Reduce server load by batching requests
   - Provide clear loading messages
   - Ensure fast response times with minimal resource usage

5. ✅ **User Interface Design**
   - Modern glassmorphism/frosted glass effect design
   - Consistent styling across all pages
   - Intuitive navigation
   - Clear visual hierarchy

## Key Features

- **Single Login System**: One unified login for all users (no separate database logins)
- **Role-Based Access**: Admin users have full access, regular users have limited access
- **Complete CRUD Operations**: Create, Read, Update, Delete for all entities
- **Search Functionality**: Search by name on all management pages
- **Status Tracking**: Track leads and applications by status
- **Audio Support**: Upload and store audio recordings/notes for applications and leads
- **File Management**: Upload and manage job application documents
- **S3 Storage**: All files stored securely in AWS S3 bucket with user-specific organization
- **Lazy Loading**: Load 2 records at a time, then "Load More" button for optimization
- **Real-time Feedback**: Loading spinners and status messages for all operations
- **Performance Optimized**: Designed for non-dedicated servers with efficient resource usage

## System Architecture

- **Backend**: FastAPI (Python web framework)
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based authentication
- **File Storage**: AWS S3 Bucket for all file storage
- **Data Storage**: Centralized data storage system
- **Audio Storage**: Audio files stored in S3 under `{username}/audio/` folder

## Optimization Principles (For Non-Dedicated Servers)

Since we don't have a dedicated server, the following optimization principles are critical:

1. **Lazy Loading**
   - Load only 2 records initially on page load
   - Implement "Load More" button to fetch additional records incrementally
   - Reduces initial page load time and server resource usage
   - Improves user experience by showing content faster

2. **Efficient Data Fetching**
   - Fetch only necessary fields, not entire records
   - Use pagination and limit queries to small batches
   - Implement proper database indexing for faster queries
   - Cache frequently accessed data when possible

3. **File Storage Optimization**
   - Store all files (resumes, JD, audio) in S3 bucket, not on server
   - Reduces server storage and bandwidth usage
   - Organize files by user: `{username}/resumes/`, `{username}/job_descriptions/`, `{username}/audio/`
   - Use S3 pre-signed URLs for secure file access
   - Compress files before upload when possible

4. **Request Optimization**
   - Batch multiple operations when possible
   - Minimize API calls by combining related requests
   - Use efficient HTTP methods (GET for read, POST for create, etc.)
   - Implement request throttling to prevent overload

5. **Frontend Optimization**
   - Load resources on-demand (lazy load images, scripts)
   - Minimize JavaScript and CSS file sizes
   - Use efficient DOM manipulation
   - Implement client-side caching for static data

6. **Database Optimization**
   - Use proper indexes on frequently queried fields
   - Limit query results to what's needed
   - Use efficient JOIN operations
   - Clean up old/unused data periodically

## Getting Started

1. Set up environment variables in `.env` file
2. Install backend dependencies: `pip install -r backend/requirements.txt`
3. Start the backend server: `python backend/main.py`
4. Open `frontend/index.html` in a web browser
5. Login with your credentials

## File Storage Structure in S3

```
s3://getiva-tracking-bucket/
├── {username1}/
│   ├── resumes/
│   │   ├── resume_company1_date.pdf
│   │   ├── resume_company2_date.docx
│   │   └── ...
│   ├── job_descriptions/
│   │   ├── jd_company1_date.pdf
│   │   ├── jd_company2_date.txt
│   │   └── ...
│   └── audio/
│       ├── audio_note_company1_date.mp3
│       ├── audio_note_company2_date.wav
│       └── ...
├── {username2}/
│   ├── resumes/
│   ├── job_descriptions/
│   └── audio/
└── ...
```

## Notes

- All data operations use a centralized storage system
- The system uses a single login mechanism (no external database logins)
- **All file uploads (resumes, JD, audio) are stored in AWS S3 bucket**
- Files are organized by username in separate folders for better management
- Lazy loading (2 records at a time) ensures fast initial page loads
- All operations provide visual feedback to users
- The system is optimized for non-dedicated servers with minimal resource usage
- S3 pre-signed URLs are used for secure file access without exposing bucket credentials

