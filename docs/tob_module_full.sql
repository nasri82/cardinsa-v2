-- =============================================
-- 🚀 TOB MODULE ENHANCEMENTS FOR INSURANCE PLATFORM
-- Author: ChatGPT
-- Generated: 2025-09-02 07:26:26
-- Description: Full SQL for advanced Table of Benefits (TOB) module
-- =============================================

-- 1. Main TOB Table
CREATE TABLE plan_benefits (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES plans(id),
    coverage_id UUID NOT NULL REFERENCES coverages(id),
    category_id UUID REFERENCES benefit_categories(id),

    benefit_name TEXT NOT NULL,
    benefit_description TEXT,
    limit_amount NUMERIC(12,2),
    coinsurance_percent NUMERIC(5,2),
    deductible_amount NUMERIC(12,2),
    requires_preapproval BOOLEAN DEFAULT FALSE,
    is_optional BOOLEAN DEFAULT FALSE,
    network_tier TEXT,
    display_group TEXT,
    display_order INT DEFAULT 0,
    disclaimer TEXT,
    alert_threshold_percent NUMERIC(5,2),
    is_trackable BOOLEAN DEFAULT FALSE,
    ai_summary TEXT,
    vector_embedding VECTOR(384),

    remarks TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Benefit Categories Table
CREATE TABLE benefit_categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    display_order INT DEFAULT 0
);

-- 3. Multilingual Translations
CREATE TABLE benefit_translations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_benefit_id UUID REFERENCES plan_benefits(id),
    language_code TEXT NOT NULL,
    label TEXT,
    description TEXT
);

-- 4. Benefit Conditions Table
CREATE TABLE benefit_conditions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_benefit_id UUID REFERENCES plan_benefits(id),
    condition_type TEXT,
    condition_json JSONB,
    notes TEXT
);

-- 5. Benefit Documents Table
CREATE TABLE benefit_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_benefit_id UUID REFERENCES plan_benefits(id),
    document_type TEXT,
    file_url TEXT,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- 6. Benefit Versioning Table
CREATE TABLE plan_benefit_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_benefit_id UUID REFERENCES plan_benefits(id),
    version_number INT,
    changes_summary TEXT,
    updated_by UUID REFERENCES users(id),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 7. Plan Exclusions
CREATE TABLE plan_exclusions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID REFERENCES plans(id),
    exclusion_type TEXT,
    exclusion_text TEXT,
    applies_to_all_benefits BOOLEAN DEFAULT TRUE
);

-- 8. Preapproval Matrix
CREATE TABLE preapproval_matrix (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_benefit_id UUID REFERENCES plan_benefits(id),
    provider_type TEXT,
    threshold_amount NUMERIC,
    always_required BOOLEAN DEFAULT FALSE,
    notes TEXT
);

-- 9. Policy-Level Overrides
CREATE TABLE policy_benefit_overrides (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id UUID REFERENCES policies(id),
    plan_benefit_id UUID REFERENCES plan_benefits(id),
    override_limit_amount NUMERIC,
    override_coinsurance NUMERIC,
    override_notes TEXT,
    effective_date DATE
);

-- 10. Benefit Change Log
CREATE TABLE benefit_change_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_benefit_id UUID,
    changed_at TIMESTAMP DEFAULT NOW(),
    changed_by UUID REFERENCES users(id),
    change_type TEXT,
    change_data JSONB
);

-- 11. Member Benefit Usage Table
CREATE TABLE member_benefit_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    member_id UUID REFERENCES members(id),
    policy_id UUID REFERENCES policies(id),
    plan_benefit_id UUID REFERENCES plan_benefits(id),
    used_amount NUMERIC DEFAULT 0,
    last_used_at TIMESTAMP
);
