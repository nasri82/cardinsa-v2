import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # project root (…/cardinsa-backend)
APP = ROOT / "app"

# ---- folders to create ----
FOLDERS = [
    "app", "app/core", "app/api", "app/api/v1", "app/modules", "app/utils", "tests", "scripts",
    # Auth & Security
    "app/modules/auth/models","app/modules/auth/schemas","app/modules/auth/repositories","app/modules/auth/services","app/modules/auth/routes",
    "app/modules/security/models","app/modules/security/schemas","app/modules/security/repositories","app/modules/security/services","app/modules/security/routes",
    # Insurance
    "app/modules/insurance/policies/models","app/modules/insurance/policies/schemas","app/modules/insurance/policies/repositories","app/modules/insurance/policies/services","app/modules/insurance/policies/routes",
    "app/modules/insurance/plans/models","app/modules/insurance/plans/schemas","app/modules/insurance/plans/repositories","app/modules/insurance/plans/services","app/modules/insurance/plans/routes",
    "app/modules/insurance/coverages/models","app/modules/insurance/coverages/schemas","app/modules/insurance/coverages/repositories","app/modules/insurance/coverages/services","app/modules/insurance/coverages/routes",
    "app/modules/insurance/claims/models","app/modules/insurance/claims/schemas","app/modules/insurance/claims/repositories","app/modules/insurance/claims/services","app/modules/insurance/claims/routes",
    "app/modules/insurance/quotations/models","app/modules/insurance/quotations/schemas","app/modules/insurance/quotations/repositories","app/modules/insurance/quotations/services","app/modules/insurance/quotations/routes",
    # Documents (unified)
    "app/modules/documents/models","app/modules/documents/schemas","app/modules/documents/repositories","app/modules/documents/services","app/modules/documents/routes",
    # Providers & Networks
    "app/modules/providers/models","app/modules/providers/schemas","app/modules/providers/repositories","app/modules/providers/services","app/modules/providers/routes",
    "app/modules/provider_networks/models","app/modules/provider_networks/schemas","app/modules/provider_networks/repositories","app/modules/provider_networks/services","app/modules/provider_networks/routes",
    # Notifications
    "app/modules/notifications/models","app/modules/notifications/schemas","app/modules/notifications/repositories","app/modules/notifications/services","app/modules/notifications/routes",
    # SaaS Subscriptions
    "app/modules/subscriptions/models","app/modules/subscriptions/schemas","app/modules/subscriptions/repositories","app/modules/subscriptions/services","app/modules/subscriptions/routes",
    # AI & Finance
    "app/modules/ai/models","app/modules/ai/schemas","app/modules/ai/repositories","app/modules/ai/services","app/modules/ai/routes",
    "app/modules/finance/models","app/modules/finance/schemas","app/modules/finance/repositories","app/modules/finance/services","app/modules/finance/routes",
    # Common DTOs/enums
    "app/modules/common",
]

ROUTE_STUBS = {
    "app/modules/auth/routes/auth_route.py": ("/auth","auth"),
    "app/modules/auth/routes/users_route.py": ("/users","users"),
    "app/modules/security/routes/security_route.py": ("/security","security"),
    "app/modules/insurance/policies/routes/policies_route.py": ("/policies","policies"),
    "app/modules/insurance/plans/routes/plans_route.py": ("/plans","plans"),
    "app/modules/insurance/coverages/routes/coverages_route.py": ("/coverages","coverages"),
    "app/modules/insurance/claims/routes/claims_route.py": ("/claims","claims"),
    "app/modules/insurance/quotations/routes/quotations_route.py": ("/quotations","quotations"),
    "app/modules/documents/routes/documents_route.py": ("/documents","documents"),
    "app/modules/providers/routes/providers_route.py": ("/providers","providers"),
    "app/modules/provider_networks/routes/networks_route.py": ("/provider-networks","provider_networks"),
    "app/modules/notifications/routes/notifications_route.py": ("/notifications","notifications"),
    "app/modules/subscriptions/routes/subscriptions_route.py": ("/subscriptions","subscriptions"),
    "app/modules/ai/routes/ai_route.py": ("/ai","ai"),
    "app/modules/finance/routes/finance_route.py": ("/finance","finance"),
}

