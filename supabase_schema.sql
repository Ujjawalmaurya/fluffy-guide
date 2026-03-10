-- SkillBridge AI — Supabase Schema
-- Run this entire file in your Supabase SQL Editor (Database → SQL Editor → New Query)
-- RLS is disabled — backend uses service_role key and handles auth itself

-- ─────────────────────────────────────────────────────────────
-- Utility: auto-update updated_at on any table that has it
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ─────────────────────────────────────────────────────────────
-- TABLE: users
-- Central user record. Created on first OTP verify.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS users (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  email           TEXT        UNIQUE NOT NULL,          -- Login identifier (no password)
  user_type       TEXT,                                 -- Enum: individual_youth, individual_bluecollar, etc.
  preferred_lang  TEXT        DEFAULT 'en',             -- 'en' or 'hi'
  is_active       BOOLEAN     DEFAULT true,             -- Soft-disable account if needed
  onboarding_done BOOLEAN     DEFAULT false,            -- Flipped to true after questionnaire submit
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

CREATE TRIGGER trg_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

ALTER TABLE users DISABLE ROW LEVEL SECURITY;


-- ─────────────────────────────────────────────────────────────
-- TABLE: otp_store
-- Short-lived OTP records. Cleaned up after use or expiry.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS otp_store (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  email       TEXT        NOT NULL,                     -- Email this OTP was generated for
  otp_code    TEXT        NOT NULL,                     -- 6-digit code stored as text
  expires_at  TIMESTAMPTZ NOT NULL,                     -- now() + 10 minutes at generation time
  is_used     BOOLEAN     DEFAULT false,                -- Marked true after successful verification
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_otp_email ON otp_store(email);
CREATE INDEX IF NOT EXISTS idx_otp_expires ON otp_store(expires_at);

ALTER TABLE otp_store DISABLE ROW LEVEL SECURITY;


-- ─────────────────────────────────────────────────────────────
-- TABLE: user_profiles
-- One row per user. Core demographic and contact info.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_profiles (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id         UUID        REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  full_name       TEXT,                                 -- User's full name
  age             INTEGER,                              -- Age in years
  gender          TEXT,                                 -- 'male', 'female', 'other', 'prefer_not'
  state           TEXT,                                 -- Indian state name (e.g. "Uttar Pradesh")
  city            TEXT,                                 -- City within state
  education_level TEXT,                                 -- 'none','primary','secondary','graduate','postgrad'
  languages       TEXT[],                               -- Languages known e.g. ['Hindi','English']
  phone           TEXT,                                 -- Optional mobile number
  avatar_url      TEXT,                                 -- Optional profile picture URL
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON user_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_profiles_state ON user_profiles(state);

CREATE TRIGGER trg_profiles_updated_at
  BEFORE UPDATE ON user_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

ALTER TABLE user_profiles DISABLE ROW LEVEL SECURITY;


-- ─────────────────────────────────────────────────────────────
-- TABLE: user_preferences
-- Career goals and work preferences. One row per user.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_preferences (
  id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id             UUID        REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  career_interests    TEXT[],                           -- e.g. ['technology','healthcare','logistics']
  expected_salary_min INTEGER,                          -- Monthly salary expectation in INR (minimum)
  expected_salary_max INTEGER,                          -- Monthly salary expectation in INR (maximum)
  work_type           TEXT,                             -- 'remote','onsite','hybrid','any'
  willing_to_relocate BOOLEAN     DEFAULT false,        -- Whether user is open to relocation
  target_roles        TEXT[],                           -- e.g. ['software developer','data analyst']
  created_at          TIMESTAMPTZ DEFAULT now(),
  updated_at          TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_prefs_user_id ON user_preferences(user_id);

CREATE TRIGGER trg_prefs_updated_at
  BEFORE UPDATE ON user_preferences
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

ALTER TABLE user_preferences DISABLE ROW LEVEL SECURITY;


-- ─────────────────────────────────────────────────────────────
-- TABLE: questionnaire_sessions
-- Stores AI-generated questions and user's submitted answers.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS questionnaire_sessions (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          UUID        REFERENCES users(id) ON DELETE CASCADE,
  language         TEXT        DEFAULT 'en',            -- 'en' or 'hi' — language questions shown in
  questions_data   JSONB,                               -- Array: [{id, question, type, options}]
  answers_data     JSONB,                               -- Array: [{question_id, question_text, answer}]
  extracted_skills TEXT[],                              -- Skills parsed from answers during SSE processing
  completed_at     TIMESTAMPTZ,                         -- Set when answers submitted
  created_at       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_qs_user_id ON questionnaire_sessions(user_id);

ALTER TABLE questionnaire_sessions DISABLE ROW LEVEL SECURITY;


-- ─────────────────────────────────────────────────────────────
-- TABLE: profile_enrichments
-- Resume data extracted by pdfplumber. One row per user.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS profile_enrichments (
  id                    UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id               UUID        REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  resume_original_name  TEXT,                           -- Original filename user uploaded
  resume_raw_text       TEXT,                           -- Full text extracted from the PDF
  resume_parsed         JSONB,                          -- Structured: {skills: [], education: [], experience: []}
  resume_uploaded_at    TIMESTAMPTZ,                    -- When the resume was uploaded
  created_at            TIMESTAMPTZ DEFAULT now(),
  updated_at            TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_enrichments_user_id ON profile_enrichments(user_id);

CREATE TRIGGER trg_enrichments_updated_at
  BEFORE UPDATE ON profile_enrichments
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

ALTER TABLE profile_enrichments DISABLE ROW LEVEL SECURITY;


-- ─────────────────────────────────────────────────────────────
-- TABLE: job_listings
-- Job data — inserted by admin via API or bulk upload.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS job_listings (
  id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  title           TEXT        NOT NULL,                 -- Job title
  company         TEXT        NOT NULL,                 -- Company name
  description     TEXT,                                 -- Job description (can be long)
  location_state  TEXT        NOT NULL,                 -- Indian state (for regional filtering)
  location_city   TEXT,                                 -- City within state
  job_type        TEXT,                                 -- 'full_time','part_time','contract','gig'
  work_mode       TEXT,                                 -- 'remote','onsite','hybrid'
  category        TEXT        NOT NULL,                 -- 'technology','healthcare','logistics', etc.
  required_skills TEXT[],                               -- Skills array for matching
  salary_min      INTEGER,                              -- Minimum monthly salary in INR
  salary_max      INTEGER,                              -- Maximum monthly salary in INR
  experience_min  INTEGER,                              -- Minimum years of experience required
  source_url      TEXT,                                 -- Original job posting URL if scraped
  is_active       BOOLEAN     DEFAULT true,             -- Soft delete flag
  created_at      TIMESTAMPTZ DEFAULT now(),
  updated_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_jobs_state ON job_listings(location_state);
CREATE INDEX IF NOT EXISTS idx_jobs_category ON job_listings(category);
CREATE INDEX IF NOT EXISTS idx_jobs_active ON job_listings(is_active);

CREATE TRIGGER trg_jobs_updated_at
  BEFORE UPDATE ON job_listings
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

ALTER TABLE job_listings DISABLE ROW LEVEL SECURITY;


-- ─────────────────────────────────────────────────────────────
-- TABLE: chat_messages
-- Per-user chat history for AI assistant context window.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS chat_messages (
  id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id     UUID        REFERENCES users(id) ON DELETE CASCADE,
  role        TEXT        NOT NULL,                     -- 'user' or 'assistant'
  content     TEXT        NOT NULL,                     -- Message text
  language    TEXT        DEFAULT 'en',                 -- Language of this message ('en' or 'hi')
  created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_chat_user_id ON chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_created ON chat_messages(created_at);

ALTER TABLE chat_messages DISABLE ROW LEVEL SECURITY;


-- ─────────────────────────────────────────────────────────────
-- TABLE: onboarding_state
-- Tracks multi-step onboarding progress per user.
-- Used for resume-on-refresh behaviour.
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS onboarding_state (
  id               UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id          UUID        REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  current_step     INTEGER     DEFAULT 1,               -- 1=user_type 2=profile 3=prefs 4=questions 5=done
  completed_steps  INTEGER[]   DEFAULT '{}',            -- e.g. {1,2,3}
  step_data        JSONB       DEFAULT '{}',            -- Temp storage for in-progress step data
  updated_at       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_onboarding_user_id ON onboarding_state(user_id);

CREATE TRIGGER trg_onboarding_updated_at
  BEFORE UPDATE ON onboarding_state
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

ALTER TABLE onboarding_state DISABLE ROW LEVEL SECURITY;
