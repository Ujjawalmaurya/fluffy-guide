-- Seed demo personas for hackathon judging (run once in Supabase SQL editor)
-- These accounts use standard Supabase Auth with password: DemoSankalp2025!

-- NOTE: Users are normally created via Supabase Auth, so we call the admin API.
-- This script seeds profile & preferences data assuming UUIDs are known.
-- Replace the UUIDs below after running "create user" via Supabase Studio.

-- === RAMESH === Rural tech aspirant from MP
-- UUID: replace-with-ramesh-uuid-from-supabase-auth
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES
  ('5a63ebfc-9ae7-4c42-b1b5-a9421ce0599d', 'Ramesh Verma', 24, 'male', 'Madhya Pradesh', 'Indore', 'Bachelor', ARRAY['Hindi', 'English'])
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles, skill_tags)
VALUES
  ('5a63ebfc-9ae7-4c42-b1b5-a9421ce0599d', ARRAY['technology', 'logistics'], 15000, 35000, 'hybrid', true,
   ARRAY['Software Developer', 'IT Support'], ARRAY['Python', 'JavaScript', 'SQL', 'Linux'])
ON CONFLICT (user_id) DO NOTHING;

UPDATE users SET onboarding_done = true WHERE id = '5a63ebfc-9ae7-4c42-b1b5-a9421ce0599d';

-- === PRIYA === Healthcare professional from Maharashtra
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES
  ('2b0fb361-b93e-42b0-925f-718f967a57de', 'Priya Sharma', 28, 'female', 'Maharashtra', 'Pune', 'Masters', ARRAY['Hindi', 'English', 'Marathi'])
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles, skill_tags)
VALUES
  ('2b0fb361-b93e-42b0-925f-718f967a57de', ARRAY['healthcare', 'education'], 25000, 60000, 'onsite', false,
   ARRAY['Staff Nurse', 'Clinical Coordinator'], ARRAY['Patient Care', 'Pharmacology', 'Medical Records', 'First Aid'])
ON CONFLICT (user_id) DO NOTHING;

UPDATE users SET onboarding_done = true WHERE id = '2b0fb361-b93e-42b0-925f-718f967a57de';

-- === OFFICER === Government evaluator
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES
  ('189c5104-9b14-4eee-a7f0-912649080b8d', 'Ravi Officer', 40, 'male', 'Delhi', 'New Delhi', 'Masters', ARRAY['Hindi', 'English'])
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles, skill_tags)
VALUES
  ('189c5104-9b14-4eee-a7f0-912649080b8d', ARRAY['finance', 'general'], 50000, 100000, 'onsite', false,
   ARRAY['Policy Analyst', 'Program Manager'], ARRAY['Data Analysis', 'Policy', 'MS Office', 'Communication'])
ON CONFLICT (user_id) DO NOTHING;

UPDATE users SET onboarding_done = true, user_type = 'government' WHERE id = '189c5104-9b14-4eee-a7f0-912649080b8d';
