-- Seed demo personas for judge review
-- Standards for UUIDs are matched with auth.users seeded IDs

-- RAMESH
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES ('daa14278-f26b-4404-95cc-5eb169925fed', 'Ramesh Verma', 24, 'male', 'Madhya Pradesh', 'Indore', 'Bachelor', ARRAY['Hindi', 'English'])
ON CONFLICT (user_id) DO UPDATE SET full_name = EXCLUDED.full_name;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles)
VALUES ('daa14278-f26b-4404-95cc-5eb169925fed', ARRAY['technology', 'logistics'], 15000, 35000, 'hybrid', true, ARRAY['Software Developer', 'IT Support'])
ON CONFLICT (user_id) DO UPDATE SET career_interests = EXCLUDED.career_interests;

INSERT INTO user_skill_profiles (user_id, skills, top_skills, assessment_contributed)
VALUES ('daa14278-f26b-4404-95cc-5eb169925fed', 
    '[{"name": "Python", "proficiency": "Intermediate"}, {"name": "SQL", "proficiency": "Beginner"}, {"name": "JavaScript", "proficiency": "Beginner"}]'::jsonb,
    ARRAY['Python', 'SQL'],
    true
)
ON CONFLICT (user_id) DO UPDATE SET skills = EXCLUDED.skills;

-- PRIYA
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES ('cea951a5-b448-4dc4-8c37-b83d1d5b689b', 'Priya Sharma', 28, 'female', 'Maharashtra', 'Pune', 'Masters', ARRAY['Hindi', 'English', 'Marathi'])
ON CONFLICT (user_id) DO UPDATE SET full_name = EXCLUDED.full_name;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles)
VALUES ('cea951a5-b448-4dc4-8c37-b83d1d5b689b', ARRAY['healthcare', 'education'], 25000, 60000, 'onsite', false, ARRAY['Staff Nurse', 'Clinical Coordinator'])
ON CONFLICT (user_id) DO UPDATE SET career_interests = EXCLUDED.career_interests;

INSERT INTO user_skill_profiles (user_id, skills, top_skills, assessment_contributed)
VALUES ('cea951a5-b448-4dc4-8c37-b83d1d5b689b', 
    '[{"name": "Patient Care", "proficiency": "Expert"}, {"name": "Pharmacology", "proficiency": "Intermediate"}]'::jsonb,
    ARRAY['Patient Care', 'Pharmacology'],
    true
)
ON CONFLICT (user_id) DO UPDATE SET skills = EXCLUDED.skills;

-- OFFICER
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES ('52001edf-a140-4d78-9e33-4705ffeed9e8', 'Ravi Officer', 40, 'male', 'Delhi', 'New Delhi', 'Masters', ARRAY['Hindi', 'English'])
ON CONFLICT (user_id) DO UPDATE SET full_name = EXCLUDED.full_name;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles)
VALUES ('52001edf-a140-4d78-9e33-4705ffeed9e8', ARRAY['finance', 'government'], 50000, 100000, 'onsite', false, ARRAY['Policy Analyst', 'Program Manager'])
ON CONFLICT (user_id) DO UPDATE SET career_interests = EXCLUDED.career_interests;

UPDATE public.users SET onboarding_done = true, user_type = 'student' WHERE id IN ('daa14278-f26b-4404-95cc-5eb169925fed', 'cea951a5-b448-4dc4-8c37-b83d1d5b689b');
UPDATE public.users SET onboarding_done = true, user_type = 'government' WHERE id = '52001edf-a140-4d78-9e33-4705ffeed9e8';
