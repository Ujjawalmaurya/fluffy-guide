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

-- ============================================
-- MIGRATION 002: Assessment + Gap Analysis
-- Run this in Supabase SQL editor AFTER Migration 001
-- ============================================

-- Modify questionnaire_sessions (add columns only)
ALTER TABLE questionnaire_sessions
  ADD COLUMN IF NOT EXISTS assessment_type TEXT DEFAULT 'onboarding',
  -- 'onboarding' | 'quick_assessment'
  ADD COLUMN IF NOT EXISTS retake_number INTEGER DEFAULT 0,
  -- Which attempt this is. 0=first attempt, 1=first retake
  ADD COLUMN IF NOT EXISTS max_retakes INTEGER DEFAULT 2,
  -- Copied from config at session creation time
  ADD COLUMN IF NOT EXISTS phase INTEGER DEFAULT 1,
  -- 1=Situation 2=Skills 3=WorkStyle 4=Goals 5=Wildcard
  ADD COLUMN IF NOT EXISTS current_question_number INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS adaptive_context JSONB DEFAULT '[]',
  -- Full conversation: [{role:"user"|"assistant", content:"..."}]
  ADD COLUMN IF NOT EXISTS extracted_proficiency JSONB DEFAULT '[]',
  -- [{skill_name, proficiency_numeric, proficiency_label, confidence}]
  ADD COLUMN IF NOT EXISTS is_complete BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS last_question_at TIMESTAMPTZ;

-- Modify users table (add assessment tracking)
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS quick_assessment_done BOOLEAN DEFAULT false;
  -- True after first quick_assessment session completed

-- Modify profile_enrichments (add Gemini extraction columns)
ALTER TABLE profile_enrichments
  ADD COLUMN IF NOT EXISTS gemini_extracted JSONB,
  -- Full Gemini extraction output. Structure documented below.
  ADD COLUMN IF NOT EXISTS extraction_model TEXT DEFAULT 'gemini-1.5-flash',
  ADD COLUMN IF NOT EXISTS extraction_status TEXT DEFAULT 'pending';
  -- 'pending' | 'processing' | 'done' | 'failed'

