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
   - Store application files securely
   - View, update, and delete application records
   - Update application status (Applied, Interview, Rejected, etc.)
   - Pagination support for better performance (10 records per page)
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
   - Handle file storage for application documents

4. ✅ **Performance Optimization**
   - Implement pagination for large datasets
   - Optimize database queries
   - Provide clear loading messages
   - Ensure fast response times

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
- **File Management**: Upload and manage job application documents
- **Real-time Feedback**: Loading spinners and status messages for all operations
- **Performance**: Pagination and lazy loading for better performance

## System Architecture

- **Backend**: FastAPI (Python web framework)
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Session-based authentication
- **File Storage**: Secure file storage system
- **Data Storage**: Centralized data storage system

## Getting Started

1. Set up environment variables in `.env` file
2. Install backend dependencies: `pip install -r backend/requirements.txt`
3. Start the backend server: `python backend/main.py`
4. Open `frontend/index.html` in a web browser
5. Login with your credentials

## Notes

- All data operations use a centralized storage system
- The system uses a single login mechanism (no external database logins)
- File uploads are stored securely and linked to user accounts
- All operations provide visual feedback to users
- The system is designed for scalability and performance

