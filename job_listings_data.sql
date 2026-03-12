-- Bulk Insert Job Listings with Diverse Categories and Requested Skills
-- Copy and run this in your Supabase SQL Editor

DELETE FROM job_listings WHERE company = 'SkillBridge Demo'; -- Cleanup previous demo data if any

INSERT INTO job_listings 
  (title, company, description, location_state, location_city, job_type, work_mode, category, required_skills, salary_min, salary_max, experience_min, is_active)
VALUES
-- TECHNOLOGY
('Senior Flutter Developer', 'SkillBridge Demo', 'Join our team to build high-performance cross-platform apps using Flutter and Dart.', 'Karnataka', 'Bengaluru', 'full_time', 'hybrid', 'technology', 
 ARRAY['Flutter', 'Dart', 'State Management (Bloc, Riverpod, Provider)', 'App Development', 'Iterative Development'], 80000, 150000, 4, true),

('Golang Backend Engineer', 'SkillBridge Demo', 'Scaling microservices for high-traffic financial applications using Go and CI/CD best practices.', 'Maharashtra', 'Pune', 'full_time', 'remote', 'technology', 
 ARRAY['Golang', 'Microservices', 'CI/CD Pipelines', 'RESTful APIs & WebSockets', 'Log Analysis'], 100000, 180000, 3, true),

('AI Prompt Engineer', 'SkillBridge Demo', 'Help us optimize our LLM workflows and ensure high-quality AI outputs.', 'Delhi', 'New Delhi', 'contract', 'hybrid', 'technology', 
 ARRAY['Prompt Engineering', 'AI Testing and Edge Case Identification', 'Technical Documentation Reading', 'Iterative Development'], 60000, 120000, 1, true),

-- FINANCE
('Fintech Integration Specialist', 'SkillBridge Demo', 'Focus on seamless payment processing and third-party integrations.', 'Karnataka', 'Bengaluru', 'full_time', 'onsite', 'finance', 
 ARRAY['Stripe Integration', 'Payment Gateway Integration', 'Stripe', 'Razorpay', 'RESTful APIs & WebSockets'], 70000, 130000, 2, true),

('Billing Solutions Architect', 'SkillBridge Demo', 'Designing robust billing and payment systems for the next generation of fintech.', 'Tamil Nadu', 'Chennai', 'full_time', 'remote', 'finance', 
 ARRAY['Stripe', 'Razorpay', 'Microservices', 'Technical Documentation Reading', 'CI/CD Pipelines'], 95000, 160000, 5, true),

-- LOGISTICS
('Supply Chain Automation Lead', 'SkillBridge Demo', 'Implementing automated tracking and logistics systems.', 'Haryana', 'Gurugram', 'full_time', 'onsite', 'logistics', 
 ARRAY['Logistics', 'Microservices', 'RESTful APIs & WebSockets', 'Technical Documentation Reading'], 55000, 95000, 3, true),

-- HEALTHCARE
('Health-Tech App Developer', 'SkillBridge Demo', 'Building patient-facing mobile apps for remote diagnostic tracking.', 'Telangana', 'Hyderabad', 'full_time', 'remote', 'healthcare', 
 ARRAY['Flutter', 'App Development', 'RESTful APIs & WebSockets', 'AI Testing and Edge Case Identification'], 75000, 140000, 3, true),

-- RETAIL & HOSPITALITY
('E-commerce Growth Manager', 'SkillBridge Demo', 'Leveraging social influence and data to drive online retail growth.', 'Maharashtra', 'Mumbai', 'full_time', 'hybrid', 'retail', 
 ARRAY['Humor & Social Influence', 'Prompt Engineering', 'Iterative Development'], 50000, 90000, 2, true),

-- MANUFACTURING & CONSTRUCTION
('Smart Factory Systems Engineer', 'SkillBridge Demo', 'Integrating IoT and modern tech into industrial manufacturing flows.', 'Gujarat', 'Ahmedabad', 'full_time', 'onsite', 'manufacturing', 
 ARRAY['Golang', 'Microservices', 'CI/CD Pipelines', 'Technical Documentation Reading'], 65000, 110000, 4, true),

-- AGRICULTURE & EDUCATION
('EdTech Curriculum Designer', 'SkillBridge Demo', 'Creating engaging content for vocational training platforms.', 'Uttar Pradesh', 'Noida', 'full_time', 'remote', 'education', 
 ARRAY['Technical Documentation Reading', 'Humor & Social Influence', 'Prompt Engineering'], 45000, 80000, 2, true);

-- Verify the insertion
SELECT category, count(*) FROM job_listings GROUP BY category;
