# Techno Bucket Database

This directory contains all database-related files for the Techno Bucket application.

## Files

| File | Description |
|------|-------------|
| `schema.sql` | Complete database schema with tables, indexes, views, procedures, and triggers |
| `seed.sql` | Sample data for development and testing |

## Database Schema Overview

### Core Tables

#### 1. `users`
Stores admin authentication data.
- Admin login credentials
- Role-based access control

#### 2. `services`
All services offered by Techno Bucket.
- ATS Resume (₹40)
- Portfolio Website (₹299)
- Custom Project (₹999)
- Profile Creation (₹149)
- Combo Pack (₹1,300)

#### 3. `portfolio_orders` ⭐ **Main Table**
Stores complete information from the portfolio order form.
**Fields:**
- `full_name` - Customer name
- `email` - Contact email
- `phone` - Phone number (optional)
- `github_profile` - GitHub URL
- `leetcode_profile` - LeetCode URL
- `linkedin_profile` - LinkedIn URL
- `skills` - JSON array of skills
- `project_links` - JSON array of project URLs
- `extra_information` - Hackathons, internships, experience, etc.
- `status` - pending/in-progress/completed/cancelled
- `amount_paid` - Payment amount
- `payment_status` - pending/paid/refunded

#### 4. `portfolio_files`
Stores uploaded file information.
- Resume (PDF)
- Profile Image
- Certificates (multiple)

#### 5. `contact_inquiries`
Stores contact form submissions.

#### 6. `order_notes`
Internal notes for admins on orders.

#### 7. `activity_logs`
Audit trail for all changes.

#### 8. `testimonials`
Customer testimonials displayed on the site.

## Setup Instructions

### Option 1: MySQL/MariaDB (Recommended for production)

```bash
# 1. Create database
mysql -u root -p < schema.sql

# 2. (Optional) Add sample data
mysql -u root -p technobucket < seed.sql
```

### Option 2: Using Docker

```bash
# Start MySQL container
docker run -d \
  --name technobucket-db \
  -e MYSQL_ROOT_PASSWORD=yourpassword \
  -e MYSQL_DATABASE=technobucket \
  -p 3306:3306 \
  mysql:8.0

# Copy and run schema
docker cp schema.sql technobucket-db:/schema.sql
docker exec technobucket-db mysql -u root -p'yourpassword' < schema.sql
```

## Common Queries

### Get all orders with file counts
```sql
SELECT * FROM vw_portfolio_orders_summary;
```

### Get daily statistics
```sql
SELECT * FROM vw_daily_stats LIMIT 30;
```

### Get order details with files
```sql
CALL sp_get_order_details(1);
```

### Update order status (with logging)
```sql
CALL sp_update_order_status(1, 'completed', 1);
```

### Get pending orders
```sql
SELECT * FROM portfolio_orders 
WHERE status = 'pending' 
ORDER BY created_at DESC;
```

## Admin Credentials

After running schema.sql:
- **Email**: admin@technobucket.com
- **Password**: bhargav (change in production!)

## Backup & Restore

```bash
# Backup
mysqldump -u root -p technobucket > backup.sql

# Restore
mysql -u root -p technobucket < backup.sql
```
