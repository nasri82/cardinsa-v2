from fastapi import APIRouter
from app.api.health_route import router as health_router


### import auth routes
from app.modules.auth.routes.auth_route import router as auth_router
from app.modules.auth.routes.users_route import router as users_router
from app.modules.auth.routes.roles_route import router as roles_router
from app.modules.auth.routes.user_roles_route import router as user_roles_router
from app.modules.auth.routes.password_reset_route import router as password_reset_router

### import org routes
from app.modules.org.routes.companies_route import router as companies_router
from app.modules.org.routes.departments_route import router as departments_router
from app.modules.org.routes.units_route import router as units_router
from app.modules.org.routes.locations_route import router as locations_router
from app.modules.org.routes.org_tree_route import router as org_tree_router
from app.modules.auth.routes.user_roles_effective_route import router as user_roles_effective_router

### import employees routes
from app.api.v1.employee_router import router as employee_module_router


### import product routes 


from app.modules.pricing.product.routes.product_catalog_route import router as product_catalog_router
from app.modules.pricing.product.routes.product_feature_route import router as product_feature_router
from app.modules.pricing.product.routes.plan_type_route import router as plan_type_router
from app.modules.pricing.product.routes.actuarial_table_route import router as actuarial_table_router

## import pricing  reference
from app.modules.pricing.reference.router import router as pricing_reference_router

# Reference Data - Insurance Types (Dynamic)
from app.modules.reference.routes.insurance_types_route import router as insurance_types_router

# Benefits module imports
from app.modules.pricing.benefits.routes.benefit_category_route import router as benefit_category_router
from app.modules.pricing.benefits.routes.coverage_route import router as coverage_router
from app.modules.pricing.benefits.routes.coverage_option_route import router as coverage_option_router
from app.modules.pricing.benefits.routes.benefit_type_route import router as benefit_type_router
from app.modules.pricing.benefits.routes.benefit_calculation_rule_route import router as benefit_rule_router
from app.modules.pricing.benefits.routes.benefit_limit_route import router as benefit_limit_router
# Step 2D â€" Benefit Module Routers
from app.modules.pricing.benefits.routes.plan_benefit_schedule_route import router as plan_benefit_schedule_router
from app.modules.pricing.benefits.routes.benefit_condition_route import router as benefit_condition_router
from app.modules.pricing.benefits.routes.benefit_translation_route import router as benefit_translation_router
from app.modules.pricing.benefits.routes.benefit_preapproval_rule_route import router as benefit_preapproval_rule_router

# Step 2C Plan Module Routers
from app.modules.pricing.plans.routes.plan_route import router as plan_router
from app.modules.pricing.plans.routes.plan_coverage_link_route import router as plan_coverage_link_router
from app.modules.pricing.plans.routes.plan_exclusion_route import router as plan_exclusion_router
from app.modules.pricing.plans.routes.plan_exclusion_link_route import router as plan_exclusion_link_router
from app.modules.pricing.plans.routes.plan_version_route import router as plan_version_router
from app.modules.pricing.plans.routes.plan_territory_route import router as plan_territory_router
from app.modules.pricing.plans.routes.plan_eligibility_rule_route import router as plan_eligibility_rule_router

# Step 3A Imports
from app.modules.providers.routes.providers_route import router as providers_router
from app.modules.providers.routes.provider_types_route import router as provider_types_router
from app.modules.providers.routes.provider_networks_route import router as provider_networks_router
from app.modules.providers.routes.provider_network_members_route import router as provider_network_members_router
from app.modules.providers.routes.provider_service_prices_route import router as provider_service_prices_router
from app.modules.providers.routes.brokers_route import router as brokers_router
from app.modules.providers.routes.provider_contact_route import router as provider_contact_router
from app.modules.providers.routes.provider_service_route import router as provider_service_router
from app.modules.providers.routes.provider_specialty_route import router as provider_specialty_router
from app.modules.providers.routes.provider_rating_route import router as provider_rating_router
from app.modules.providers.routes.provider_document_route import router as provider_document_router
from app.modules.providers.routes.provider_tag_route import router as provider_tag_router
from app.modules.providers.routes.provider_flag_route import router as provider_flag_router
from app.modules.providers.routes.provider_image_route import router as provider_image_router
from app.modules.providers.routes.provider_working_hours_route import router as provider_working_hours_router
from app.modules.providers.routes.provider_availability_exception_route import router as provider_availability_exception_router
from app.modules.providers.routes.provider_claim_route import router as provider_claim_router
from app.modules.providers.routes.provider_audit_log_route import router as provider_audit_log_router
from app.modules.providers.routes.broker_assignment_route import router as broker_assignment_router
from app.modules.providers.routes.tpa_integration_log_route import router as tpa_integration_log_router

