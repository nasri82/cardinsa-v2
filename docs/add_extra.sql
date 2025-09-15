-- =============================================
-- 4. CREATE PERFORMANCE INDEXES (SAFE)
-- =============================================

-- Create indexes only if they don't exist
DO $
BEGIN
    -- Policy Cancellations
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_policy_cancellations_policy_id') THEN
        CREATE INDEX idx_policy_cancellations_policy_id ON policy_cancellations(policy_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_policy_cancellations_status') THEN
        CREATE INDEX idx_policy_cancellations_status ON policy_cancellations(status);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_policy_cancellations_effective_date') THEN
        CREATE INDEX idx_policy_cancellations_effective_date ON policy_cancellations(effective_date);
    END IF;

    -- Member Benefit Usage
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_member_benefit_usage_member_policy') THEN
        CREATE INDEX idx_member_benefit_usage_member_policy ON member_benefit_usage(member_id, policy_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_member_benefit_usage_benefit_type') THEN
        CREATE INDEX idx_member_benefit_usage_benefit_type ON member_benefit_usage(benefit_type);
    END IF;
    
    IF NOT EXISTS-- =============================================
-- 🎯 FINAL MISSING TABLES FOR PRODUCTION
-- Lock Phase - Complete Schema
-- =============================================

-- Check and fix existing table constraints if needed
-- First check if primary key exists, if not add it
DO $
BEGIN
    -- Check if primary key constraint exists
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_type = 'PRIMARY KEY' 
        AND table_name = 'premium_invoices' 
        AND table_schema = 'public'
    ) THEN
        ALTER TABLE premium_invoices ADD CONSTRAINT premium_invoices_pkey PRIMARY KEY (id);
    END IF;
END $;

-- =============================================
-- 1. CRITICAL OPERATIONAL TABLES
-- =============================================

-- A. Policy Cancellations (REGULATORY REQUIREMENT)
CREATE TABLE policy_cancellations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID NOT NULL REFERENCES policies(id),
    cancellation_type VARCHAR(50) NOT NULL,
    requested_date DATE NOT NULL,
    effective_date DATE NOT NULL,
    cancellation_reason TEXT NOT NULL,
    refund_amount NUMERIC(15,2) DEFAULT 0,
    status VARCHAR(30) DEFAULT 'requested',
    approved_by UUID REFERENCES users(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    
    CONSTRAINT valid_cancellation_type CHECK (cancellation_type IN 
        ('member_request', 'non_payment', 'fraud', 'regulatory', 'underwriting_decline'))
);

-- B. Member Benefit Usage Tracking (CORE BUSINESS LOGIC)
CREATE TABLE member_benefit_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    policy_id UUID NOT NULL REFERENCES policies(id) ON DELETE CASCADE,
    plan_id UUID NOT NULL REFERENCES plans(id),
    
    benefit_type VARCHAR(100) NOT NULL,
    period_type VARCHAR(20) DEFAULT 'annual',
    period_start_date DATE NOT NULL,
    period_end_date DATE NOT NULL,
    
    benefit_limit NUMERIC(15,2) NOT NULL,
    used_amount NUMERIC(15,2) DEFAULT 0,
    remaining_amount NUMERIC(15,2) NOT NULL,
    
    benefit_count_limit INTEGER,
    used_count INTEGER DEFAULT 0,
    remaining_count INTEGER,
    
    utilization_percentage NUMERIC(5,2) GENERATED ALWAYS AS (
        CASE WHEN benefit_limit > 0 THEN (used_amount / benefit_limit * 100) ELSE 0 END
    ) STORED,
    
    is_exhausted BOOLEAN DEFAULT FALSE,
    last_used_date DATE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_member_benefit_period UNIQUE(member_id, policy_id, benefit_type, period_start_date, period_type)
);

-- C. Benefit Alert Logs (MEMBER COMMUNICATION)
CREATE TABLE benefit_alert_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_benefit_usage_id UUID NOT NULL REFERENCES member_benefit_usage(id) ON DELETE CASCADE,
    member_id UUID NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    
    alert_type VARCHAR(50) NOT NULL,
    threshold_percentage NUMERIC(5,2),
    alert_message TEXT NOT NULL,
    alert_message_ar TEXT,
    
    delivery_channels VARCHAR(100)[],
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    email_sent BOOLEAN DEFAULT FALSE,
    sms_sent BOOLEAN DEFAULT FALSE,
    
    member_acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    
    alert_status VARCHAR(30) DEFAULT 'pending',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID
);

