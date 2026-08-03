from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from base_de_datos import Base, URL_BASE_DATOS

# Registra TODOS los modelos en Base.metadata antes de que target_metadata
# se lea mas abajo. app.py logra esto via dos caminos combinados: (1) importa
# los routers, que transitivamente importan catalogo_modelos.py (que a su vez
# importa los 17 Repositorios del CRUD generico), y (2) importa a mano los 4
# modelos que quedan fuera de ese catalogo (ver comentario original en
# app.py). Este archivo NO importa los routers (evitarlo a proposito: routers/
# auth.py -> configuracion.py exige CONTINENTAL_SECRET_KEY, y no tiene sentido
# que un comando de migracion dependa de eso), asi que replica el mismo
# resultado importando catalogo_modelos directo (mismo efecto, sin FastAPI/
# configuracion.py de por medio) + los modelos que ni siquiera catalogo_modelos
# cubre (Historial, Adjunto, AlertaEstado -- cada uno con su propio router
# dedicado en vez del CRUD generico).
import catalogo_modelos  # noqa: F401 - registra los 17 modelos del catalogo generico
from Modulos.Historial import Historial  # noqa: F401
from Modulos.Adjuntos import Adjunto  # noqa: F401
from Modulos.AlertaEstado import AlertaEstado  # noqa: F401

# Los mismos 4 imports "huerfanos" que ya tiene app.py (ver comentario ahi):
# no se usan directamente aqui tampoco, solo para que SQLAlchemy los registre.
from Modulos.Cartera import Cartera  # noqa: F401
from Modulos.Lecturas import Lecturas  # noqa: F401
from Modulos.Rentabilidad import Rentabilidad  # noqa: F401
from Modulos.Sedes import Sedes  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Usa la URL real de la app (base_de_datos.py) en vez del valor hardcodeado
# que trae alembic.ini por defecto, para que Alembic siempre apunte a la
# misma base de datos que usa la aplicacion.
config.set_main_option("sqlalchemy.url", URL_BASE_DATOS)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