# Step 3A.5: Import Actuarial Router EARLY (before Demographics)
# This ensures ActuarialPremiumRateTables model is loaded before OccupationPremiumFactor tries to reference it
from app.modules.actuarial.router import router as actuarial_router

# Step 3A.6: Pricing Engine Routes - Phases 1.2, 1.3, 1.4
from app.modules.pricing.plans.routes.group_pricing_route import router as group_pricing_router
from app.modules.pricing.plans.routes.rating_class_route import router as rating_class_router
from app.modules.pricing.plans.routes.composite_rating_route import router as composite_rating_router

# Step 3B: Demographics Routes
from app.modules.demographics.routes.age_bracket_route import router as age_bracket_router
from app.modules.demographics.routes.premium_age_bracket_route import router as premium_age_bracket_router
from app.modules.demographics.routes.occupation_category_route import router as occupation_category_router
from app.modules.demographics.routes.occupation_premium_factor_route import router as occupation_premium_factor_router
from app.modules.demographics.routes.occupation_underwriting_rule_route import router as occupation_underwriting_rule_router

# Step 3C: Specialized Insurance Lines
from app.modules.workers_comp.router import router as workers_comp_router
from app.modules.cyber.router import router as cyber_insurance_router
from app.modules.marine.router import router as marine_insurance_router

# Pricing Profiles (Step 4)
from app.modules.pricing.profiles.router import router as pricing_profiles_router

# 🚀 STEP 6: ADVANCED RULES ENGINE IMPORTS
# Add these new imports for Step 6 components
from app.modules.pricing.profiles.routes.advanced_rules_route import router as advanced_rules_router
from app.modules.pricing.profiles.routes.rule_orchestration_route import router as rule_orchestration_router

from app.modules.pricing.modifiers.router import router as pricing_modifiers_router

# 🤖 AI PRICING ENGINE
from app.modules.pricing.ai.router import router as ai_pricing_router


# Pricing Calculation Routes
from app.modules.pricing.calculations.routes import (
    premium_calculation_route,
    premium_override_log_route,
)



## quotations


from app.modules.pricing.quotations.routes.quotations_route import router as quotations_router
from app.modules.pricing.quotations.routes.quotation_items_route import router as quotation_items_router
from app.modules.pricing.quotations.routes.quotation_factors_route import router as quotation_factors_router

# 📋 PRICING PROGRAMS MODULE
from app.modules.pricing.programs.routes.program_route import router as programs_router

# 🎉  UNDERWRITING MODULE
from app.modules.underwriting.routes.underwriting_route import router as underwriting_router

# 📋 POLICY MODULE
from app.modules.insurance.policies.routes.policies_route import router as policies_router
from app.modules.insurance.policies.routes.policy_dependents_route import router as policy_dependents_router
from app.modules.insurance.policies.routes.policy_lifecycle_route import router as policy_lifecycle_router
from app.modules.insurance.policies.routes.policy_types_route import router as policy_types_router
from app.modules.insurance.policies.routes.policy_coverages_route import router as policy_coverages_router
from app.modules.insurance.policies.routes.policy_payments_route import router as policy_payments_router
from app.modules.insurance.policies.routes.policy_status_logs_route import router as policy_status_logs_router
from app.modules.insurance.policies.routes.policy_suspension_payment_route import router as policy_suspension_payment_router

