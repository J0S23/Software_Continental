"""agregar notas_internas a clientes

Revision ID: f34714ea9ba5
Revises: 161f682239e7
Create Date: 2026-08-03 00:21:59.167430

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f34714ea9ba5'
down_revision: Union[str, Sequence[str], None] = '161f682239e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Editado a mano: autogenerate tambien detecto el drift preexistente
    # entre continental_app.db y los modelos (7 tablas legacy sin modelo
    # Python, y columnas agregadas en refactors anteriores nunca migradas).
    # Ese drift se deja pendiente para una migracion aparte, deliberada;
    # esta migracion solo agrega la columna nueva.
    op.add_column('clientes', sa.Column('notas_internas', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('clientes', 'notas_internas')
