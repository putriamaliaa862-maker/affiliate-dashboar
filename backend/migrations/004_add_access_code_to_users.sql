-- Migration 004: Add access_code to users table
-- Purpose: Enable users to have unique access codes for extension authentication
-- Date: 2026-01-18
-- Compatible with: SQLite, PostgreSQL

-- Add access_code column (nullable for existing users)
ALTER TABLE users ADD COLUMN access_code VARCHAR(64);

-- Add unique index to prevent duplicate access codes  
CREATE UNIQUE INDEX ix_users_access_code ON users(access_code);
