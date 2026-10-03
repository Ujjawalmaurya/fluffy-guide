-- SkillBridge AI — Migration 002 (Standalone)
-- Run this ONLY if Migration 001 (base schema) is already applied.
-- If starting fresh, run the full supabase_schema.sql instead.

-- ─────────────────────────────────────────────────────────────
-- Utility: auto-update updated_at (skip if already exists)
-- ─────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ─────────────────────────────────────────────────────────────
-- Modify questionnaire_sessions (add new columns)
-- ─────────────────────────────────────────────────────────────
ALTER TABLE questionnaire_sessions
  ADD COLUMN IF NOT EXISTS assessment_type TEXT DEFAULT 'onboarding',
  ADD COLUMN IF NOT EXISTS retake_number INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS max_retakes INTEGER DEFAULT 2,
  ADD COLUMN IF NOT EXISTS phase INTEGER DEFAULT 1,
  ADD COLUMN IF NOT EXISTS current_question_number INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS adaptive_context JSONB DEFAULT '[]',
  ADD COLUMN IF NOT EXISTS extracted_proficiency JSONB DEFAULT '[]',
  ADD COLUMN IF NOT EXISTS is_complete BOOLEAN DEFAULT false,
  ADD COLUMN IF NOT EXISTS last_question_at TIMESTAMPTZ;

-- ─────────────────────────────────────────────────────────────
-- Modify users table (add assessment tracking)
-- ─────────────────────────────────────────────────────────────
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS quick_assessment_done BOOLEAN DEFAULT false;

-- ─────────────────────────────────────────────────────────────
-- Modify profile_enrichments (add Gemini extraction columns)
-- ─────────────────────────────────────────────────────────────
ALTER TABLE profile_enrichments
  ADD COLUMN IF NOT EXISTS gemini_extracted JSONB,
  ADD COLUMN IF NOT EXISTS extraction_model TEXT DEFAULT 'gemini-2.0-flash',
  ADD COLUMN IF NOT EXISTS extraction_status TEXT DEFAULT 'pending';

-- ─────────────────────────────────────────────────────────────
-- NEW TABLE: user_skill_profiles
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_skill_profiles (
  id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id                UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  skills                 JSONB DEFAULT '[]',
  profile_version        INTEGER DEFAULT 1,
  resume_contributed     BOOLEAN DEFAULT false,
  assessment_contributed BOOLEAN DEFAULT false,
  created_at             TIMESTAMPTZ DEFAULT now(),
  updated_at             TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_skill_profiles_user ON user_skill_profiles(user_id);
ALTER TABLE user_skill_profiles DISABLE ROW LEVEL SECURITY;


-- ─────────────────────────────────────────────────────────────
-- NEW TABLE: gap_analysis_reports
-- ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS gap_analysis_reports (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id              UUID REFERENCES users(id) ON DELETE CASCADE UNIQUE,
  profile_hash         TEXT NOT NULL,
  strengths            JSONB DEFAULT '[]',
  gaps                 JSONB DEFAULT '[]',
  partial_matches      JSONB DEFAULT '[]',
  target_roles         TEXT[],
  total_jobs_analyzed  INTEGER DEFAULT 0,
  roadmap              JSONB DEFAULT '[]',
  is_stale             BOOLEAN DEFAULT false,
  gemini_raw_output    TEXT,
  computed_at          TIMESTAMPTZ DEFAULT now(),
  created_at           TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_gap_reports_user ON gap_analysis_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_gap_reports_stale ON gap_analysis_reports(user_id, is_stale);
ALTER TABLE gap_analysis_reports DISABLE ROW LEVEL SECURITY;


-- ─────────────────────────────────────────────────────────────
-- TABLE: learning_resources
-- Drop and recreate to fix any partially-created state
-- ─────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS learning_resources CASCADE;

CREATE TABLE learning_resources (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name             TEXT NOT NULL,
  provider         TEXT NOT NULL,
  url              TEXT NOT NULL,
  description      TEXT,
  skill_tags       TEXT[] NOT NULL,
  category         TEXT NOT NULL,
  is_free          BOOLEAN DEFAULT true,
  cost_inr         INTEGER DEFAULT 0,
  duration_weeks   INTEGER,
  difficulty_level INTEGER,
  language         TEXT DEFAULT 'en',
  delivery_type    TEXT,
  is_active        BOOLEAN DEFAULT true,
  created_at       TIMESTAMPTZ DEFAULT now(),
  updated_at       TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_resources_tags ON learning_resources USING GIN(skill_tags);
CREATE INDEX idx_resources_category ON learning_resources(category);
CREATE INDEX idx_resources_active ON learning_resources(is_active);
ALTER TABLE learning_resources DISABLE ROW LEVEL SECURITY;


-- ─────────────────────────────────────────────────────────────
-- SEED: curated Indian learning resources
-- ─────────────────────────────────────────────────────────────
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