# 🏥 TPA & CLAIMS MODULE
from app.modules.tpa.routes.tpa_companies_route import router as tpa_companies_router

# ✨ PHASE 2: COMPREHENSIVE CLAIMS MANAGEMENT (New)
from app.modules.insurance.claims.routes.claims_route import router as claims_router
from app.modules.insurance.claims.routes.claim_assignment_route import router as claim_assignment_router
from app.modules.insurance.claims.routes.claim_sla_route import router as claim_sla_router
from app.modules.insurance.claims.routes.claim_workflow_route import router as claim_workflow_router

# Legacy TPA Claims (Old - for backward compatibility)
# Commented out to avoid table definition conflicts - use new comprehensive claims module instead
# from app.modules.claims.routes.claims_route import router as legacy_claims_router
# from app.modules.claims.routes.tpa_webhooks_route import router as tpa_webhooks_router
# from app.modules.claims.routes.reserves_route import router as reserves_router
# from app.modules.claims.routes.fraud_route import router as fraud_router
# from app.modules.claims.routes.subrogation_route import router as subrogation_router
# from app.modules.claims.routes.activities_route import router as activities_router
# from app.modules.claims.routes.notes_route import router as notes_router
# from app.modules.claims.routes.appeals_route import router as appeals_router
# from app.modules.claims.routes.medical_reviews_route import router as medical_reviews_router
# from app.modules.claims.routes.workflow_route import router as workflow_router

# 🚗 GARAGE/MOTOR INSURANCE MODULE (Damage Assessment & Repair Estimates)
from app.modules.garages.router import router as garages_router

# 💰 FINANCE & ACCOUNTING MODULE
from app.modules.finance.routes.payment_routes import router as payment_routes_router
from app.modules.finance.routes.invoice_routes import router as invoice_routes_router
from app.modules.finance.routes.gateway_management_routes import router as gateway_management_router
from app.modules.finance.routes.payment_gateway_routes import router as payment_gateway_router
from app.modules.finance.routes.email_routes import router as email_router

# 💰 FINANCIAL INTEGRATION MODULE (Bank Accounts, Cash Management, Payment Batches, Reimbursements, Reconciliation, Journal Posting)
from app.modules.finance.routes.bank_accounts_route import router as bank_accounts_router
from app.modules.finance.routes.cash_management_route import router as cash_management_router
from app.modules.finance.routes.payment_batches_route import router as payment_batches_router
from app.modules.finance.routes.member_reimbursements_route import router as member_reimbursements_router
from app.modules.finance.routes.reconciliation_route import router as reconciliation_router
from app.modules.finance.routes.journal_posting_route import router as journal_posting_router

# 📒 ACCOUNTING MODULE (Double-Entry Bookkeeping)
from app.modules.accounting.routes import router as accounting_router

# 📄 DOCUMENT MANAGEMENT SYSTEM
from app.modules.documents.routes.document_routes import router as document_routes_router
from app.modules.documents.routes.template_routes import router as template_routes_router
from app.modules.documents.routes.category_routes import router as category_routes_router
from app.modules.documents.routes.workflow_routes import router as workflow_routes_router

# 👥 MEMBER/POLICYHOLDER MODULE
from app.modules.members.routes import router as members_main_router

# 🏢 GROUP INSURANCE MODULE
from app.modules.groups.routes.enrollment_period_routes import router as enrollment_period_router
from app.modules.groups.routes.renewals_route import router as groups_renewals_router
from app.modules.groups.routes import router as groups_main_router


# 🔲 QR CODE & VERIFICATION MODULE
from app.modules.qr.routes import qr_router

# 💰 BILLING & COLLECTIONS MODULE
from app.modules.billing.routes import billing_router

# 🔌 EXTERNAL API MODULE (TPA Integration, File Exchange, API Management)
from app.modules.external_api.routes import external_api_router

# 📊 ADMIN DASHBOARD MODULE
from app.modules.admin.routes.dashboard_route import router as dashboard_router