-- D. Claim Action Logs (DETAILED AUDIT TRAIL)
CREATE TABLE claim_action_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_id UUID NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    
    action_type VARCHAR(50) NOT NULL,
    action_description TEXT NOT NULL,
    previous_status VARCHAR(50),
    new_status VARCHAR(50),
    
    previous_amount NUMERIC(15,2),
    new_amount NUMERIC(15,2),
    
    supporting_documents JSONB,
    internal_notes TEXT,
    member_visible_notes TEXT,
    
    requires_approval BOOLEAN DEFAULT FALSE,
    approved_by UUID REFERENCES users(id),
    
    action_taken_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    action_taken_by UUID NOT NULL REFERENCES users(id),
    
    CONSTRAINT valid_action_type CHECK (action_type IN 
        ('status_change', 'amount_adjustment', 'document_added', 'approval_granted', 
         'approval_denied', 'fraud_flag_added', 'payment_processed'))
);

-- =============================================
-- 2. SYSTEM CONFIGURATION TABLES
-- =============================================

-- A. System Feature Flags
CREATE TABLE system_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    flag_name VARCHAR(100) NOT NULL UNIQUE,
    flag_category VARCHAR(50) NOT NULL,
    
    is_enabled BOOLEAN DEFAULT FALSE,
    flag_value JSONB,
    description TEXT NOT NULL,
    
    company_id UUID REFERENCES companies(id),
    environment VARCHAR(20) DEFAULT 'production',
    rollout_percentage NUMERIC(5,2) DEFAULT 100.00,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- B. Collections Management
CREATE TABLE collections_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID NOT NULL REFERENCES policies(id) ON DELETE CASCADE,
    invoice_number VARCHAR(30),
    member_id UUID NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    
    collection_stage VARCHAR(50) NOT NULL,
    days_overdue INTEGER NOT NULL,
    outstanding_amount NUMERIC(15,2) NOT NULL,
    
    action_type VARCHAR(50) NOT NULL,
    communication_channel VARCHAR(30),
    
    communication_sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    member_responded BOOLEAN DEFAULT FALSE,
    response_type VARCHAR(30),
    
    payment_received BOOLEAN DEFAULT FALSE,
    payment_amount NUMERIC(15,2),
    payment_date DATE,
    
    next_action_date DATE,
    collection_status VARCHAR(30) DEFAULT 'active',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    
    CONSTRAINT valid_collection_stage CHECK (collection_stage IN 
        ('first_reminder', 'second_reminder', 'final_notice', 'legal_action'))
);

-- C. Policy Flags for Compliance
CREATE TABLE policy_flags (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID NOT NULL REFERENCES policies(id) ON DELETE CASCADE,
    
    flag_type VARCHAR(50) NOT NULL,
    flag_severity VARCHAR(20) DEFAULT 'info',
    flag_reason TEXT NOT NULL,
    
    effective_date DATE DEFAULT CURRENT_DATE,
    expiry_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    
    blocks_renewals BOOLEAN DEFAULT FALSE,
    blocks_endorsements BOOLEAN DEFAULT FALSE,
    blocks_claims BOOLEAN DEFAULT FALSE,
    requires_manager_approval BOOLEAN DEFAULT FALSE,
    
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID REFERENCES users(id),
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    
    CONSTRAINT valid_flag_type CHECK (flag_type IN 
        ('compliance_review', 'fraud_investigation', 'payment_default', 'high_risk',
         'regulatory_hold', 'vip_member', 'subsidized_policy')),
    CONSTRAINT valid_severity CHECK (flag_severity IN ('info', 'warning', 'critical', 'blocker'))
);

-- =============================================
-- 3. MISSING BUSINESS TABLES
-- =============================================

