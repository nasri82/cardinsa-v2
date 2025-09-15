Phase 2: Organizations + Scoped RBAC (kickoff pack)
Standards we carry forward

SQLAlchemy 2.0 models, Pydantic v2 schemas.

Permissions use (resource, action) and require_permission(resource, action).

Raw SQL for schema/seed (idempotent), like we did in Auth v1.

Module layout per feature: app/modules/org/{models,schemas,repositories,routes}.

1) SQL — schema & seeds (copy–paste, Postgres)
BEGIN;

-- Extensions
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ========== Companies / Departments / Units ==========
CREATE TABLE IF NOT EXISTS companies (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  name        varchar(160) NOT NULL,
  code        varchar(60),
  description text,
  is_active   boolean NOT NULL DEFAULT true,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (name),
  UNIQUE (code)
);

CREATE TABLE IF NOT EXISTS departments (
  id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id  uuid NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  name        varchar(160) NOT NULL,
  code        varchar(60),
  description text,
  is_active   boolean NOT NULL DEFAULT true,
  created_at  timestamptz NOT NULL DEFAULT now(),
  updated_at  timestamptz NOT NULL DEFAULT now(),
  UNIQUE (company_id, name),
  UNIQUE (company_id, code)
);

CREATE TABLE IF NOT EXISTS units (
  id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  department_id uuid NOT NULL REFERENCES departments(id) ON DELETE CASCADE,
  name          varchar(160) NOT NULL,
  code          varchar(60),
  description   text,
  is_active     boolean NOT NULL DEFAULT true,
  created_at    timestamptz NOT NULL DEFAULT now(),
  updated_at    timestamptz NOT NULL DEFAULT now(),
  UNIQUE (department_id, name),
  UNIQUE (department_id, code)
);

-- Helpful indexes
CREATE INDEX IF NOT EXISTS ix_departments_company ON departments(company_id);
CREATE INDEX IF NOT EXISTS ix_units_department     ON units(department_id);

-- ========== Scoped RBAC: wire scopes to user_roles ==========
-- (We already added nullable columns earlier; now add FKs if not present)
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM information_schema.constraint_column_usage
    WHERE table_name='user_roles' AND constraint_name='fk_user_roles_company'
  ) THEN
    ALTER TABLE user_roles
      ADD CONSTRAINT fk_user_roles_company
      FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.constraint_column_usage
    WHERE table_name='user_roles' AND constraint_name='fk_user_roles_department'
  ) THEN
    ALTER TABLE user_roles
      ADD CONSTRAINT fk_user_roles_department
      FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE;
  END IF;

  IF NOT EXISTS (
    SELECT 1 FROM information_schema.constraint_column_usage
    WHERE table_name='user_roles' AND constraint_name='fk_user_roles_unit'
  ) THEN
    ALTER TABLE user_roles
      ADD CONSTRAINT fk_user_roles_unit
      FOREIGN KEY (unit_id) REFERENCES units(id) ON DELETE CASCADE;
  END IF;
END$$;

-- ========== Permissions for orgs ==========
-- (resource, action) pairs; idempotent via unique index you already have
INSERT INTO permissions (name, description, resource, action)
VALUES
  ('Manage Companies',   'CRUD companies',     'companies',   'manage'),
  ('Read Companies',     'List/read companies','companies',   'read'),
  ('Manage Departments', 'CRUD departments',   'departments', 'manage'),
  ('Read Departments',   'List/read departments','departments','read'),
  ('Manage Units',       'CRUD units',         'units',       'manage'),
  ('Read Units',         'List/read units',    'units',       'read')
ON CONFLICT (resource, action)
DO UPDATE SET name=EXCLUDED.name, description=EXCLUDED.description;

-- Grants
-- SuperAdmin → everything
WITH r AS (SELECT id FROM roles WHERE name='SuperAdmin'),
     p AS (SELECT id FROM permissions WHERE resource IN ('companies','departments','units'))
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM r CROSS JOIN p
ON CONFLICT DO NOTHING;

-- Admin → manage/read orgs
WITH r AS (SELECT id FROM roles WHERE name='Admin'),
     p AS (SELECT id FROM permissions WHERE resource IN ('companies','departments','units'))
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM r CROSS JOIN p
ON CONFLICT DO NOTHING;