# 🛡️ REINSURANCE MODULE
from app.modules.reinsurance.routes.reinsurers_route import router as reinsurers_router
from app.modules.reinsurance.routes.reinsurance_route import router as reinsurance_main_router
from app.modules.reinsurance.routes.cessions_route import router as cessions_router
from app.modules.reinsurance.routes.recoveries_route import router as recoveries_router
from app.modules.reinsurance.routes.bordereaux_route import router as bordereaux_router
from app.modules.reinsurance.routes.settlements_route import router as settlements_router
from app.modules.reinsurance.routes.participations_route import router as participations_router


api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])


###vauth routes 

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(roles_router)
api_router.include_router(user_roles_router)
api_router.include_router(password_reset_router)
api_router.include_router(user_roles_effective_router)

###org routes
api_router.include_router(companies_router)
api_router.include_router(departments_router)
api_router.include_router(units_router)
api_router.include_router(locations_router)
api_router.include_router(org_tree_router)


### employee  routes 
api_router.include_router(employee_module_router)


# Register product-level endpoints (Step 2B - Products Module)
api_router.include_router(product_catalog_router, prefix="/pricing/products", tags=["Products"])
api_router.include_router(product_feature_router, prefix="/pricing/products/features", tags=["Products"])
api_router.include_router(plan_type_router, prefix="/pricing/plan-types", tags=["Products"])
api_router.include_router(actuarial_table_router, prefix="/pricing/actuarial-tables", tags=["Actuarial"])



### Register pricing refernces routes
api_router.include_router(pricing_reference_router)

### Register Insurance Types (Dynamic Reference Data)
api_router.include_router(insurance_types_router, prefix="/insurance-types", tags=["Insurance Types"])

# Register benefits routers (Step 2D - Benefits Module)
api_router.include_router(benefit_category_router, prefix="/pricing/benefits/categories", tags=["Benefits"])
api_router.include_router(coverage_router, prefix="/pricing/benefits/coverages", tags=["Benefits"])
api_router.include_router(coverage_option_router, prefix="/pricing/benefits/coverage-options", tags=["Benefits"])
api_router.include_router(benefit_type_router, prefix="/pricing/benefits/types", tags=["Benefits"])
api_router.include_router(benefit_rule_router, prefix="/pricing/benefits/calculation-rules", tags=["Benefits"])
api_router.include_router(benefit_limit_router, prefix="/pricing/benefits/limits", tags=["Benefits"])
api_router.include_router(plan_benefit_schedule_router, prefix="/pricing/benefits/schedules", tags=["Benefits"])
api_router.include_router(benefit_condition_router, prefix="/pricing/benefits/conditions", tags=["Benefits"])
api_router.include_router(benefit_translation_router, prefix="/pricing/benefits/translations", tags=["Benefits"])
api_router.include_router(benefit_preapproval_rule_router, prefix="/pricing/benefits/preapproval-rules", tags=["Benefits"])


# âœ… Register Step 2C Plan Routes
api_router.include_router(plan_router, prefix="/pricing/plans", tags=["Plans"])
api_router.include_router(plan_coverage_link_router, prefix="/pricing/plans/coverage-links", tags=["Plans"])
api_router.include_router(plan_exclusion_router, prefix="/pricing/plans/exclusions", tags=["Plans"])
api_router.include_router(plan_exclusion_link_router, prefix="/pricing/plans/exclusion-links", tags=["Plans"])
api_router.include_router(plan_version_router, prefix="/pricing/plans/versions", tags=["Plans"])
api_router.include_router(plan_territory_router, prefix="/pricing/plans/territories", tags=["Plans"])
api_router.include_router(plan_eligibility_rule_router, prefix="/pricing/plans/eligibility-rules", tags=["Plans"])

