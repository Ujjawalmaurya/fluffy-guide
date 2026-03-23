-- Seed demo personas for hackathon judging (run once in Supabase SQL editor)
-- These accounts use standard Supabase Auth with password: DemoSankalp2025!

-- NOTE: Users are normally created via Supabase Auth, so we call the admin API.
-- This script seeds profile & preferences data assuming UUIDs are known.
-- Replace the UUIDs below after running "create user" via Supabase Studio.

-- === RAMESH === Rural tech aspirant from MP
-- UUID: replace-with-ramesh-uuid-from-supabase-auth
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES
  ('daa14278-f26b-4404-95cc-5eb169925fed', 'Ramesh Verma', 24, 'male', 'Madhya Pradesh', 'Indore', 'Bachelor', ARRAY['Hindi', 'English'])
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles, skill_tags)
VALUES
  ('daa14278-f26b-4404-95cc-5eb169925fed', ARRAY['technology', 'logistics'], 15000, 35000, 'hybrid', true,
   ARRAY['Software Developer', 'IT Support'], ARRAY['Python', 'JavaScript', 'SQL', 'Linux'])
ON CONFLICT (user_id) DO NOTHING;

UPDATE users SET onboarding_done = true WHERE id = 'daa14278-f26b-4404-95cc-5eb169925fed';

-- === PRIYA === Healthcare professional from Maharashtra
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES
  ('cea951a5-b448-4dc4-8c37-b83d1d5b689b', 'Priya Sharma', 28, 'female', 'Maharashtra', 'Pune', 'Masters', ARRAY['Hindi', 'English', 'Marathi'])
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles, skill_tags)
VALUES
  ('cea951a5-b448-4dc4-8c37-b83d1d5b689b', ARRAY['healthcare', 'education'], 25000, 60000, 'onsite', false,
   ARRAY['Staff Nurse', 'Clinical Coordinator'], ARRAY['Patient Care', 'Pharmacology', 'Medical Records', 'First Aid'])
ON CONFLICT (user_id) DO NOTHING;

UPDATE users SET onboarding_done = true WHERE id = 'cea951a5-b448-4dc4-8c37-b83d1d5b689b';

-- === OFFICER === Government evaluator
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES
  ('52001edf-a140-4d78-9e33-4705ffeed9e8', 'Ravi Officer', 40, 'male', 'Delhi', 'New Delhi', 'Masters', ARRAY['Hindi', 'English'])
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles, skill_tags)
VALUES
  ('52001edf-a140-4d78-9e33-4705ffeed9e8', ARRAY['finance', 'general'], 50000, 100000, 'onsite', false,
   ARRAY['Policy Analyst', 'Program Manager'], ARRAY['Data Analysis', 'Policy', 'MS Office', 'Communication'])
ON CONFLICT (user_id) DO NOTHING;

UPDATE users SET onboarding_done = true, user_type = 'government' WHERE id = '52001edf-a140-4d78-9e33-4705ffeed9e8';
