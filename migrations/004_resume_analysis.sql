-- Migration 004: Enhanced Resume Analysis
-- Table to store detailed AI analysis results for resumes

CREATE TABLE IF NOT EXISTS resume_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    resume_url TEXT, -- Supabase storage path
    raw_text TEXT, -- Extracted resume text
    structured_profile JSONB, -- Full extracted profile (StructuredProfile)
    quality_scores JSONB, -- All scoring dimensions (QualityScores)
    suggestions JSONB, -- Improvement suggestions (SuggestionSet)
    india_flags JSONB, -- India-specific detections
    overall_score INTEGER CHECK (overall_score >= 0 AND overall_score <= 100),
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now(),
    UNIQUE(user_id) -- Ensure one record per user, latest wins
);

-- Index for fast user lookup
CREATE INDEX IF NOT EXISTS idx_resume_analysis_user_id ON resume_analysis(user_id);

-- Trigger for updated_at
CREATE TRIGGER trg_resume_analysis_updated_at
    BEFORE UPDATE ON resume_analysis
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- RLS Policies
ALTER TABLE resume_analysis ENABLE ROW LEVEL SECURITY;

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'resume_analysis' AND policyname = 'Users can only read/write their own resume analysis'
    ) THEN
        CREATE POLICY "Users can only read/write their own resume analysis"
            ON resume_analysis
            FOR ALL
            USING (auth.uid() = user_id);
    END IF;
END $$;

-- Rate limiting table
CREATE TABLE IF NOT EXISTS user_rate_limits (
    user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    bullet_improvement_count INTEGER DEFAULT 0,
    last_reset_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE user_rate_limits DISABLE ROW LEVEL SECURITY;
