"""Tablas iniciales

Revision ID: efee06555c1c
Revises: 
Create Date: 2026-03-28 02:21:32.699392

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'efee06555c1c'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('rol',
    sa.Column('ro_codigo', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('ro_nombre', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('ro_codigo', name=op.f('rol_pkey')),
    sa.UniqueConstraint('ro_nombre', name=op.f('rol_ro_nombre_key'))
    )
    op.create_table('colonia',
    sa.Column('co_codigo', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('co_pais', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('co_departamento', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('co_ciudad', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('lider', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('co_codigo', name=op.f('colonia_pkey'))
    )
    op.create_table('usuario',
    sa.Column('us_codigo', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('us_fecha_creacion', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('us_tipo_doc', sa.Enum('CC', 'CE', name='tipodoc'), nullable=False),
    sa.Column('us_documento', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('us_celular', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('us_correo', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('us_contrasenia', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('co_codigo', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('ro_codigo', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('us_nombre', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('us_apellido', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('us_genero', sa.Enum('F', 'M', 'OTRO', name='genero'), nullable=False),
    sa.Column('us_fecha_nacimiento', sa.DATE(), autoincrement=False, nullable=False),
    sa.Column('us_pais', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('us_departamento', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('us_ciudad', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['co_codigo'], ['colonia.co_codigo'], name=op.f('usuario_co_codigo_fkey')),
    sa.ForeignKeyConstraint(['ro_codigo'], ['rol.ro_codigo'], name=op.f('usuario_ro_codigo_fkey')),
    sa.PrimaryKeyConstraint('us_codigo', name=op.f('usuario_pkey')),
    sa.UniqueConstraint('us_celular', name=op.f('usuario_us_celular_key')),
    sa.UniqueConstraint('us_correo', name=op.f('usuario_us_correo_key')),
    sa.UniqueConstraint('us_documento', name=op.f('usuario_us_documento_key'))
    )
    op.create_table('retorno',
    sa.Column('codigo', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('fecha_creacion', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('anio', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('estado', sa.Enum('ACTIVO', 'FINALIZADO', name='retornoestado'), nullable=False),
    sa.PrimaryKeyConstraint('codigo', name=op.f('retorno_pkey')),
    sa.UniqueConstraint('anio', name=op.f('uk2_retorno'))
    )
    op.create_index(op.f('ix_retorno_codigo'), 'retorno', ['codigo'], unique=False)
    op.create_table('parentesco',
    sa.Column('pa_codigo', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('pa_fecha_creacion', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('pa_estado', sa.Enum('pendiente', 'aceptada', 'rechazada', 'expirada', name='estadosolicitudparentesco'), nullable=False),
    sa.Column('us_codigo_solicitante', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('us_codigo_destinatario', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('pa_tipo_parentesco', sa.Enum('padre', 'madre', 'hermano', 'hijo', 'abuelo', 'tio', 'primo', 'madrastra', 'padrastro', 'hijastro', 'conyuge', name='tipoparentesco'), nullable=False),
    sa.ForeignKeyConstraint(['us_codigo_destinatario'], ['usuario.us_codigo'], name=op.f('parentesco_us_codigo_destinatario_fkey')),
    sa.ForeignKeyConstraint(['us_codigo_solicitante'], ['usuario.us_codigo'], name=op.f('parentesco_us_codigo_solicitante_fkey')),
    sa.PrimaryKeyConstraint('pa_codigo', name=op.f('parentesco_pkey'))
    )
    op.create_table('solicitud_colonia',
    sa.Column('so_codigo', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('us_codigo', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('co_codigo', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('so_estado', sa.Enum('pendiente', 'aceptada', 'rechazada', 'expirada', name='estadosolicitud'), nullable=False),
    sa.Column('so_fecha_creacion', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['co_codigo'], ['colonia.co_codigo'], name=op.f('solicitud_colonia_co_codigo_fkey')),
    sa.ForeignKeyConstraint(['us_codigo'], ['usuario.us_codigo'], name=op.f('solicitud_colonia_us_codigo_fkey')),
    sa.PrimaryKeyConstraint('so_codigo', name=op.f('solicitud_colonia_pkey'))
    )
    op.create_index(op.f('ix_solicitud_colonia_so_codigo'), 'solicitud_colonia', ['so_codigo'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_solicitud_colonia_so_codigo'), table_name='solicitud_colonia')
    op.drop_table('solicitud_colonia')
    op.drop_table('parentesco')
    op.drop_index(op.f('ix_retorno_codigo'), table_name='retorno')
    op.drop_table('retorno')
    op.drop_table('usuario')
    op.drop_table('colonia')
    op.drop_table('rol')
    
    # Opcional: Eliminar tipos ENUM de postgres si es necesario
    op.execute('DROP TYPE estadosolicitud')
    op.execute('DROP TYPE estadosolicitudparentesco')
    op.execute('DROP TYPE tipoparentesco')
    op.execute('DROP TYPE tipodoc')
    op.execute('DROP TYPE genero')
    op.execute('DROP TYPE retornoestado')