-- NEW TABLE: user_skill_profiles
-- Single source of truth for a user's skills.
-- Updated by both resume parsing and assessment completion.
CREATE TABLE IF NOT EXISTS user_skill_profiles (
  id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  skills                 JSONB DEFAULT '[]',
  -- Array of skill objects:
  -- [{
  --   skill_name: string,
  --   category: string,          ("technical|soft|domain|tool|language")
  --   proficiency_numeric: int,  (1-5)
  --   proficiency_label: string, ("Beginner|Elementary|Intermediate|Advanced|Expert")
  --   source: string,            ("resume"|"assessment"|"both")
  --   confidence_score: float,   (0.0 to 1.0)
  --   last_updated: timestamp
  -- }]
  profile_version        INTEGER DEFAULT 1,
  -- Incremented on every update. Used for staleness detection.
  resume_contributed     BOOLEAN DEFAULT false,
  -- True if resume parsing has fed into this profile
  assessment_contributed BOOLEAN DEFAULT false,
  -- True if assessment has fed into this profile
  created_at             TIMESTAMPTZ DEFAULT now(),
  updated_at             TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_skill_profiles_user
  ON user_skill_profiles(user_id);

-- NEW TABLE: gap_analysis_reports
-- Cached gap analysis result. Recomputed only when profile changes.
CREATE TABLE IF NOT EXISTS gap_analysis_reports (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id              UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  profile_hash         TEXT NOT NULL,
  -- SHA256 of sorted skills + timestamps. Changes = stale report.
  strengths            JSONB DEFAULT '[]',
  -- [{skill_name, proficiency_label, job_demand_pct, message}]
  gaps                 JSONB DEFAULT '[]',
  -- [{skill_name, category, priority_score, frequency_pct,
  --   learnability_weeks, recommended_resources:[resource_id]}]
  partial_matches      JSONB DEFAULT '[]',
  -- [{skill_name, current_level, required_level, gap_size}]
  target_roles         TEXT[],
  total_jobs_analyzed  INTEGER DEFAULT 0,
  roadmap              JSONB DEFAULT '[]',
  -- [{week, focus_skill, goal, action, resource_id,
  --   resource_name, resource_url, milestone}]
  is_stale             BOOLEAN DEFAULT false,
  -- Set true when profile_hash no longer matches current profile
  gemini_raw_output    TEXT,
  -- Stored for debugging. Never shown to user.
  computed_at          TIMESTAMPTZ DEFAULT now(),
  created_at           TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_gap_reports_user
  ON gap_analysis_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_gap_reports_stale
  ON gap_analysis_reports(user_id, is_stale);

-- NEW TABLE: learning_resources
-- Curated resource library. Gemini picks from here. Never invents.
CREATE TABLE IF NOT EXISTS learning_resources (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name             TEXT NOT NULL,
  -- Full name e.g. "Python for Everybody - NPTEL"
  provider         TEXT NOT NULL,
  -- "SWAYAM" | "NPTEL" | "PMKVY" | "Coursera" | "YouTube" | "NSDC" | "freeCodeCamp"
  url              TEXT NOT NULL,
  description      TEXT,
  skill_tags       TEXT[] NOT NULL,
  -- Skills this resource teaches e.g. ['python','data analysis']
  category         TEXT NOT NULL,
  -- 'technology'|'business'|'vocational'|'soft_skills'|'language'|'healthcare'
  is_free          BOOLEAN DEFAULT true,
  cost_inr         INTEGER DEFAULT 0,
  duration_weeks   INTEGER,
  difficulty_level INTEGER,
  -- 1=absolute beginner to 5=expert
  language         TEXT DEFAULT 'en',
  -- 'en' | 'hi' | 'both'
  delivery_type    TEXT,
  -- 'video'|'certification'|'self_paced'|'workshop'|'book'
  is_active        BOOLEAN DEFAULT true,
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_resources_tags
  ON learning_resources USING GIN(skill_tags);
CREATE INDEX IF NOT EXISTS idx_resources_category
  ON learning_resources(category);
CREATE INDEX IF NOT EXISTS idx_resources_active
  ON learning_resources(is_active);

-- SEED: 10 curated Indian learning resources
INSERT INTO learning_resources
  (name, provider, url, description, skill_tags, category,
   is_free, cost_inr, duration_weeks, difficulty_level, language, delivery_type)
VALUES
('Python Programming - NPTEL',
 'NPTEL', 'https://nptel.ac.in/courses/106/106/106106212/',
 'Foundational Python course with certification from IIT',
 ARRAY['python','programming','data analysis'],
 'technology', true, 0, 12, 2, 'en', 'certification'),

('Tally Prime with GST - Hindi',
 'YouTube', 'https://www.youtube.com/@TallyPrime',
 'Complete Tally Prime tutorial in Hindi covering GST filing',
 ARRAY['tally','accounting','gst','finance'],
 'business', true, 0, 4, 1, 'hi', 'video'),

('Digital Marketing - SWAYAM',
 'SWAYAM', 'https://swayam.gov.in/nd1_noc20_mg54/preview',
 'Govt certified digital marketing course covering SEO and social media',
 ARRAY['digital marketing','social media','seo','content'],
 'business', true, 0, 8, 2, 'en', 'certification'),

('EV Technology Fundamentals - PMKVY',
 'PMKVY', 'https://www.pmkvyofficial.org/',
 'Electric vehicle repair and maintenance vocational training',
 ARRAY['electric vehicles','ev repair','automotive','mechanics'],
 'vocational', true, 0, 12, 2, 'hi', 'workshop'),

('Data Analysis with Excel - NPTEL',
 'NPTEL', 'https://nptel.ac.in/courses/110/110/110110006/',
 'Excel for data analysis including pivot tables and charts',
 ARRAY['excel','data analysis','spreadsheets','ms office'],
 'technology', true, 0, 8, 1, 'en', 'certification'),

('English Communication Skills - SWAYAM',
 'SWAYAM', 'https://swayam.gov.in/nd1_noc20_hu01/preview',
 'Improve spoken and written English for professional settings',
 ARRAY['english','communication','soft skills','presentation'],
 'soft_skills', true, 0, 6, 1, 'en', 'self_paced'),

('Full Stack Web Development - freeCodeCamp',
 'freeCodeCamp', 'https://www.freecodecamp.org/learn',
 'Complete web development from HTML basics to React and Node',
 ARRAY['html','css','javascript','react','nodejs','web development'],
 'technology', true, 0, 20, 2, 'en', 'self_paced'),

('Healthcare and Nursing Assistant - PMKVY',
 'PMKVY', 'https://www.pmkvyofficial.org/',
 'Vocational training for nursing assistant and patient care',
 ARRAY['healthcare','nursing','patient care','first aid'],
 'healthcare', true, 0, 16, 2, 'hi', 'workshop'),

('Logistics and Supply Chain - NSDC',
 'NSDC', 'https://www.nsdcindia.org/',
 'Warehouse management, inventory and supply chain fundamentals',
 ARRAY['logistics','supply chain','warehouse','inventory'],
 'vocational', true, 0, 8, 2, 'en', 'certification'),

('Spoken Hindi for Professionals - SWAYAM',
 'SWAYAM', 'https://swayam.gov.in',
 'Professional Hindi communication for workplace settings',
 ARRAY['hindi','communication','language','soft skills'],
 'language', true, 0, 4, 1, 'hi', 'self_paced');
