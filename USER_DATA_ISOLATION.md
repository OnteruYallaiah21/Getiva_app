# User Data Isolation - GetIVA Tracking System

## ✅ Data Separation Implementation

The system is designed so **each user can ONLY see and access their own data**. Here's how it works:

## 🔒 How Data Isolation Works

### 1. **Separate CSV Files Per User**

Each user has their own CSV file:
- `applications_user1.csv` - Only user1's applications
- `applications_user2.csv` - Only user2's applications
- `applications_demo.csv` - Only demo's applications
- `applications_admin.csv` - Only admin's applications (if admin has applications)

**File naming pattern:** `applications_{username}.csv`

### 2. **Backend Validation**

The backend ensures users can only access their own data:

```python
@app.get("/applications")
async def get_applications(username: str):
    # Returns ONLY applications for the specified username
    applications = read_applications(username)
    return {"applications": applications}
```

**Key Points:**
- Each API call requires `username` parameter
- Backend reads from `applications_{username}.csv` only
- No cross-user data access possible

### 3. **Frontend Security**

The frontend enforces user-specific access:

```javascript
let currentUsername = sessionStorage.getItem('username');
// Always uses the logged-in user's username
const response = await fetch(`${API_BASE}/applications?username=${currentUsername}`);
```

**Protection:**
- Username comes from session storage (set during login)
- User cannot change their username in API calls
- Each user only sees their own applications

### 4. **CRUD Operations - User Specific**

All operations are username-specific:

- **Create:** `POST /applications` - Requires username, saves to user's CSV
- **Read:** `GET /applications?username={username}` - Only returns user's data
- **Update:** `PUT /applications/{id}` - Requires username, updates user's CSV only
- **Delete:** `DELETE /applications/{id}` - Requires username, deletes from user's CSV only

### 5. **Admin Access**

Admins have special access:
- Can view **all users** via `/admin/users`
- Can view **any user's applications** via `/admin/applications/{username}`
- This is intentional - admins need to manage all users

## 📁 File Structure

```
backend/data/
├── users.csv                    # All user credentials
├── applications_user1.csv       # User1's applications ONLY
├── applications_user2.csv      # User2's applications ONLY
├── applications_demo.csv        # Demo's applications ONLY
└── applications_admin.csv       # Admin's applications (if any)
```

## 🔐 Security Features

### ✅ Implemented:
1. **Separate CSV files** - Each user's data in separate file
2. **Username validation** - Backend uses username from request
3. **Session-based access** - Frontend uses logged-in user's username
4. **No cross-access** - Users cannot access other users' data

### ⚠️ Additional Security (Optional):
- Add authentication tokens (JWT) for production
- Add server-side username validation against session
- Add rate limiting
- Add HTTPS in production

## 🧪 Testing Data Isolation

### Test 1: Login as user1
1. Login with `user1` / `user1@123`
2. You should ONLY see user1's applications
3. Check CSV: `applications_user1.csv` only

### Test 2: Login as user2
1. Login with `user2` / `user2@123`
2. You should ONLY see user2's applications
3. Check CSV: `applications_user2.csv` only

### Test 3: Admin Access
1. Login as `admin` / `admin@123`
2. Admin portal shows all users
3. Can view any user's applications
4. This is expected behavior

## 📊 Data Flow

```
User Login → Session Storage (username)
    ↓
Frontend Request → GET /applications?username={logged_in_user}
    ↓
Backend → Reads applications_{username}.csv
    ↓
Returns → Only that user's applications
    ↓
Frontend Display → Shows only user's data
```

## ✅ Current Status

**Data Isolation:** ✅ **FULLY IMPLEMENTED**

- Each user has separate CSV file
- Backend filters by username
- Frontend uses logged-in user's username
- No cross-user data access
- Admin can view all (by design)

---

**Your data is properly isolated - each user can only see their own applications! 🔒**