-- User → read-only orgs
WITH r AS (SELECT id FROM roles WHERE name='User'),
     p AS (SELECT id FROM permissions WHERE action='read' AND resource IN ('companies','departments','units'))
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.id, p.id FROM r JOIN p ON TRUE
ON CONFLICT DO NOTHING;

-- ========== Demo seed ==========
INSERT INTO companies (id, name, code, description) VALUES
  (gen_random_uuid(), 'Cardinsa', 'CARD', 'Main tenant')
ON CONFLICT (name) DO NOTHING;

WITH c AS (SELECT id FROM companies WHERE name='Cardinsa')
INSERT INTO departments (id, company_id, name, code) VALUES
  (gen_random_uuid(), (SELECT id FROM c), 'Engineering', 'ENG'),
  (gen_random_uuid(), (SELECT id FROM c), 'Operations',  'OPS')
ON CONFLICT DO NOTHING;

WITH d1 AS (SELECT id FROM departments WHERE name='Engineering'),
     d2 AS (SELECT id FROM departments WHERE name='Operations')
INSERT INTO units (id, department_id, name, code) VALUES
  (gen_random_uuid(), (SELECT id FROM d1), 'Platform',  'PLAT'),
  (gen_random_uuid(), (SELECT id FROM d1), 'Product',   'PROD'),
  (gen_random_uuid(), (SELECT id FROM d2), 'Support',   'SUP')
ON CONFLICT DO NOTHING;

COMMIT;

2) Module layout (create these files)
app/modules/org/
  models/
    company_model.py
    department_model.py
    unit_model.py
  schemas/
    company_schema.py
    department_schema.py
    unit_schema.py
  repositories/
    company_repository.py
    department_repository.py
    unit_repository.py
  routes/
    companies_route.py
    departments_route.py
    units_route.py


Use require_permission on routes:

companies: ("companies","read"), ("companies","manage")

departments: ("departments","read"), ("departments","manage")

units: ("units","read"), ("units","manage")

3) Minimal model snippets (SQLAlchemy 2.0)
# app/modules/org/models/company_model.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Text
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin

class Company(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "companies"
    name: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    code: Mapped[str | None] = mapped_column(String(60), unique=True)
    description: Mapped[str | None] = mapped_column(Text())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    departments = relationship("Department", back_populates="company", lazy="selectin")

# app/modules/org/models/department_model.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Text, ForeignKey
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin

class Department(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "departments"
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str | None] = mapped_column(String(60))
    description: Mapped[str | None] = mapped_column(Text())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    company = relationship("Company", back_populates="departments", lazy="joined")
    units = relationship("Unit", back_populates="department", lazy="selectin")

# app/modules/org/models/unit_model.py
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Text, ForeignKey
from app.core.database import Base, UUIDPrimaryKeyMixin, TimestampMixin

class Unit(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "units"
    department_id: Mapped[str] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    code: Mapped[str | None] = mapped_column(String(60))
    description: Mapped[str | None] = mapped_column(Text())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    department = relationship("Department", back_populates="units", lazy="joined")

4) Route skeletons (permissions on each)
# app/modules/org/routes/companies_route.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import require_permission
from app.modules.org.repositories import company_repository as repo
from app.modules.org.schemas.company_schema import CompanyCreate, CompanyOut

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.get("", response_model=list[CompanyOut], dependencies=[Depends(require_permission("companies","read"))])
def list_companies(db: Session = Depends(get_db)):
    return repo.list_all(db)

@router.post("", response_model=CompanyOut, dependencies=[Depends(require_permission("companies","manage"))])
def create_company(payload: CompanyCreate, db: Session = Depends(get_db)):
    return repo.create(db, payload)


(Repeat same pattern for departments and units with their resources.)

Finally, include these routers in app/api/v1/router.py:

from app.modules.org.routes.companies_route import router as companies_router
from app.modules.org.routes.departments_route import router as departments_router
from app.modules.org.routes.units_route import router as units_router

api_router.include_router(companies_router)
api_router.include_router(departments_router)
api_router.include_router(units_router)

5) Quick smoke plan after implementing

Run the SQL above.

GET /companies (as User/Admin/SuperAdmin): Users can read; Admin/SuperAdmin can create.

Create department under Cardinsa → create units → list by parent.

Assign a role scoped to company_id/department_id (we’ll add the service helper next) and verify guards.