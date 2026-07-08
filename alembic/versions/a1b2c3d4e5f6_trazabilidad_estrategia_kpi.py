"""trazabilidad: estrategia.matriz_id, indicador_cmi.kpi_id

Revision ID: a1b2c3d4e5f6
Revises: 7c3f6280e8d5
Create Date: 2026-07-07 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '7c3f6280e8d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: enlaces de trazabilidad matriz→estrategia y kpi→indicador_cmi."""
    with op.batch_alter_table('estrategia') as batch:
        batch.add_column(sa.Column('matriz_id', sa.Integer(), nullable=True))
        batch.create_foreign_key(
            'fk_estrategia_matriz', 'matriz', ['matriz_id'], ['id']
        )
    with op.batch_alter_table('indicador_cmi') as batch:
        batch.add_column(sa.Column('kpi_id', sa.Integer(), nullable=True))
        batch.create_foreign_key(
            'fk_indicador_cmi_kpi', 'indicador', ['kpi_id'], ['id']
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('indicador_cmi') as batch:
        batch.drop_constraint('fk_indicador_cmi_kpi', type_='foreignkey')
        batch.drop_column('kpi_id')
    with op.batch_alter_table('estrategia') as batch:
        batch.drop_constraint('fk_estrategia_matriz', type_='foreignkey')
        batch.drop_column('matriz_id')
