-- Techno Bucket Database Seed Data
-- Run this after schema.sql to populate with sample data

USE technobucket;

-- ============================================
-- SAMPLE PORTFOLIO ORDERS
-- ============================================
INSERT INTO portfolio_orders (
    full_name, 
    email, 
    phone,
    github_profile, 
    leetcode_profile, 
    linkedin_profile, 
    skills, 
    project_links, 
    extra_information,
    status,
    amount_paid,
    payment_status
) VALUES 
(
    'John Doe',
    'john.doe@example.com',
    '+91 98765 43210',
    'https://github.com/johndoe',
    'https://leetcode.com/johndoe',
    'https://linkedin.com/in/johndoe',
    '["React", "TypeScript", "Node.js", "MongoDB", "Python"]',
    '["https://johndoe-portfolio.vercel.app", "https://github.com/johndoe/ecommerce-app"]',
    'Won 2nd place in Smart India Hackathon 2024.\n\nInterned at TechCorp for 3 months as a Full Stack Developer.\n\nActive member of the college coding club.',
    'in-progress',
    299.00,
    'paid'
),
(
    'Jane Smith',
    'jane.smith@example.com',
    '+91 87654 32109',
    'https://github.com/janesmith',
    'https://leetcode.com/janesmith',
    'https://linkedin.com/in/janesmith',
    '["Python", "Machine Learning", "TensorFlow", "Pandas", "SQL"]',
    '["https://janesmith-ml.vercel.app", "https://github.com/janesmith/stock-predictor"]',
    'Participated in Google Summer of Code 2024.\n\nResearch intern at IIT Delhi working on NLP projects.\n\nPublished 2 papers on sentiment analysis.',
    'pending',
    299.00,
    'pending'
),
(
    'Rahul Kumar',
    'rahul.kumar@example.com',
    '+91 76543 21098',
    'https://github.com/rahulk',
    'https://leetcode.com/rahulk',
    'https://linkedin.com/in/rahulk',
    '["Java", "Spring Boot", "MySQL", "AWS", "Docker"]',
    '["https://rahulk.dev", "https://github.com/rahulk/microservices"]',
    '2 years experience at Infosys as Software Engineer.\n\nAWS Certified Solutions Architect.\n\nOrganized college tech fest for 2 consecutive years.',
    'completed',
    299.00,
    'paid'
);

-- ============================================
-- SAMPLE FILES FOR ORDERS
-- ============================================
INSERT INTO portfolio_files (order_id, file_type, original_filename, stored_filename, file_path, file_size, mime_type) VALUES
-- Order 1 files
(1, 'resume', 'John_Doe_Resume.pdf', 'resume_1_1699123456.pdf', '/uploads/orders/1/resume_1_1699123456.pdf', 245760, 'application/pdf'),
(1, 'profile_image', 'john_profile.jpg', 'profile_1_1699123457.jpg', '/uploads/orders/1/profile_1_1699123457.jpg', 102400, 'image/jpeg'),
(1, 'certificate', 'SIH_Certificate.pdf', 'cert_1_1699123458.pdf', '/uploads/orders/1/cert_1_1699123458.pdf', 51200, 'application/pdf'),

-- Order 2 files
(2, 'resume', 'Jane_Smith_CV.pdf', 'resume_2_1699123460.pdf', '/uploads/orders/2/resume_2_1699123460.pdf', 198000, 'application/pdf'),
(2, 'profile_image', 'jane_photo.png', 'profile_2_1699123461.png', '/uploads/orders/2/profile_2_1699123461.png', 204800, 'image/png'),

-- Order 3 files
(3, 'resume', 'Rahul_Kumar_Resume.pdf', 'resume_3_1699123470.pdf', '/uploads/orders/3/resume_3_1699123470.pdf', 320000, 'application/pdf'),
(3, 'profile_image', 'rahul_pic.jpg', 'profile_3_1699123471.jpg', '/uploads/orders/3/profile_3_1699123471.jpg', 153600, 'image/jpeg'),
(3, 'certificate', 'AWS_Certification.pdf', 'cert_3_1699123472.pdf', '/uploads/orders/3/cert_3_1699123472.pdf', 45000, 'application/pdf'),
(3, 'certificate', 'Infosys_Experience.pdf', 'cert_3_1699123473.pdf', '/uploads/orders/3/cert_3_1699123473.pdf', 38000, 'application/pdf');

-- ============================================
-- SAMPLE CONTACT INQUIRIES
-- ============================================
INSERT INTO contact_inquiries (name, email, service_id, service_name, message, status) VALUES
(
    'Alice Johnson',
    'alice@example.com',
    1,
    'ATS-Friendly Resume',
    'I need a professional resume for a software engineer position at a FAANG company. Please include all my projects and experience.',
    'new'
),
(
    'Bob Williams',
    'bob@example.com',
    5,
    'Complete Career Combo Pack',
    'I am a recent graduate looking for a complete package. Can you help me with resume, portfolio and LinkedIn profile?',
    'read'
),
(
    'Carol Davis',
    'carol@example.com',
    3,
    'Custom Project',
    'I need a custom e-commerce dashboard built with React and Node.js. Please contact me to discuss requirements.',
    'replied'
);

-- ============================================
-- SAMPLE ORDER NOTES
-- ============================================
INSERT INTO order_notes (order_id, admin_id, note, is_internal) VALUES
(1, 1, 'Client prefers blue color scheme for the portfolio. Discussed design preferences over email.', FALSE),
(1, 1, 'Resume needs some formatting fixes - spacing issues in the skills section.', TRUE),
(3, 1, 'Order completed successfully. Client is very happy with the result!', FALSE);

-- ============================================
-- UPDATE ORDER 3 COMPLETION DATE
-- ============================================
UPDATE portfolio_orders 
SET completed_at = DATE_SUB(NOW(), INTERVAL 2 DAY)
WHERE id = 3;

-- Verify data insertion
SELECT 'Portfolio Orders' as table_name, COUNT(*) as count FROM portfolio_orders
UNION ALL
SELECT 'Portfolio Files', COUNT(*) FROM portfolio_files
UNION ALL
SELECT 'Contact Inquiries', COUNT(*) FROM contact_inquiries
UNION ALL
SELECT 'Order Notes', COUNT(*) FROM order_notes
UNION ALL
SELECT 'Services', COUNT(*) FROM services
UNION ALL
SELECT 'Testimonials', COUNT(*) FROM testimonials;
