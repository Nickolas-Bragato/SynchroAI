import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
from dotenv import load_dotenv

load_dotenv()

# ─── Importa Base e todos os modelos ───────────────────────────────────────────
# IMPORTANTE: estes imports devem vir ANTES de target_metadata = Base.metadata
# Sem eles o Alembic não enxerga as tabelas e gera migrations vazias.
from app.database import Base
from app.models import (
    Volunteer,
    Institution,
    Need,
    Match,
    TaskHistory,
    Reward,
    Alert,
    Feedback,
    Interest,
)

# ─── Configuração do Alembic ────────────────────────────────────────────────────
config = context.config

# Injeta a DATABASE_URL do .env (sobrescreve o alembic.ini)
db_url = os.getenv("DATABASE_URL", "")
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
config.set_main_option("sqlalchemy.url", db_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Aponta para os metadados de todos os modelos importados acima
target_metadata = Base.metadata


# ─── Modo offline (gera SQL sem conectar no banco) ──────────────────────────────
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# ─── Modo online (conecta no banco e executa) ───────────────────────────────────
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()