ENTITIES = [
    ("app/modules/auth","User","users"),
    ("app/modules/auth","Role","roles"),
    ("app/modules/security","Permission","permissions"),
    ("app/modules/insurance/policies","Policy","policies"),
    ("app/modules/insurance/plans","Plan","plans"),
    ("app/modules/insurance/coverages","Coverage","coverages"),
    ("app/modules/insurance/claims","Claim","claims"),
    ("app/modules/insurance/quotations","Quotation","quotations"),
    ("app/modules/documents","Document","documents"),
    ("app/modules/providers","Provider","providers"),
    ("app/modules/provider_networks","ProviderNetwork","provider_networks"),
    ("app/modules/notifications","Notification","notifications"),
    ("app/modules/subscriptions","SaaSPlan","saas_plans"),
    ("app/modules/subscriptions","CompanySubscription","company_saas_subscriptions"),
    ("app/modules/ai","AiTask","ai_tasks"),
    ("app/modules/finance","Invoice","invoices"),
]

def write_if_absent(path: Path, content: str):
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

def main():
    # 1) dirs + __init__.py
    for d in FOLDERS:
        p = ROOT / d
        p.mkdir(parents=True, exist_ok=True)
        init_py = p / "__init__.py"
        if not init_py.exists():
            init_py.write_text("", encoding="utf-8")

    # 2) keep your existing working core files; add health + router if missing
    write_if_absent(APP/"api/health_route.py", 
        "from fastapi import APIRouter\nrouter=APIRouter(prefix='/health')\n"
        "@router.get('/liveness')\n"
        "def l():\n    return {'status':'ok'}\n"
        "@router.get('/readiness')\n"
        "def r():\n    return {'status':'ready'}\n"
    )
    write_if_absent(APP/"api/v1/router.py", 
        "from fastapi import APIRouter\nfrom app.api.health_route import router as health_router\n\n"
        "api_router = APIRouter()\napi_router.include_router(health_router, tags=['health'])\n"
        "# Uncomment module routers as you implement them:\n"
        "# from app.modules.auth.routes.auth_route import router as auth_router\n"
        "# api_router.include_router(auth_router)\n"
    )

    # 3) route stubs
    for rel, (prefix, tag) in ROUTE_STUBS.items():
        write_if_absent(ROOT/rel,
            f"from fastapi import APIRouter\nrouter=APIRouter(prefix='{prefix}', tags=['{tag}'])\n"
            "@router.get('/_ping')\n"
            "def _ping():\n"
            f"    return {{'ok': True, 'module': '{tag}'}}\n"
        )

    # 4) placeholder model/schema/repo/service
    for base_dir, cls, tbl in ENTITIES:
        write_if_absent(ROOT/f"{base_dir}/models/{cls.lower()}_model.py",
            "from sqlalchemy.orm import Mapped, mapped_column\n"
            "from sqlalchemy.dialects.postgresql import UUID as PG_UUID\n"
            "import uuid\nfrom app.core.database import Base\n\n"
            f"class {cls}(Base):\n"
            f"    __tablename__ = '{tbl}'\n"
            "    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)\n"
        )
        write_if_absent(ROOT/f"{base_dir}/schemas/{cls.lower()}_schema.py",
            "from pydantic import BaseModel\n\n"
            f"class {cls}Base(BaseModel):\n    pass\n\n"
            f"class {cls}Create({cls}Base):\n    pass\n\n"
            f"class {cls}Read({cls}Base):\n    id: str | None = None\n"
        )
        write_if_absent(ROOT/f"{base_dir}/repositories/{cls.lower()}_repository.py",
            f"# repository for {cls} (implement CRUD later)\n"
        )
        write_if_absent(ROOT/f"{base_dir}/services/{cls.lower()}_service.py",
            f"# service for {cls} (business logic later)\n"
        )

    # 5) utils & common
    write_if_absent(APP/"utils/crypto.py", "# hashing/jwt helpers later\n")
    write_if_absent(APP/"utils/pagination.py", "# pagination helpers later\n")
    write_if_absent(APP/"utils/time.py", "# timezone & datetime helpers later\n")
    write_if_absent(APP/"modules/common/README.md", "Shared DTOs, enums, constants go here.\n")

    print("✅ Structure generated (non-destructive).")

if __name__ == "__main__":
    main()
