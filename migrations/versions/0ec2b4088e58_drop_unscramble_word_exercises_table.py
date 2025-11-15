"""drop unscramble word exercises table

Revision ID: 0ec2b4088e58
Revises: 69fff129170a
Create Date: 2025-11-15 16:05:17.173303

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0ec2b4088e58"
down_revision: Union[str, Sequence[str], None] = "69fff129170a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_index(
        op.f("unscramble_word_exercises_exercise_id_index"), table_name="unscramble_word_exercises"
    )
    op.drop_table("unscramble_word_exercises")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        "unscramble_word_exercises",
        sa.Column("id", sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column("exercise_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column("word", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("scrambled_word", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("context_sentence", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("word_translation", sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column("emoji", sa.VARCHAR(length=255), autoincrement=False, nullable=True),
        sa.Column(
            "created_at", postgresql.TIMESTAMP(precision=0), autoincrement=False, nullable=True
        ),
        sa.Column(
            "updated_at", postgresql.TIMESTAMP(precision=0), autoincrement=False, nullable=True
        ),
        sa.Column(
            "context_sentence_translation",
            sa.VARCHAR(length=255),
            autoincrement=False,
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["exercise_id"],
            ["exercises.id"],
            name=op.f("unscramble_word_exercises_exercise_id_foreign"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("unscramble_word_exercises_pkey")),
    )
    op.create_index(
        op.f("unscramble_word_exercises_exercise_id_index"),
        "unscramble_word_exercises",
        ["exercise_id"],
        unique=False,
    )
