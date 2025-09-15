import sys, re
from pathlib import Path
from typing import List

GREEN = "\033[92m"; RED = "\033[91m"; YELLOW = "\033[93m"; CYAN = "\033[96m"; RESET = "\033[0m"
def ok(msg): print(f"{GREEN}✔{RESET} {msg}")
def warn(msg): print(f"{YELLOW}!{RESET} {msg}")
def bad(msg): print(f"{RED}✘{RESET} {msg}")

def read_text(p: Path) -> str:
    try: return p.read_text(encoding="utf-8", errors="ignore")
    except: return ""

def exists(p: Path, label: str):
    if p.exists(): ok(f"{label} exists: {p}")
    else: bad(f"{label} missing: {p}")

def check_basic_layout(root: Path):
    print()
    ok("Checking base layout...")
    for d in ["app", "app/api/v1", "app/core", "alembic"]:
        exists(root / d, "Dir")

    # accept either flat or modular structure
    flat_ok = all((root / p).exists() for p in ["app/models","app/schemas","app/services","app/db"])
    modules_dir = root / "app/modules"
    modular_ok = modules_dir.exists()
    if flat_ok:
        ok("Flat layout present (app/models, app/schemas, app/services, app/db)")
    else:
        warn("Flat layout not found (that’s OK if you use modules/)")

    if modular_ok:
        ok("Modular layout detected: app/modules")
    else:
        warn("Modular layout (app/modules) not found")

def check_core_files(root: Path):
    print()
    ok("Checking core files...")
    for f in ["app/main.py", "app/api/v1/router.py", "app/core/dependencies.py"]:
        exists(root / f, "File")

    # config may be in multiple forms
    cfg_candidates = [
        root / "app/core/config.py",
        root / "app/core/settings.py",
        root / "app/core/config/__init__.py",
    ]
    if any(p.exists() for p in cfg_candidates):
        ok("Config/settings module present")
    else:
        bad("No config/settings found (expected app/core/config.py or settings.py)")

def check_dependencies_symbols(root: Path):
    print()
    ok("Checking auth guards in dependencies.py...")
    p = root / "app/core/dependencies.py"
    if not p.exists():
        bad("dependencies.py missing")
        return
    s = read_text(p)
    for sym in ["get_current_user", "require_role", "require_permissions"]:
        if re.search(rf"def\s+{sym}\b", s):
            ok(f"{sym} found")
        else:
            warn(f"{sym} NOT found")

def check_router_registration(root: Path):
    print()
    ok("Checking API router registrations...")
    p = root / "app/api/v1/router.py"
    if not p.exists():
        bad("router.py missing")
        return
    s = read_text(p)
    inc = re.findall(r"include_router\(([^)]+)\)", s)
    if inc: ok(f"include_router() calls detected: {len(inc)}")
    else: warn("No include_router() calls detected")
    print(f"{CYAN}--- router.py snippet ---{RESET}\n" + s[:600] + ("..." if len(s) > 600 else ""))

def list_module_dirs(root: Path, sub: str) -> List[Path]:
    base = root / "app/modules"
    if not base.exists(): return []
    return [p for p in base.rglob(sub) if p.is_dir()]

def check_modular_presence(root: Path):
    print()
    ok("Scanning modules/ for models/schemas/routes/services...")
    for sub in ["models", "schemas", "routes", "services"]:
        dirs = list_module_dirs(root, sub)
        if dirs:
            ok(f"Found {sub} dirs under modules: {len(dirs)}")
        else:
            warn(f"No {sub} dirs found under modules/")

def check_employee_module(root: Path):
    print()
    ok("Checking Employee module under modules/ ...")
    base = root / "app/modules"
    if not base.exists():
        warn("app/modules missing; skipping")
        return

    # common paths
    expected = [
        ("models", ["employee_model.py","department_model.py","unit_model.py"]),
        ("schemas", ["employee_schema.py","department_schema.py","unit_schema.py"]),
        ("routes", ["employee_route.py","departments_route.py","units_route.py"]),
        ("services", ["employee_service.py"]),
        ("crud", ["employee_crud.py","department_crud.py","unit_crud.py"]),
    ]
    found_any = False
    for sub, names in expected:
        subdirs = [p for p in base.rglob(sub) if p.is_dir()]
        hit = False
        for d in subdirs:
            for n in names:
                if (d / n).exists():
                    ok(f"Employee module: {sub}/{n} present in {d}")
                    found_any = True
                    hit = True
        if not hit:
            warn(f"Employee module: no {sub}/" + " or missing expected files")

def check_alembic(root: Path):
    print()
    ok("Checking Alembic...")
    env = root / "alembic/env.py"
    versions = root / "alembic/versions"
    if env.exists(): ok("alembic/env.py present")
    else: warn("alembic/env.py missing")
    if versions.exists() and any(versions.glob("*.py")):
        ok("Alembic versions present")
    else:
        warn("No migration files under alembic/versions")

def main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} /path/to/cardinsa-backend-root\n")
        sys.exit(2)
    root = Path(sys.argv[1]).resolve()
    if not root.exists():
        bad(f"Path not found: {root}"); sys.exit(2)
    print(f"{CYAN}Auditing backend at:{RESET} {root}\n")
    check_basic_layout(root)
    check_core_files(root)
    check_dependencies_symbols(root)
    check_router_registration(root)
    check_modular_presence(root)
    check_employee_module(root)
    check_alembic(root)
    print()
    ok("Audit finished")

if __name__ == "__main__":
    main()