# Register Pricing Engine Enhancement Routes - Phases 1.2, 1.3, 1.4
api_router.include_router(group_pricing_router, prefix="/pricing/plans", tags=["Plans - Group Pricing"])
api_router.include_router(rating_class_router, prefix="/pricing/plans", tags=["Plans - Rating Classes"])
api_router.include_router(composite_rating_router, prefix="/pricing/plans", tags=["Plans - Composite Rating"])

# âœ… Step 3A Router Includes
api_router.include_router(providers_router)
api_router.include_router(provider_types_router)
api_router.include_router(provider_networks_router)
api_router.include_router(provider_network_members_router)
api_router.include_router(provider_service_prices_router)
api_router.include_router(brokers_router, tags=["Provider Brokers"])
api_router.include_router(provider_contact_router, tags=["Provider Contacts"])
api_router.include_router(provider_service_router, tags=["Provider Services"])
api_router.include_router(provider_specialty_router, tags=["Provider Specialties"])
api_router.include_router(provider_rating_router, tags=["Provider Ratings"])
api_router.include_router(provider_document_router, tags=["Provider Documents"])
api_router.include_router(provider_tag_router, tags=["Provider Tags"])
api_router.include_router(provider_flag_router, tags=["Provider Flags"])
api_router.include_router(provider_image_router, tags=["Provider Images"])
api_router.include_router(provider_working_hours_router, tags=["Provider Working Hours"])
api_router.include_router(provider_availability_exception_router, tags=["Provider Availability Exceptions"])
api_router.include_router(provider_claim_router, tags=["Provider Claims"])
api_router.include_router(provider_audit_log_router, tags=["Provider Audit Logs"])
api_router.include_router(broker_assignment_router, tags=["Broker Assignments"])
api_router.include_router(tpa_integration_log_router, tags=["TPA Integration Logs"])

# Demographics
api_router.include_router(age_bracket_router, prefix="/age-brackets", tags=["Demographics"])
api_router.include_router(premium_age_bracket_router, prefix="/premium-age-brackets", tags=["Demographics"])
api_router.include_router(occupation_category_router, prefix="/occupation-categories", tags=["Demographics"])
api_router.include_router(occupation_premium_factor_router, prefix="/occupation-premium-factors", tags=["Demographics", "Pricing"])
api_router.include_router(occupation_underwriting_rule_router, prefix="/occupation-underwriting-rules", tags=["Demographics", "Underwriting"])

# Specialized Insurance Lines
api_router.include_router(workers_comp_router, prefix="/workers-comp", tags=["Workers' Compensation"])
api_router.include_router(cyber_insurance_router, prefix="/cyber", tags=["Cyber Insurance"])
api_router.include_router(marine_insurance_router, prefix="/marine", tags=["Marine Insurance"])

# Step 4: Pricing Profiles
api_router.include_router(pricing_profiles_router, prefix="/pricing/profiles", tags=["Pricing Profiles"])

# 🚀 STEP 6: ADVANCED RULES ENGINE ROUTERS
# Add these router registrations for Step 6 components
api_router.include_router(advanced_rules_router, prefix="/pricing/profiles/advanced-rules", tags=["Advanced Rules"])
api_router.include_router(rule_orchestration_router, prefix="/pricing/profiles/orchestration", tags=["Rule Orchestration"])

api_router.include_router(pricing_modifiers_router, prefix="/pricing/modifiers")

# 🤖 AI PRICING ENGINE - 44 Endpoints
api_router.include_router(ai_pricing_router, prefix="/pricing/ai", tags=["AI Pricing Engine"])

# Include calculation module routes (Step 7 - Premium Calculation Engine)
api_router.include_router(premium_calculation_route.router, prefix="/pricing/calculations", tags=["Premium Calculations"])
api_router.include_router(premium_override_log_route.router, prefix="/pricing/calculations/overrides", tags=["Premium Overrides"])


### quotations (Step 7B - Quotations Module)
api_router.include_router(quotations_router, prefix="/pricing/quotations", tags=["Quotations"])
api_router.include_router(quotation_items_router, prefix="/pricing/quotations/items", tags=["Quotation Items"])
api_router.include_router(quotation_factors_router, prefix="/pricing/quotations/factors", tags=["Quotation Factors"])