-- A. Claim Workflow Enhancement
CREATE TABLE claim_checklists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_type VARCHAR(50) NOT NULL,
    checklist_item TEXT NOT NULL,
    is_mandatory BOOLEAN DEFAULT TRUE,
    display_order INTEGER DEFAULT 0,
    description TEXT,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE claim_approvers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    claim_type VARCHAR(50) NOT NULL,
    min_amount NUMERIC(15,2) DEFAULT 0,
    max_amount NUMERIC(15,2),
    approver_role VARCHAR(50) NOT NULL,
    approval_level INTEGER DEFAULT 1,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- B. Broker/Agency Management (Missing from your schema)
CREATE TABLE brokers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    broker_code VARCHAR(50) UNIQUE NOT NULL,
    broker_name VARCHAR(200) NOT NULL,
    contact_person VARCHAR(150),
    email VARCHAR(150),
    phone VARCHAR(50),
    address TEXT,
    
    license_number VARCHAR(100),
    license_expiry DATE,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

CREATE TABLE broker_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    broker_id UUID NOT NULL REFERENCES brokers(id),
    company_id UUID REFERENCES companies(id),
    group_id UUID REFERENCES groups(id),
    policy_id UUID REFERENCES policies(id),
    
    assignment_type VARCHAR(50) NOT NULL, -- company, group, policy
    effective_date DATE DEFAULT CURRENT_DATE,
    expiry_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- C. Corporate Delegates (HR Contacts)
CREATE TABLE delegates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID NOT NULL REFERENCES companies(id),
    group_id UUID REFERENCES groups(id),
    
    delegate_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(50),
    position VARCHAR(100),
    department VARCHAR(100),
    
    permissions JSONB, -- What they can do
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- D. Document Templates (TOB, Certificates, etc.)
CREATE TABLE document_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name VARCHAR(200) NOT NULL,
    template_type VARCHAR(50) NOT NULL, -- tob, certificate, policy, endorsement
    template_category VARCHAR(50),
    
    template_content TEXT, -- HTML/Template content
    template_variables JSONB, -- Available placeholders
    
    company_id UUID REFERENCES companies(id), -- NULL = global template
    language_code VARCHAR(5) DEFAULT 'en',
    
    is_active BOOLEAN DEFAULT TRUE,
    version VARCHAR(20) DEFAULT '1.0',
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id),
    updated_by UUID REFERENCES users(id)
);

-- E. User Preferences (Member Portal)
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    member_id UUID REFERENCES members(id), -- For member portal preferences
    
    preference_category VARCHAR(50) NOT NULL,
    preference_key VARCHAR(100) NOT NULL,
    preference_value JSONB NOT NULL,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure only one of user_id or member_id is set
    CONSTRAINT check_user_or_member CHECK (
        (user_id IS NOT NULL AND member_id IS NULL) OR 
        (user_id IS NULL AND member_id IS NOT NULL)
    )
);

-- Create separate unique indexes for user and member preferences
CREATE UNIQUE INDEX idx_user_preferences_user 
ON user_preferences(user_id, preference_category, preference_key) 
WHERE user_id IS NOT NULL;

CREATE UNIQUE INDEX idx_user_preferences_member 
ON user_preferences(member_id, preference_category, preference_key) 
WHERE member_id IS NOT NULL;

-- F. AI Task Templates
CREATE TABLE ai_task_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_name VARCHAR(200) NOT NULL,
    task_type VARCHAR(50) NOT NULL, -- ocr, summarization, classification, fraud_detection
    
    prompt_template TEXT NOT NULL,
    model_parameters JSONB,
    expected_output_format JSONB,
    
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INTEGER DEFAULT 0,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id)
);

-- =============================================
-- 4. CREATE PERFORMANCE INDEXES (SAFE)
-- =============================================

