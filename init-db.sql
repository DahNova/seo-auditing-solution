-- Initialize database with required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create database if not exists (this will be automatically handled by postgres image)
-- The database 'seo_auditing' is created via POSTGRES_DB environment variable

-- Grant all privileges to user
GRANT ALL PRIVILEGES ON DATABASE seo_auditing TO seo_user;