-- Migration 003: Analytics Views and Roles
-- Purpose: Enable government-level tracking and regional skill gap analysis.

-- 1. Add role column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS role TEXT DEFAULT 'youth';
COMMENT ON COLUMN users.role IS 'User roles: youth (default), officer, admin';

-- 2. View: District Training Funnel
-- Visualizes the conversion pipeline from registration to assessment completion by region.
CREATE OR REPLACE VIEW district_training_funnel AS
SELECT 
    up.state,
    up.city,
    COUNT(u.id) AS registered_count,
    COUNT(up.id) FILTER (WHERE up.is_onboarded = TRUE) AS onboarded_count,
    COUNT(qs.id) FILTER (WHERE qs.is_complete = TRUE) AS assessed_count
FROM 
    users u
LEFT JOIN 
    user_profiles up ON u.id = up.user_id
LEFT JOIN 
    questionnaire_sessions qs ON u.id = qs.user_id
GROUP BY 
    up.state, up.city;

-- 3. View: Regional Skill Demand (Aggregated from Job Listings)
CREATE OR REPLACE VIEW regional_skill_demand AS
SELECT 
    location_state AS state,
    location_city AS city,
    skill AS skill_name,
    COUNT(*) AS demand_count
FROM 
    job_listings,
    unnest(required_skills) AS skill
GROUP BY 
    location_state, location_city, skill;

-- 4. View: Regional Skill Supply (Aggregated from User Skill Profiles)
CREATE OR REPLACE VIEW regional_skill_supply AS
SELECT 
    up.state,
    up.city,
    skill AS skill_name,
    COUNT(*) AS supply_count
FROM 
    user_skill_profiles usp
JOIN 
    user_profiles up ON usp.user_id = up.user_id,
    unnest(usp.skills) AS skill
GROUP BY 
    up.state, up.city, skill;

-- 5. View: Skill Gap Analysis by Region
-- Combines demand and supply views to identify mismatches.
CREATE OR REPLACE VIEW skill_gap_by_region AS
SELECT 
    COALESCE(d.state, s.state) AS state,
    COALESCE(d.city, s.city) AS city,
    COALESCE(d.skill_name, s.skill_name) AS skill_name,
    COALESCE(d.demand_count, 0) AS demand,
    COALESCE(s.supply_count, 0) AS supply,
    (COALESCE(d.demand_count, 0) - COALESCE(s.supply_count, 0)) AS gap
FROM 
    regional_skill_demand d
FULL OUTER JOIN 
    regional_skill_supply s ON d.state = s.state AND d.city = s.city AND d.skill_name = s.skill_name;

-- 6. View: Monthly Training Outcomes (Regionalized)
CREATE OR REPLACE VIEW training_outcomes_monthly AS
SELECT 
    up.state,
    up.city,
    date_trunc('month', qs.completed_at) AS month,
    COUNT(*) AS completions_count
FROM 
    questionnaire_sessions qs
JOIN
    user_profiles up ON qs.user_id = up.user_id
WHERE 
    qs.is_complete = TRUE
GROUP BY 
    up.state, up.city, 3;
