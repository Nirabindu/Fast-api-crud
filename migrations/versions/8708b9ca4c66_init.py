"""init

Revision ID: 8708b9ca4c66
Revises: 4cd7de2fd4ef
Create Date: 2024-12-11 18:36:06.302317

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

"""
importing sqlmodel
"""
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "8708b9ca4c66"
down_revision: Union[str, None] = "4cd7de2fd4ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "books", ["uid"])
    op.create_unique_constraint(None, "users", ["uid"])
    op.drop_column("users", "is_active")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=False),
    )
    op.drop_constraint(None, "users", type_="unique")
    op.drop_constraint(None, "books", type_="unique")
    # ### end Alembic commands ###
