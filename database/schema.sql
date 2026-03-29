-- Techno Bucket Database Schema
-- Run these commands to set up the complete database

-- Create database
CREATE DATABASE IF NOT EXISTS technobucket;
USE technobucket;

-- ============================================
-- USERS TABLE (for admin authentication)
-- ============================================
CREATE TABLE users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'customer') DEFAULT 'customer',
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert default admin user
-- Password: bhargav (hashed)
INSERT INTO users (email, password_hash, role, name) VALUES 
('admin@technobucket.com', '$2y$10$YourHashedPasswordHere', 'admin', 'Techno Bucket Admin');

-- ============================================
-- SERVICES TABLE
-- ============================================
CREATE TABLE services (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    original_price DECIMAL(10, 2),
    features JSON,
    is_popular BOOLEAN DEFAULT FALSE,
    is_combo BOOLEAN DEFAULT FALSE,
    sort_order INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Insert services
INSERT INTO services (name, slug, description, price, features, is_popular) VALUES
('ATS-Friendly Resume', 'ats-resume', 'Get past the bots and land interviews with our professionally crafted, ATS-optimized resumes.', 40.00, '["ATS-Optimized Format", "Keyword Research", "Multiple Revisions", "PDF & Word Export"]', FALSE),

('Portfolio Website', 'portfolio-website', 'Showcase your work with a stunning, responsive portfolio website that impresses recruiters.', 299.00, '["Responsive Design", "Custom Domain Setup", "5 Pages Included", "Contact Form Integration"]', TRUE),

('Custom Project', 'custom-project', 'Need something unique? We build custom web applications, tools, and solutions tailored to your requirements.', 999.00, '["Full-Stack Development", "Modern Tech Stack", "Scalable Architecture", "3 Months Support"]', FALSE),

('Professional Profile Creation', 'profile-creation', 'Stand out on LinkedIn and other professional platforms with an optimized profile.', 149.00, '["LinkedIn Optimization", "Headline & Summary", "Skills Endorsement Strategy", "Profile Photo Tips"]', FALSE);

-- Insert combo pack
INSERT INTO services (name, slug, description, price, original_price, features, is_combo, is_popular) VALUES
('Complete Career Combo Pack', 'combo-pack', 'Get everything you need to launch your career! Includes all premium services at a special discounted price.', 1300.00, 1487.00, '["ATS-Friendly Resume (₹40)", "Portfolio Website (₹299)", "Professional Profile Creation (₹149)", "FREE Custom Project Consultation (₹999 value)", "Priority Support", "Save ₹368 (25% off)"]', TRUE, TRUE);

-- ============================================
-- PORTFOLIO ORDERS TABLE
-- Stores complete information from portfolio order form
-- ============================================
CREATE TABLE portfolio_orders (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    
    -- Personal Information
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    
    -- Profile Links (all mandatory)
    github_profile VARCHAR(500) NOT NULL,
    leetcode_profile VARCHAR(500) NOT NULL,
    linkedin_profile VARCHAR(500) NOT NULL,
    
    -- Skills (stored as JSON array)
    skills JSON NOT NULL,
    
    -- Project Links (stored as JSON array)
    project_links JSON NOT NULL,
    
    -- Extra Information
    extra_information TEXT,
    
    -- Order Status
    status ENUM('pending', 'in-progress', 'completed', 'cancelled') DEFAULT 'pending',
    
    -- Pricing
    amount_paid DECIMAL(10, 2) DEFAULT 299.00,
    payment_status ENUM('pending', 'paid', 'refunded') DEFAULT 'pending',
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    -- Index for faster queries
    INDEX idx_email (email),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- ============================================
-- FILES TABLE (for uploads)
-- ============================================
CREATE TABLE portfolio_files (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT UNSIGNED NOT NULL,
    file_type ENUM('resume', 'profile_image', 'certificate') NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    stored_filename VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size BIGINT UNSIGNED,
    mime_type VARCHAR(100),
    sort_order INT DEFAULT 0,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (order_id) REFERENCES portfolio_orders(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id),
    INDEX idx_file_type (file_type)
);

-- ============================================
-- CONTACT INQUIRIES TABLE
-- ============================================
CREATE TABLE contact_inquiries (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    service_id BIGINT UNSIGNED,
    service_name VARCHAR(255),
    message TEXT,
    status ENUM('new', 'read', 'replied', 'spam') DEFAULT 'new',
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE SET NULL,
    INDEX idx_email (email),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at)
);

-- ============================================
-- ORDER NOTES TABLE (for admin internal notes)
-- ============================================
CREATE TABLE order_notes (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT UNSIGNED NOT NULL,
    admin_id BIGINT UNSIGNED NOT NULL,
    note TEXT NOT NULL,
    is_internal BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (order_id) REFERENCES portfolio_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_order_id (order_id)
);

-- ============================================
-- ACTIVITY LOG TABLE
-- ============================================
CREATE TABLE activity_logs (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    entity_type ENUM('order', 'inquiry', 'user') NOT NULL,
    entity_id BIGINT UNSIGNED NOT NULL,
    action VARCHAR(100) NOT NULL,
    old_values JSON,
    new_values JSON,
    performed_by BIGINT UNSIGNED,
    performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_performed_at (performed_at)
);

-- ============================================
-- TESTIMONIALS TABLE
-- ============================================
CREATE TABLE testimonials (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    role VARCHAR(255),
    company VARCHAR(255),
    content TEXT NOT NULL,
    rating INT DEFAULT 5,
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    sort_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample testimonials
INSERT INTO testimonials (customer_name, role, company, content, is_featured) VALUES
('Rahul Sharma', 'Software Engineer', 'Google', 'Techno Bucket helped me create a stunning portfolio that got me noticed by top companies.', TRUE),
('Priya Patel', 'Product Manager', 'Microsoft', 'The ATS-friendly resume was a game changer. I started getting interview calls immediately!', TRUE),
('Amit Kumar', 'Data Scientist', 'Amazon', 'Best investment for my career. The combo pack gave me everything I needed.', TRUE);

-- ============================================
-- VIEWS FOR COMMON QUERIES
-- ============================================

-- View: Active orders with file counts
CREATE VIEW vw_portfolio_orders_summary AS
SELECT 
    po.id,
    po.full_name,
    po.email,
    po.status,
    po.created_at,
    COUNT(DISTINCT pf.id) as total_files,
    SUM(CASE WHEN pf.file_type = 'resume' THEN 1 ELSE 0 END) as resume_count,
    SUM(CASE WHEN pf.file_type = 'profile_image' THEN 1 ELSE 0 END) as profile_image_count,
    SUM(CASE WHEN pf.file_type = 'certificate' THEN 1 ELSE 0 END) as certificate_count
FROM portfolio_orders po
LEFT JOIN portfolio_files pf ON po.id = pf.order_id
GROUP BY po.id, po.full_name, po.email, po.status, po.created_at;

-- View: Daily order statistics
CREATE VIEW vw_daily_stats AS
SELECT 
    DATE(created_at) as date,
    COUNT(*) as total_orders,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_orders,
    SUM(CASE WHEN status = 'in-progress' THEN 1 ELSE 0 END) as in_progress_orders,
    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_orders
FROM portfolio_orders
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- ============================================
-- STORED PROCEDURES
-- ============================================

DELIMITER //

-- Procedure: Update order status with logging
CREATE PROCEDURE sp_update_order_status(
    IN p_order_id BIGINT UNSIGNED,
    IN p_new_status VARCHAR(50),
    IN p_admin_id BIGINT UNSIGNED
)
BEGIN
    DECLARE v_old_status VARCHAR(50);
    
    -- Get current status
    SELECT status INTO v_old_status FROM portfolio_orders WHERE id = p_order_id;
    
    -- Update status
    UPDATE portfolio_orders 
    SET status = p_new_status,
        completed_at = CASE WHEN p_new_status = 'completed' THEN NOW() ELSE completed_at END
    WHERE id = p_order_id;
    
    -- Log the activity
    INSERT INTO activity_logs (entity_type, entity_id, action, old_values, new_values, performed_by)
    VALUES ('order', p_order_id, 'status_changed', 
            JSON_OBJECT('status', v_old_status), 
            JSON_OBJECT('status', p_new_status), 
            p_admin_id);
END //

-- Procedure: Get order details with all files
CREATE PROCEDURE sp_get_order_details(IN p_order_id BIGINT UNSIGNED)
BEGIN
    SELECT 
        po.*,
        JSON_ARRAYAGG(
            JSON_OBJECT(
                'file_id', pf.id,
                'file_type', pf.file_type,
                'filename', pf.original_filename,
                'file_path', pf.file_path,
                'uploaded_at', pf.uploaded_at
            )
        ) as files
    FROM portfolio_orders po
    LEFT JOIN portfolio_files pf ON po.id = pf.order_id
    WHERE po.id = p_order_id
    GROUP BY po.id;
END //

DELIMITER ;

-- ============================================
-- TRIGGERS
-- ============================================

DELIMITER //

-- Trigger: Log when order is created
CREATE TRIGGER trg_order_created
AFTER INSERT ON portfolio_orders
FOR EACH ROW
BEGIN
    INSERT INTO activity_logs (entity_type, entity_id, action, new_values, performed_at)
    VALUES ('order', NEW.id, 'order_created', 
            JSON_OBJECT('email', NEW.email, 'name', NEW.full_name), 
            NOW());
END //

DELIMITER ;