-- Create indexes only if they don't exist
DO $
BEGIN
    -- Policy Cancellations
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_policy_cancellations_policy_id') THEN
        CREATE INDEX idx_policy_cancellations_policy_id ON policy_cancellations(policy_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_policy_cancellations_status') THEN
        CREATE INDEX idx_policy_cancellations_status ON policy_cancellations(status);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_policy_cancellations_effective_date') THEN
        CREATE INDEX idx_policy_cancellations_effective_date ON policy_cancellations(effective_date);
    END IF;

    -- Member Benefit Usage
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_member_benefit_usage_member_policy') THEN
        CREATE INDEX idx_member_benefit_usage_member_policy ON member_benefit_usage(member_id, policy_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_member_benefit_usage_benefit_type') THEN
        CREATE INDEX idx_member_benefit_usage_benefit_type ON member_benefit_usage(benefit_type);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_member_benefit_usage_exhausted') THEN
        CREATE INDEX idx_member_benefit_usage_exhausted ON member_benefit_usage(is_exhausted) WHERE is_exhausted = TRUE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_member_benefit_usage_utilization') THEN
        CREATE INDEX idx_member_benefit_usage_utilization ON member_benefit_usage(utilization_percentage DESC);
    END IF;

    -- Benefit Alert Logs
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_benefit_alert_logs_member_id') THEN
        CREATE INDEX idx_benefit_alert_logs_member_id ON benefit_alert_logs(member_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_benefit_alert_logs_sent_at') THEN
        CREATE INDEX idx_benefit_alert_logs_sent_at ON benefit_alert_logs(sent_at DESC);
    END IF;

    -- Claim Action Logs
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_claim_action_logs_claim_id') THEN
        CREATE INDEX idx_claim_action_logs_claim_id ON claim_action_logs(claim_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_claim_action_logs_taken_at') THEN
        CREATE INDEX idx_claim_action_logs_taken_at ON claim_action_logs(action_taken_at DESC);
    END IF;

    -- System Flags
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_system_flags_enabled') THEN
        CREATE INDEX idx_system_flags_enabled ON system_flags(is_enabled) WHERE is_enabled = TRUE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_system_flags_company') THEN
        CREATE INDEX idx_system_flags_company ON system_flags(company_id);
    END IF;

    -- Collections Logs
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_collections_logs_policy_id') THEN
        CREATE INDEX idx_collections_logs_policy_id ON collections_logs(policy_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_collections_logs_status') THEN
        CREATE INDEX idx_collections_logs_status ON collections_logs(collection_status);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_collections_logs_overdue') THEN
        CREATE INDEX idx_collections_logs_overdue ON collections_logs(days_overdue DESC);
    END IF;

    -- Policy Flags
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_policy_flags_policy_id') THEN
        CREATE INDEX idx_policy_flags_policy_id ON policy_flags(policy_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_policy_flags_active') THEN
        CREATE INDEX idx_policy_flags_active ON policy_flags(is_active) WHERE is_active = TRUE;
    END IF;

    -- Brokers
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_brokers_active') THEN
        CREATE INDEX idx_brokers_active ON brokers(is_active) WHERE is_active = TRUE;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_broker_assignments_broker') THEN
        CREATE INDEX idx_broker_assignments_broker ON broker_assignments(broker_id);
    END IF;

    -- Delegates
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_delegates_company') THEN
        CREATE INDEX idx_delegates_company ON delegates(company_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_delegates_active') THEN
        CREATE INDEX idx_delegates_active ON delegates(is_active) WHERE is_active = TRUE;
    END IF;
END $;

-- Create separate unique indexes for user preferences (safe)
DO $
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_user_preferences_user') THEN
        CREATE UNIQUE INDEX idx_user_preferences_user 
        ON user_preferences(user_id, preference_category, preference_key) 
        WHERE user_id IS NOT NULL;
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_indexes WHERE indexname = 'idx_user_preferences_member') THEN
        CREATE UNIQUE INDEX idx_user_preferences_member 
        ON user_preferences(member_id, preference_category, preference_key) 
        WHERE member_id IS NOT NULL;
    END IF;
END $;

-- =============================================
-- 5. CREATE ESSENTIAL VIEWS (SAFE)
-- =============================================

-- Create views only if they don't exist
DO $
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.views WHERE table_name = 'v_member_benefit_summary') THEN
        EXECUTE 'CREATE VIEW v_member_benefit_summary AS
        SELECT 
            mbu.member_id,
            m.full_name as member_name,
            mbu.policy_id,
            p.policy_number,
            COUNT(*) as total_benefits,
            COUNT(*) FILTER (WHERE mbu.utilization_percentage >= 80) as benefits_near_limit,
            COUNT(*) FILTER (WHERE mbu.is_exhausted = TRUE) as exhausted_benefits,
            SUM(mbu.used_amount) as total_used_amount,
            SUM(mbu.remaining_amount) as total_remaining_amount,
            AVG(mbu.utilization_percentage) as avg_utilization
        FROM member_benefit_usage mbu
        JOIN members m ON mbu.member_id = m.id
        JOIN policies p ON mbu.policy_id = p.id
        GROUP BY mbu.member_id, m.full_name, mbu.policy_id, p.policy_number';
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM information_schema.views WHERE table_name = 'v_active_policy_flags') THEN
        EXECUTE 'CREATE VIEW v_active_policy_flags AS
        SELECT 
            pf.*,
            p.policy_number,
            m.full_name as member_name,
            c.name as company_name
        FROM policy_flags pf
        JOIN policies p ON pf.policy_id = p.id
        JOIN members m ON p.member_id = m.id
        JOIN companies c ON p.company_id = c.id
        WHERE pf.is_active = TRUE 
          AND (pf.expiry_date IS NULL OR pf.expiry_date >= CURRENT_DATE)';
    END IF;
END $;

-- =============================================
-- 6. INSERT ESSENTIAL SEED DATA (SAFE)
-- =============================================

-- Insert system flags only if they don't exist
INSERT INTO system_flags (flag_name, flag_category, description, is_enabled, created_by) 
SELECT 'enable_ai_fraud_detection', 'ai', 'Enable AI-powered fraud detection for claims', TRUE, u.id
FROM users u 
WHERE NOT EXISTS (SELECT 1 FROM system_flags WHERE flag_name = 'enable_ai_fraud_detection')
LIMIT 1;

INSERT INTO system_flags (flag_name, flag_category, description, is_enabled, created_by) 
SELECT 'enable_benefit_alerts', 'feature', 'Enable automatic benefit utilization alerts', TRUE, u.id
FROM users u 
WHERE NOT EXISTS (SELECT 1 FROM system_flags WHERE flag_name = 'enable_benefit_alerts')
LIMIT 1;

INSERT INTO system_flags (flag_name, flag_category, description, is_enabled, created_by) 
SELECT 'enable_auto_renewals', 'feature', 'Enable automatic policy renewals', TRUE, u.id
FROM users u 
WHERE NOT EXISTS (SELECT 1 FROM system_flags WHERE flag_name = 'enable_auto_renewals')
LIMIT 1;

INSERT INTO system_flags (flag_name, flag_category, description, is_enabled, created_by) 
SELECT 'maintenance_mode', 'system', 'Put system in maintenance mode', FALSE, u.id
FROM users u 
WHERE NOT EXISTS (SELECT 1 FROM system_flags WHERE flag_name = 'maintenance_mode')
LIMIT 1;

INSERT INTO system_flags (flag_name, flag_category, description, is_enabled, created_by) 
SELECT 'enable_real_time_pricing', 'pricing', 'Enable real-time pricing calculations', TRUE, u.id
FROM users u 
WHERE NOT EXISTS (SELECT 1 FROM system_flags WHERE flag_name = 'enable_real_time_pricing')
LIMIT 1;

-- Insert claim checklist items (safe)
INSERT INTO claim_checklists (claim_type, checklist_item, is_mandatory, display_order) 
SELECT * FROM (VALUES
    ('medical', 'Medical report from treating physician', TRUE, 1),
    ('medical', 'Prescription receipts', TRUE, 2),
    ('medical', 'Hospital discharge summary (if applicable)', FALSE, 3),
    ('medical', 'Lab test results', FALSE, 4),
    ('dental', 'Dental treatment plan', TRUE, 1),
    ('dental', 'X-rays or imaging', FALSE, 2),
    ('maternity', 'Birth certificate', TRUE, 1),
    ('maternity', 'Hospital bills', TRUE, 2),
    ('maternity', 'Prenatal care records', FALSE, 3)
) AS v(claim_type, checklist_item, is_mandatory, display_order)
WHERE NOT EXISTS (
    SELECT 1 FROM claim_checklists cc 
    WHERE cc.claim_type = v.claim_type 
    AND cc.checklist_item = v.checklist_item
);

-- Insert claim approvers (safe)
INSERT INTO claim_approvers (claim_type, min_amount, max_amount, approver_role, approval_level) 
SELECT * FROM (VALUES
    ('medical', 0, 1000, 'claims_officer', 1),
    ('medical', 1000, 5000, 'senior_claims_officer', 2),
    ('medical', 5000, NULL, 'claims_manager', 3),
    ('dental', 0, 500, 'claims_officer', 1),
    ('dental', 500, NULL, 'senior_claims_officer', 2),
    ('maternity', 0, 2000, 'claims_officer', 1),
    ('maternity', 2000, NULL, 'claims_manager', 2)
) AS v(claim_type, min_amount, max_amount, approver_role, approval_level)
WHERE NOT EXISTS (
    SELECT 1 FROM claim_approvers ca 
    WHERE ca.claim_type = v.claim_type 
    AND ca.approver_role = v.approver_role
    AND ca.approval_level = v.approval_level
);

-- Insert document templates (safe)
INSERT INTO document_templates (template_name, template_type, template_category, language_code, created_by) 
SELECT template_name, template_type, template_category, language_code, u.id
FROM (VALUES
    ('Standard Policy Certificate', 'certificate', 'policy', 'en'),
    ('Table of Benefits - Medical', 'tob', 'medical', 'en'),
    ('Table of Benefits - Medical (Arabic)', 'tob', 'medical', 'ar'),
    ('Policy Endorsement Letter', 'endorsement', 'policy', 'en'),
    ('Claims Settlement Letter', 'letter', 'claims', 'en'),
    ('Welcome Letter - New Member', 'letter', 'onboarding', 'en')
) AS v(template_name, template_type, template_category, language_code)
CROSS JOIN (SELECT id FROM users LIMIT 1) u
WHERE NOT EXISTS (
    SELECT 1 FROM document_templates dt 
    WHERE dt.template_name = v.template_name 
    AND dt.language_code = v.language_code
);

-- Insert AI task templates (safe)
INSERT INTO ai_task_templates (template_name, task_type, prompt_template, created_by) 
SELECT template_name, task_type, prompt_template, u.id
FROM (VALUES
    ('Medical Document OCR', 'ocr', 'Extract all text from this medical document. Focus on: patient name, date, diagnosis, treatment, costs.'),
    ('Claim Fraud Detection', 'fraud_detection', 'Analyze this claim for potential fraud indicators. Consider: timing, amounts, provider history, member behavior.'),
    ('Policy Summarization', 'summarization', 'Create a 2-paragraph summary of this insurance policy highlighting key benefits and exclusions.'),
    ('Risk Assessment', 'classification', 'Assess the risk level (LOW/MEDIUM/HIGH) of this insurance application based on provided information.')
) AS v(template_name, task_type, prompt_template)
CROSS JOIN (SELECT id FROM users LIMIT 1) u
WHERE NOT EXISTS (
    SELECT 1 FROM ai_task_templates att 
    WHERE att.template_name = v.template_name
);

-- Add helpful comments
COMMENT ON TABLE policy_cancellations IS 'Tracks all policy cancellation requests and processing workflow';
COMMENT ON TABLE member_benefit_usage IS 'Real-time tracking of member benefit utilization against limits';
COMMENT ON TABLE benefit_alert_logs IS 'Log of all benefit-related alerts sent to members';
COMMENT ON TABLE claim_action_logs IS 'Detailed audit trail of all claim processing actions';
COMMENT ON TABLE system_flags IS 'Feature flags and system configuration for operational control';
COMMENT ON TABLE collections_logs IS 'Payment collection activities and member follow-up tracking';
COMMENT ON TABLE policy_flags IS 'Special compliance and operational flags on policies';
COMMENT ON TABLE brokers IS 'Insurance broker/agent master data';
COMMENT ON TABLE delegates IS 'Corporate HR delegates authorized to manage group policies';
COMMENT ON TABLE document_templates IS 'Templates for generating insurance documents and certificates';
COMMENT ON TABLE user_preferences IS 'User and member portal preference settings';
COMMENT ON TABLE ai_task_templates IS 'Reusable AI task templates for automation workflows';