"""initial migration

Revision ID: 6d43b626df7b
Revises: 
Create Date: 2023-02-01 09:46:09.240783

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import table

# revision identifiers, used by Alembic.
revision = '6d43b626df7b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('telegram_id', sa.BIGINT(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('telegram_id')
    )
    op.create_table('channel_photos',
    sa.Column('photo_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('file_id', sa.TEXT(), nullable=False),
    sa.PrimaryKeyConstraint('photo_id')
    )

    op.execute(table('admins', sa.Column('telegram_id', sa.BIGINT(),
                                         nullable=False)).insert().values(telegram_id=459553073))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('channel_photos')
    op.drop_table('admins')
    # ### end Alembic commands ###
