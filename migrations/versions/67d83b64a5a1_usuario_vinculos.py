"""usuario vinculos

Revision ID: 67d83b64a5a1
Revises: 313c4aace741
Create Date: 2025-08-16 16:21:16.552737

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '67d83b64a5a1'
down_revision = '313c4aace741'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('usuario', schema=None) as batch_op:
        batch_op.add_column(sa.Column('paciente_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('profissional_id', sa.Integer(), nullable=True))

        batch_op.create_index('ix_usuario_paciente_id', ['paciente_id'])
        batch_op.create_index('ix_usuario_profissional_id', ['profissional_id'])

        batch_op.create_foreign_key(
            'fk_usuario_paciente_id_paciente',
            'paciente',
            ['paciente_id'], ['id'],
            ondelete=None
        )
        batch_op.create_foreign_key(
            'fk_usuario_profissional_id_profissional',
            'profissional',
            ['profissional_id'], ['id'],
            ondelete=None
        )

def downgrade():
    with op.batch_alter_table('usuario', schema=None) as batch_op:
        # derruba FKs/IX antes de remover colunas
        batch_op.drop_constraint('fk_usuario_profissional_id_profissional', type_='foreignkey')
        batch_op.drop_constraint('fk_usuario_paciente_id_paciente', type_='foreignkey')
        batch_op.drop_index('ix_usuario_profissional_id')
        batch_op.drop_index('ix_usuario_paciente_id')

        batch_op.drop_column('profissional_id')
        batch_op.drop_column('paciente_id')


    # ### end Alembic commands ###