### programs (Pricing Programs Module)
api_router.include_router(programs_router, prefix="/pricing/programs", tags=["Pricing Programs"])


### underwriting
api_router.include_router(underwriting_router, tags=["Underwriting Engine"])

### policies
api_router.include_router(policies_router, tags=["Policy Management"])
api_router.include_router(policy_dependents_router, tags=["Policy Dependents"])
api_router.include_router(policy_lifecycle_router, tags=["Policy Lifecycle"])
api_router.include_router(policy_suspension_payment_router, tags=["Policy Suspension & Payment Schedules"])
api_router.include_router(policy_types_router, tags=["Policy Types"])
api_router.include_router(policy_coverages_router, tags=["Policy Coverages"])
api_router.include_router(policy_payments_router, tags=["Policy Payments"])
api_router.include_router(policy_status_logs_router, tags=["Policy Status Logs"])

### TPA & Claims
api_router.include_router(tpa_companies_router, tags=["TPA Management"])

# ✨ PHASE 2: COMPREHENSIVE CLAIMS MANAGEMENT (36 endpoints - New!)
api_router.include_router(claims_router, tags=["Claims Management"])

# ✨ PHASE 2 WEEK 4: CLAIMS WORKFLOW AUTOMATION (25+ endpoints - New!)
api_router.include_router(claim_assignment_router, prefix="/claims", tags=["Claims Management"])
api_router.include_router(claim_sla_router, prefix="/claims", tags=["Claims Management"])
api_router.include_router(claim_workflow_router, prefix="/claims", tags=["Claims Management"])

# Legacy TPA Claims (for backward compatibility)
# Commented out to avoid table definition conflicts - use new comprehensive claims module instead
# api_router.include_router(legacy_claims_router, prefix="/tpa-claims", tags=["TPA Claims (Legacy)"])
# api_router.include_router(tpa_webhooks_router, tags=["TPA Webhooks"])
# api_router.include_router(reserves_router, tags=["Claims Reserves"])
# api_router.include_router(fraud_router, tags=["Fraud Detection"])
# api_router.include_router(subrogation_router, tags=["Subrogation"])
# api_router.include_router(activities_router, tags=["Claim Activities"])
# api_router.include_router(notes_router, tags=["Claim Notes"])
# api_router.include_router(appeals_router, tags=["Claim Appeals"])
# api_router.include_router(medical_reviews_router, tags=["Medical Reviews"])
# api_router.include_router(workflow_router, tags=["Claim Workflow"])

### Garage/Motor Insurance Module (Damage Assessment & Repair Estimates)
api_router.include_router(garages_router, tags=["Garage Management"])

### Finance & Accounting
api_router.include_router(payment_routes_router, tags=["Finance"])
api_router.include_router(invoice_routes_router, tags=["Finance"])
api_router.include_router(payment_gateway_router, tags=["Finance - Payment Gateways"])
api_router.include_router(gateway_management_router, tags=["Finance - Gateway Management"])
api_router.include_router(email_router, tags=["Finance - Email Service"])

### Financial Integration (48 endpoints - Bank Accounts, Cash Management, Payment Batches, Reimbursements, Reconciliation, Journal Posting)
api_router.include_router(bank_accounts_router, tags=["Financial Integration - Bank Accounts"])
api_router.include_router(cash_management_router, tags=["Financial Integration - Cash Management"])
api_router.include_router(payment_batches_router, tags=["Financial Integration - Payment Batches"])
api_router.include_router(member_reimbursements_router, tags=["Financial Integration - Member Reimbursements"])
api_router.include_router(reconciliation_router, tags=["Financial Integration - Reconciliation"])
api_router.include_router(journal_posting_router, tags=["Financial Integration - Journal Posting"])

### Accounting Module (Double-Entry Bookkeeping) - 53 Endpoints
api_router.include_router(accounting_router, tags=["Accounting"])

