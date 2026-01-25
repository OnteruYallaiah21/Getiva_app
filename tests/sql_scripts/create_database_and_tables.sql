-- Create Getiva_Tracking Database and Tables in Aiven PostgreSQL
-- Run this script in your Aiven PostgreSQL console (connect to 'defaultdb' first, then create database)

-- Step 1: Create the database (run this first while connected to 'defaultdb' or 'postgres' database)
-- Note: In Aiven, you may need to create the database through the Aiven Console UI instead of SQL
CREATE DATABASE "Getiva_Tracking";

-- Step 2: Connect to the new database and run the following commands:

-- Users table
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Leads table
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

-- Recruiters table
CREATE TABLE IF NOT EXISTS recruiters (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    deals_with TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Applications table
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_created_at ON leads(created_at);
CREATE INDEX IF NOT EXISTS idx_recruiters_deals_with ON recruiters(deals_with);
CREATE INDEX IF NOT EXISTS idx_applications_username ON applications(username);
CREATE INDEX IF NOT EXISTS idx_applications_timestamp ON applications(timestamp);

-- Verify tables were created
SELECT 
    table_name, 
    table_type 
FROM information_schema.tables 
WHERE table_schema = 'public' 
    AND table_name IN ('users', 'leads', 'recruiters', 'applications')
ORDER BY table_name;

-- Success message
SELECT '✅ Database Getiva_Tracking and all tables created successfully!' AS status;

