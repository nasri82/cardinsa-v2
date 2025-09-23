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

# Benefits module imports
from app.modules.pricing.benefits.routes.benefit_category_route import router as benefit_category_router
from app.modules.pricing.benefits.routes.coverage_route import router as coverage_router
from app.modules.pricing.benefits.routes.coverage_option_route import router as coverage_option_router
from app.modules.pricing.benefits.routes.benefit_type_route import router as benefit_type_router
from app.modules.pricing.benefits.routes.benefit_calculation_rule_route import router as benefit_rule_router
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

# Step 3B: Demographics Routes
from app.modules.demographics.routes.age_bracket_route import router as age_bracket_router
from app.modules.demographics.routes.premium_age_bracket_route import router as premium_age_bracket_router
from app.modules.demographics.routes.occupation_category_route import router as occupation_category_router

# Pricing Profiles (Step 4)
from app.modules.pricing.profiles.router import router as pricing_profiles_router

# 🚀 STEP 6: ADVANCED RULES ENGINE IMPORTS
# Add these new imports for Step 6 components
from app.modules.pricing.profiles.routes.advanced_rules_route import router as advanced_rules_router
from app.modules.pricing.profiles.routes.rule_orchestration_route import router as rule_orchestration_router

from app.modules.pricing.modifiers.router import router as pricing_modifiers_router


# Pricing Calculation Routes
from app.modules.pricing.calculations.routes import (
    premium_calculation_route,
    premium_override_log_route,
)



## quotations


from app.modules.pricing.quotations.routes.quotations_route import router as quotations_router
from app.modules.pricing.quotations.routes.quotation_items_route import router as quotation_items_router
from app.modules.pricing.quotations.routes.quotation_factors_route import router as quotation_factors_router

# 🎉  UNDERWRITING MODULE 
from app.modules.underwriting.routes.underwriting_route import router as underwriting_router


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
api_router.include_router(org_tree_router)


### employee  routes 
api_router.include_router(employee_module_router)


# Register product-level endpoints
api_router.include_router(product_catalog_router)
api_router.include_router(product_feature_router)
api_router.include_router(plan_type_router)
api_router.include_router(actuarial_table_router)



### Register pricing refernces routes
api_router.include_router(pricing_reference_router)

# Register benefits routers
api_router.include_router(benefit_category_router)
api_router.include_router(coverage_router)
api_router.include_router(coverage_option_router)
api_router.include_router(benefit_type_router)
api_router.include_router(benefit_rule_router)
api_router.include_router(plan_benefit_schedule_router)
api_router.include_router(benefit_condition_router)
api_router.include_router(benefit_translation_router)
api_router.include_router(benefit_preapproval_rule_router)


# âœ… Register Step 2C Plan Routes
api_router.include_router(plan_router)
api_router.include_router(plan_coverage_link_router)
api_router.include_router(plan_exclusion_router)
api_router.include_router(plan_exclusion_link_router)
api_router.include_router(plan_version_router)
api_router.include_router(plan_territory_router)
api_router.include_router(plan_eligibility_rule_router)

# âœ… Step 3A Router Includes
api_router.include_router(providers_router)
api_router.include_router(provider_types_router)
api_router.include_router(provider_networks_router)
api_router.include_router(provider_network_members_router)
api_router.include_router(provider_service_prices_router)

# Demographics
api_router.include_router(age_bracket_router, prefix="/age-brackets", tags=["Demographics"])
api_router.include_router(premium_age_bracket_router, prefix="/premium-age-brackets", tags=["Demographics"])
api_router.include_router(occupation_category_router, prefix="/occupation-categories", tags=["Demographics"])


# Step 4: Pricing Profiles
api_router.include_router(pricing_profiles_router)

# 🚀 STEP 6: ADVANCED RULES ENGINE ROUTERS
# Add these router registrations for Step 6 components
api_router.include_router(advanced_rules_router)
api_router.include_router(rule_orchestration_router)

api_router.include_router(pricing_modifiers_router, prefix="/pricing/modifiers")

# Include calculation module routes
api_router.include_router(premium_calculation_route.router)
api_router.include_router(premium_override_log_route.router)


### quotations
api_router.include_router(quotations_router)
api_router.include_router(quotation_items_router)
api_router.include_router(quotation_factors_router)


### underwriting
api_router.include_router(underwriting_router, tags=["Underwriting Engine"])