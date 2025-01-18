"""conflict

Revision ID: 2083ca7ab9ea
Revises: 7720a72d6cb5
Create Date: 2024-12-27 19:44:14.709697

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2083ca7ab9ea'
down_revision: Union[str, None] = '2e1a6673a07f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('patronomic', sa.String(length=50), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'patronomic')
    # ### end Alembic commands ###