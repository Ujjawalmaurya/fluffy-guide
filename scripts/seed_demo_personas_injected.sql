-- Seed demo personas for hackathon judging
-- These accounts use standard Supabase Auth with password seeded by seed_demo_auth.py
-- This script seeds profile & preferences data assuming UUIDs are known.
-- The seed_demo_auth.py script replaces these UUIDs with actual ones.

-- === RAVI === Rural youth from UP (Vocational/PMKVY focus)
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES
  ('19499f81-d09f-4cec-9170-d2dd7a73998b', 'Ravi Kumar', 22, 'male', 'Uttar Pradesh', 'Varanasi', 'Secondary', ARRAY['Hindi', 'Bhojpuri'])
ON CONFLICT (user_id) DO UPDATE SET
  full_name = EXCLUDED.full_name,
  age = EXCLUDED.age,
  state = EXCLUDED.state,
  city = EXCLUDED.city,
  education_level = EXCLUDED.education_level,
  languages = EXCLUDED.languages;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles, skill_tags)
VALUES
  ('19499f81-d09f-4cec-9170-d2dd7a73998b', ARRAY['manufacturing', 'construction'], 12000, 25000, 'onsite', true,
   ARRAY['Electrician', 'Solar Technician'], ARRAY['Basic Electricals', 'Solar Panel Installation'])
ON CONFLICT (user_id) DO UPDATE SET
  career_interests = EXCLUDED.career_interests,
  target_roles = EXCLUDED.target_roles,
  skill_tags = EXCLUDED.skill_tags;

UPDATE users SET onboarding_done = true, user_type = 'individual' WHERE id = '19499f81-d09f-4cec-9170-d2dd7a73998b';

-- === MEERA === Self-employed woman from Bihar (SHG/Microfinance focus)
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES
  ('b401e096-7adf-4177-b606-acc16e670984', 'Meera Devi', 34, 'female', 'Bihar', 'Muzaffarpur', 'Primary', ARRAY['Hindi', 'Maithili'])
ON CONFLICT (user_id) DO UPDATE SET
  full_name = EXCLUDED.full_name,
  age = EXCLUDED.age,
  state = EXCLUDED.state,
  city = EXCLUDED.city,
  education_level = EXCLUDED.education_level,
  languages = EXCLUDED.languages;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles, skill_tags)
VALUES
  ('b401e096-7adf-4177-b606-acc16e670984', ARRAY['textiles', 'handicrafts', 'finance'], 8000, 20000, 'hybrid', false,
   ARRAY['Tailoring', 'SHG Leader'], ARRAY['Embroidery', 'Stitching', 'Community Leadership'])
ON CONFLICT (user_id) DO UPDATE SET
  career_interests = EXCLUDED.career_interests,
  target_roles = EXCLUDED.target_roles,
  skill_tags = EXCLUDED.skill_tags;

UPDATE users SET onboarding_done = true, user_type = 'individual' WHERE id = 'b401e096-7adf-4177-b606-acc16e670984';

-- === ARJUN === Retrenched industrial worker from Tamil Nadu (Reskilling focus)
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES
  ('d07b48ff-ed15-40a8-be21-0c1e0a3ae392', 'Arjun Subramanian', 42, 'male', 'Tamil Nadu', 'Coimbatore', 'Diploma', ARRAY['Tamil', 'English'])
ON CONFLICT (user_id) DO UPDATE SET
  full_name = EXCLUDED.full_name,
  age = EXCLUDED.age,
  state = EXCLUDED.state,
  city = EXCLUDED.city,
  education_level = EXCLUDED.education_level,
  languages = EXCLUDED.languages;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles, skill_tags)
VALUES
  ('d07b48ff-ed15-40a8-be21-0c1e0a3ae392', ARRAY['it_services', 'logistics', 'education'], 30000, 70000, 'remote', true,
   ARRAY['Data Entry', 'Logistics Coordinator'], ARRAY['MS Excel', 'Inventory Management', 'Basic Coding', 'Tamil Typing'])
ON CONFLICT (user_id) DO UPDATE SET
  career_interests = EXCLUDED.career_interests,
  target_roles = EXCLUDED.target_roles,
  skill_tags = EXCLUDED.skill_tags;

UPDATE users SET onboarding_done = true, user_type = 'individual' WHERE id = 'd07b48ff-ed15-40a8-be21-0c1e0a3ae392';

-- === ADMIN === SANKALP Platform Admin
INSERT INTO user_profiles (user_id, full_name, age, gender, state, city, education_level, languages)
VALUES
  ('2a27c06e-56a3-42cb-ba40-799a323c3b21', 'System Admin', 35, 'male', 'Delhi', 'New Delhi', 'PhD', ARRAY['English', 'Hindi'])
ON CONFLICT (user_id) DO UPDATE SET
  full_name = EXCLUDED.full_name,
  age = EXCLUDED.age,
  state = EXCLUDED.state,
  city = EXCLUDED.city,
  education_level = EXCLUDED.education_level,
  languages = EXCLUDED.languages;

INSERT INTO user_preferences (user_id, career_interests, expected_salary_min, expected_salary_max, work_type, willing_to_relocate, target_roles, skill_tags)
VALUES
  ('2a27c06e-56a3-42cb-ba40-799a323c3b21', ARRAY['government', 'finance'], 100000, 200000, 'onsite', false,
   ARRAY['Principal Secretary', 'Project Manager'], ARRAY['Management', 'Strategy', 'Public Policy'])
ON CONFLICT (user_id) DO UPDATE SET
  career_interests = EXCLUDED.career_interests,
  target_roles = EXCLUDED.target_roles,
  skill_tags = EXCLUDED.skill_tags;

UPDATE users SET onboarding_done = true, user_type = 'government' WHERE id = '2a27c06e-56a3-42cb-ba40-799a323c3b21';
