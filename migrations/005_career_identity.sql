-- 005_career_identity.sql
-- Adds fields for career identity persona and AI embeddings

-- 1. Profile Expansion
ALTER TABLE user_profiles
ADD COLUMN IF NOT EXISTS career_identity TEXT,
ADD COLUMN IF NOT EXISTS identity_embedding vector(384);

-- 2. Job Listings Expansion
-- We add an embedding column to jobs for vector similarity matching
ALTER TABLE job_listings
ADD COLUMN IF NOT EXISTS job_embedding vector(384);

-- 3. Skill Assessment Update
ALTER TABLE user_skill_profiles
ADD COLUMN IF NOT EXISTS top_skills TEXT[] DEFAULT '{}',
ADD COLUMN IF NOT EXISTS last_assessment_date TIMESTAMPTZ DEFAULT NOW();

-- 4. HNSW Indexes
CREATE INDEX IF NOT EXISTS idx_user_identity_embedding ON user_profiles 
USING hnsw (identity_embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_job_embedding ON job_listings 
USING hnsw (job_embedding vector_cosine_ops);

-- 5. RPC Function for Matching
-- This allows the backend to perform vector search directly in the DB
CREATE OR REPLACE FUNCTION match_jobs(
  query_embedding vector(384),
  match_threshold float,
  match_count int,
  filter_state text default null
)
RETURNS TABLE (
  id uuid,
  title text,
  company text,
  location_state text,
  location_city text,
  category text,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    j.id,
    j.title,
    j.company,
    j.location_state,
    j.location_city,
    j.category,
    1 - (j.job_embedding <=> query_embedding) AS similarity
  FROM job_listings j
  WHERE (j.location_state = filter_state OR filter_state IS NULL)
    AND j.is_active = true
    AND 1 - (j.job_embedding <=> query_embedding) > match_threshold
  ORDER BY j.job_embedding <=> query_embedding
  LIMIT match_count;
END;
$$;
