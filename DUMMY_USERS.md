# Dummy User Accounts

The following test user accounts have been created for the GetIVA Tracking System:

## Admin Account

- **Username:** `admin`
- **Password:** `admin@123`
- **Role:** Admin
- **Access:** Full admin portal access (create/edit/delete users, view all applications)

## Regular User Accounts

### User 1
- **Username:** `user1`
- **Password:** `user1@123`
- **Role:** User
- **Access:** User portal (view/add/edit/delete own applications)

### User 2
- **Username:** `user2`
- **Password:** `user2@123`
- **Role:** User
- **Access:** User portal (view/add/edit/delete own applications)

### Demo User
- **Username:** `demo`
- **Password:** `demo@123`
- **Role:** User
- **Access:** User portal (view/add/edit/delete own applications)

## How to Login

1. **Access the application:**
   - Open browser and go to: `http://localhost:8000`
   - Or open `frontend/index.html` directly

2. **Login with any account:**
   - Enter username and password from the list above
   - Click "Login"

3. **What you'll see:**
   - **Admin users** → Redirected to Admin Portal
   - **Regular users** → Redirected to User Portal

## Testing

- All passwords are hashed using SHA256
- Each user has their own applications CSV file: `applications_{username}.csv`
- Admin can view all users and their applications
- Regular users can only see their own applications

## Security Note

⚠️ **Change the admin password in production!**
These are test accounts with simple passwords for development/testing purposes only.

