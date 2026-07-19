"""Add an opaque user-provided lesson kind."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_lesson_kind"
down_revision: str | None = "0001_mvp_gradebook"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("lessons") as batch_op:
        batch_op.add_column(sa.Column("kind", sa.String(20), nullable=False, server_default="practice"))


def downgrade() -> None:
    with op.batch_alter_table("lessons") as batch_op:
        batch_op.drop_column("kind")
