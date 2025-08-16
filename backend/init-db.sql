-- =============================================================================
-- HRMS-SAAS Database Initialization Script
-- =============================================================================

-- Create the main database if it doesn't exist
-- This script assumes the database 'hrms_main' already exists

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS public;
CREATE SCHEMA IF NOT EXISTS hrms_shared;

-- Set search path
SET search_path TO public, hrms_shared;

-- Create base tables in public schema (tenant management)
CREATE TABLE IF NOT EXISTS public.tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(100) UNIQUE NOT NULL,
    domain VARCHAR(255),
    subdomain VARCHAR(100),
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(50),
    contact_address TEXT,
    company_name VARCHAR(255),
    industry VARCHAR(100),
    company_size VARCHAR(50),
    founded_year INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    plan VARCHAR(20) DEFAULT 'free',
    subscription_start_date TIMESTAMP WITH TIME ZONE,
    subscription_end_date TIMESTAMP WITH TIME ZONE,
    trial_end_date TIMESTAMP WITH TIME ZONE,
    max_users INTEGER DEFAULT 10,
    max_storage_gb INTEGER DEFAULT 5,
    max_projects INTEGER DEFAULT 5,
    timezone VARCHAR(50) DEFAULT 'UTC',
    locale VARCHAR(10) DEFAULT 'en_US',
    currency VARCHAR(3) DEFAULT 'USD',
    features_enabled JSONB DEFAULT '{}',
    settings JSONB DEFAULT '{}',
    logo_url VARCHAR(500),
    primary_color VARCHAR(7),
    secondary_color VARCHAR(7),
    webhook_url VARCHAR(500),
    api_key VARCHAR(255),
    billing_email VARCHAR(255),
    billing_address TEXT,
    tax_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    created_by VARCHAR(255),
    updated_by VARCHAR(255),
    deleted_by VARCHAR(255)
);

-- Create indexes for tenants
CREATE INDEX IF NOT EXISTS idx_tenants_slug ON public.tenants(slug);
CREATE INDEX IF NOT EXISTS idx_tenants_domain ON public.tenants(domain);
CREATE INDEX IF NOT EXISTS idx_tenants_subdomain ON public.tenants(subdomain);
CREATE INDEX IF NOT EXISTS idx_tenants_status ON public.tenants(status);
CREATE INDEX IF NOT EXISTS idx_tenants_plan ON public.tenants(plan);

-- Create system roles table in public schema
CREATE TABLE IF NOT EXISTS public.system_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    display_name VARCHAR(100) NOT NULL,
    permissions JSONB DEFAULT '{}',
    is_system_role BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    priority INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create system users table in public schema
CREATE TABLE IF NOT EXISTS public.system_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    user_type VARCHAR(20) DEFAULT 'super_admin',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create system user roles table
CREATE TABLE IF NOT EXISTS public.system_user_roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES public.system_users(id) ON DELETE CASCADE,
    role_id UUID REFERENCES public.system_roles(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, role_id)
);

-- Insert default system roles
INSERT INTO public.system_roles (name, description, display_name, permissions, is_default, priority) VALUES
('super_admin', 'Super Administrator with full system access', 'Super Administrator', 
 '{"*": true}', TRUE, 100),
('system_admin', 'System Administrator with limited system access', 'System Administrator',
 '{"tenant_management": true, "user_management": true, "system_config": true}', FALSE, 90),
('tenant_admin', 'Tenant Administrator with full tenant access', 'Tenant Administrator',
 '{"tenant_management": true, "user_management": true, "hr_management": true}', FALSE, 80)
ON CONFLICT (name) DO NOTHING;

-- Create default super admin user (password: admin123)
INSERT INTO public.system_users (username, email, first_name, last_name, hashed_password, user_type) VALUES
('admin', 'admin@hrms-saas.com', 'System', 'Administrator', 
 '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj3ZxQQxq6re', 'super_admin')
ON CONFLICT (username) DO NOTHING;

-- Assign super admin role to admin user
INSERT INTO public.system_user_roles (user_id, role_id)
SELECT u.id, r.id 
FROM public.system_users u, public.system_roles r 
WHERE u.username = 'admin' AND r.name = 'super_admin'
ON CONFLICT DO NOTHING;

-- Create audit log table
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id VARCHAR(100),
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for audit logs
CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant_id ON public.audit_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at);

-- Create system configuration table
CREATE TABLE IF NOT EXISTS public.system_config (
    key VARCHAR(255) PRIMARY KEY,
    value JSONB NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default system configuration
INSERT INTO public.system_config (key, value, description, is_public) VALUES
('default_tenant_features', 
 '{"employee_management": true, "leave_management": true, "payroll": false, "recruitment": false, "performance": false}',
 'Default features enabled for new tenants', FALSE),
('system_settings',
 '{"max_tenants": 1000, "default_plan": "free", "trial_days": 30, "max_file_size_mb": 10}',
 'System-wide configuration settings', FALSE),
('email_templates',
 '{"welcome": "Welcome to HRMS-SAAS!", "password_reset": "Reset your password", "invitation": "You are invited to join"}',
 'Default email templates', FALSE)
ON CONFLICT (key) DO NOTHING;

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON public.tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_roles_updated_at BEFORE UPDATE ON public.system_roles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_users_updated_at BEFORE UPDATE ON public.system_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON public.system_config
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create function to create tenant schema
CREATE OR REPLACE FUNCTION create_tenant_schema(tenant_slug VARCHAR)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', tenant_slug);
    
    -- Create tenant-specific tables in the new schema
    EXECUTE format('
        CREATE TABLE IF NOT EXISTS %I.users (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN DEFAULT TRUE,
            is_verified BOOLEAN DEFAULT FALSE,
            user_type VARCHAR(20) DEFAULT ''employee'',
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        )
    ', tenant_slug);
    
    EXECUTE format('
        CREATE INDEX IF NOT EXISTS idx_%I_users_username ON %I.users(username)
    ', tenant_slug, tenant_slug);
    
    EXECUTE format('
        CREATE INDEX IF NOT EXISTS idx_%I_users_email ON %I.users(email)
    ', tenant_slug, tenant_slug);
    
    -- Add more tenant-specific tables as needed
    
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA public TO hrms_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO hrms_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO hrms_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO hrms_user;

-- Create a default tenant for testing
INSERT INTO public.tenants (name, slug, contact_email, company_name, status, plan) VALUES
('Demo Company', 'demo', 'admin@demo.com', 'Demo Company Inc.', 'active', 'professional')
ON CONFLICT (slug) DO NOTHING;

-- Create demo tenant schema
SELECT create_tenant_schema('demo');

-- Print completion message
DO $$
BEGIN
    RAISE NOTICE 'HRMS-SAAS database initialization completed successfully!';
    RAISE NOTICE 'Default admin user: admin / admin123';
    RAISE NOTICE 'Demo tenant created with slug: demo';
END $$;