### Document Management System
api_router.include_router(document_routes_router, tags=["Documents"])
api_router.include_router(template_routes_router, tags=["Documents"])
api_router.include_router(category_routes_router, tags=["Documents"])
api_router.include_router(workflow_routes_router, tags=["Documents"])

### Member/Policyholder Module (183 endpoints across 12 routes)
api_router.include_router(members_main_router)

# Register Groups Insurance Module
# IMPORTANT: Static routes MUST be registered BEFORE dynamic routes
api_router.include_router(enrollment_period_router, prefix="/groups/enrollment-periods", tags=["Group Enrollment Periods"])
api_router.include_router(groups_renewals_router, prefix="/groups/renewals", tags=["Group Renewals"])
api_router.include_router(groups_main_router, tags=["Group Insurance"])


### QR Code & Verification Module (30+ endpoints)
api_router.include_router(qr_router, tags=["QR Codes"])

### Billing & Collections Module (25+ endpoints)
api_router.include_router(billing_router)

### External API Module (TPA Integration, File Exchange, Admin)
api_router.include_router(external_api_router)

### Admin Dashboard Module
api_router.include_router(dashboard_router, prefix="/admin", tags=["Admin Dashboard"])

### Reinsurance Module - Complete ✅
api_router.include_router(reinsurance_main_router, tags=["Reinsurance"])
api_router.include_router(reinsurers_router, tags=["Reinsurance - Reinsurers"])
api_router.include_router(cessions_router, tags=["Reinsurance - Cessions"])
api_router.include_router(recoveries_router, tags=["Reinsurance - Recoveries"])
api_router.include_router(bordereaux_router, tags=["Reinsurance - Bordereaux"])
api_router.include_router(settlements_router, tags=["Reinsurance - Settlements"])
api_router.include_router(participations_router, tags=["Reinsurance - Participations"])

# 🛡️ TREATY MODULE (Reinsurance Treaty Management)
from app.modules.treaty.routes.treaties_route import router as treaties_router
from app.modules.treaty.routes.layers_route import router as layers_router
from app.modules.treaty.routes.programs_route import router as programs_router
from app.modules.treaty.routes.reinstatements_route import router as reinstatements_router

# 🪪 DIGITAL INSURANCE CARDS MODULE (QR Code Verification)
from app.modules.insurance.cards.routes.digital_card_route import router as digital_cards_router

# 📊 ACTUARIAL MODULE (IFRS 17, IAS 19, Pricing Engine)
from app.modules.actuarial.router import router as actuarial_router

### Treaty Module - Complete ✅
api_router.include_router(treaties_router, tags=["Treaty Contracts"])
api_router.include_router(layers_router, tags=["Treaty Layers"])
api_router.include_router(programs_router, tags=["Treaty Programs"])
api_router.include_router(reinstatements_router, tags=["Treaty Reinstatements"])

### Digital Insurance Cards Module - Complete ✅
api_router.include_router(digital_cards_router, tags=["Digital Insurance Cards"])

### Actuarial Module - Complete ✅ (IFRS 17, IAS 19, Pricing)
api_router.include_router(actuarial_router, tags=["Actuarial"])

### Reporting Module - Complete ✅ (Phase 5: Reports, BI Dashboards, Regulatory)
from app.modules.reporting.router import router as reporting_router
api_router.include_router(reporting_router, tags=["Reporting"])

### Payment Gateway Integration - Complete ✅ (Phase 6: Stripe, PayPal)
from app.modules.payments.routes.payment_gateway_route import router as payment_gateway_integration_router
api_router.include_router(payment_gateway_integration_router, prefix="/payments", tags=["Payment Gateway Integration"])

### Admin Management - Complete ✅ (Phase 7: System Config, Audit Trails)
from app.modules.admin.routes.system_config_route import router as system_config_router
from app.modules.admin.routes.audit_trail_route import router as audit_trail_router
api_router.include_router(system_config_router, prefix="/admin", tags=["Admin - System Configuration"])
api_router.include_router(audit_trail_router, prefix="/admin", tags=["Admin - Audit Trail"])
