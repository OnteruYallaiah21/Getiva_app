-- ============================================
-- SUPABASE DATABASE TABLES CREATION SQL
-- ============================================
-- Run this SQL in your Supabase SQL Editor
-- Go to: https://supabase.com/dashboard → Your Project → SQL Editor
-- ============================================

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Leads Table
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    status TEXT DEFAULT 'talk',
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Recruiters Table
CREATE TABLE IF NOT EXISTS recruiters (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    deals_with TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. Applications Table
CREATE TABLE IF NOT EXISTS applications (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    company TEXT NOT NULL,
    jobdescription TEXT,
    filename TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    download_link TEXT,
    view_link TEXT,
    status TEXT DEFAULT 'applied'
);

-- ============================================
-- OPTIONAL: Create indexes for better performance
-- ============================================

-- Index on username for applications (for faster user queries)
CREATE INDEX IF NOT EXISTS idx_applications_username ON applications(username);

-- Index on timestamp for applications (for faster date filtering)
CREATE INDEX IF NOT EXISTS idx_applications_timestamp ON applications(timestamp);

-- Index on status for leads (for faster status filtering)
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);

-- Index on username for users (already primary key, but good to have)
-- Note: Primary key already creates an index automatically

-- ============================================
-- VERIFY TABLES WERE CREATED
-- ============================================
-- Run this query to verify all tables exist:
-- SELECT table_name 
-- FROM information_schema.tables 
-- WHERE table_schema = 'public' 
-- AND table_name IN ('users', 'leads', 'recruiters', 'applications')
-- ORDER BY table_name;
-- ============================================

