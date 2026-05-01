-- Migration 005: Make email unique in otp_store to allow upsert
-- This ensures one user only has one active OTP entry.

-- 1. Clean up existing data to avoid constraint violation
DELETE FROM otp_store;

-- 2. Add unique constraint
ALTER TABLE otp_store ADD CONSTRAINT otp_store_email_key UNIQUE (email);
