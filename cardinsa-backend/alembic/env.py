from __future__ import annotations

import sys
from pathlib import Path

from alembic import context
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool

# --- Make sure we can import your app package ("app/") ---
BASE_DIR = Path(__file__).resolve().parents[1]  # project root (contains "app" and "alembic")
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

# --- Import your settings and metadata ---
from app.core.settings import settings
from app.core.database import Base

# Alembic Config object, provides access to values in alembic.ini
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for 'autogenerate'
target_metadata = Base.metadata

# ---- Inject DB URL safely (escape % for ConfigParser) ----
url = settings.DATABASE_URL
# ConfigParser treats % as interpolation; double them
if "%" in url:
    url = url.replace("%", "%%")
config.set_main_option("sqlalchemy.url", url)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=url,                      # use the escaped URL
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
