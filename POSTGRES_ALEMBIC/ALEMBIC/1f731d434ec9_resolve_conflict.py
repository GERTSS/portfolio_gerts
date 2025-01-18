"""resolve conflict

Revision ID: 1f731d434ec9
Revises: 2083ca7ab9ea, 7720a72d6cb5
Create Date: 2024-12-27 19:50:35.291406

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1f731d434ec9'
down_revision: Union[str, None] = ('2083ca7ab9ea', '7720a72d6cb5')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
