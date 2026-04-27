"""initial tables

Revision ID: 001_initial
Revises:
Create Date: 2025-04-27

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # ── volunteers ─────────────────────────────────────────────────────────────
    op.create_table(
        "volunteers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cpf", sa.String(14), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column(
            "type",
            sa.Enum("permanent", "freelancer", name="volunteertype"),
            nullable=False,
            server_default="freelancer",
        ),
        sa.Column("skills", sa.JSON(), nullable=True),
        sa.Column("availability", sa.JSON(), nullable=True),
        sa.Column("carfo_profile", sa.JSON(), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("latitude", sa.String(20), nullable=True),
        sa.Column("longitude", sa.String(20), nullable=True),
        sa.Column("points", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("open_to_rotation", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_volunteers_id", "volunteers", ["id"])
    op.create_index("ix_volunteers_cpf", "volunteers", ["cpf"], unique=True)
    op.create_index("ix_volunteers_email", "volunteers", ["email"], unique=True)

    # ── institutions ───────────────────────────────────────────────────────────
    op.create_table(
        "institutions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cnpj", sa.String(18), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("email", sa.String(200), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column(
            "type",
            sa.Enum("ngo", "government", "religious", "health", "crisis", "other", name="institutiontype"),
            nullable=False,
            server_default="ngo",
        ),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("address", sa.String(300), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_institutions_id", "institutions", ["id"])
    op.create_index("ix_institutions_cnpj", "institutions", ["cnpj"], unique=True)
    op.create_index("ix_institutions_email", "institutions", ["email"], unique=True)

    # ── needs ──────────────────────────────────────────────────────────────────
    op.create_table(
        "needs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("institution_id", sa.Integer(), nullable=False),
        sa.Column("required_skills", sa.JSON(), nullable=True),
        sa.Column("volunteers_needed", sa.Integer(), nullable=True, server_default="1"),
        sa.Column(
            "urgency",
            sa.Enum("low", "medium", "high", "critical", name="urgencylevel"),
            nullable=True,
            server_default="medium",
        ),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state", sa.String(2), nullable=True),
        sa.Column("address", sa.String(300), nullable=True),
        sa.Column("start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "status",
            sa.Enum("open", "in_progress", "completed", "cancelled", name="needstatus"),
            nullable=False,
            server_default="open",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_needs_id", "needs", ["id"])

    # ── matches ────────────────────────────────────────────────────────────────
    op.create_table(
        "matches",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("volunteer_id", sa.Integer(), nullable=False),
        sa.Column("need_id", sa.Integer(), nullable=False),
        sa.Column("score", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column(
            "status",
            sa.Enum("suggested", "accepted", "rejected", "completed", "no_show", name="matchstatus"),
            nullable=False,
            server_default="suggested",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("responded_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["need_id"], ["needs.id"]),
        sa.ForeignKeyConstraint(["volunteer_id"], ["volunteers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_matches_id", "matches", ["id"])

    # ── task_history ───────────────────────────────────────────────────────────
    op.create_table(
        "task_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("match_id", sa.Integer(), nullable=False),
        sa.Column("hours_worked", sa.Float(), nullable=True, server_default="0.0"),
        sa.Column("feedback_score", sa.Integer(), nullable=True),
        sa.Column("feedback_text", sa.Text(), nullable=True),
        sa.Column("points_earned", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("completed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["match_id"], ["matches.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_history_id", "task_history", ["id"])

    # ── rewards ────────────────────────────────────────────────────────────────
    op.create_table(
        "rewards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("volunteer_id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.Enum("leisure", "maintenance", "course", "merchandise", "other", name="rewardtype"),
            nullable=False,
            server_default="other",
        ),
        sa.Column("description", sa.String(300), nullable=False),
        sa.Column("points_spent", sa.Integer(), nullable=False),
        sa.Column("redeemed_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["volunteer_id"], ["volunteers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rewards_id", "rewards", ["id"])

    # ── alerts ─────────────────────────────────────────────────────────────────
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("volunteer_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.String(500), nullable=False),
        sa.Column(
            "type",
            sa.Enum("info", "warning", "emergency", "wellbeing", name="alerttype"),
            nullable=False,
            server_default="info",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["volunteer_id"], ["volunteers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_alerts_id", "alerts", ["id"])

    # ── feedbacks ──────────────────────────────────────────────────────────────
    op.create_table(
        "feedbacks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("volunteer_id", sa.Integer(), nullable=False),
        sa.Column("need_id", sa.Integer(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["need_id"], ["needs.id"]),
        sa.ForeignKeyConstraint(["volunteer_id"], ["volunteers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feedbacks_id", "feedbacks", ["id"])

    # ── interests ──────────────────────────────────────────────────────────────
    op.create_table(
        "interests",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("volunteer_id", sa.Integer(), nullable=False),
        sa.Column("need_id", sa.Integer(), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "voluntario_para_necessidade",
                "instituicao_para_voluntario",
                name="interesttype",
            ),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("pending", "mutual", name="intereststatus"),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["need_id"], ["needs.id"]),
        sa.ForeignKeyConstraint(["volunteer_id"], ["volunteers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_interests_id", "interests", ["id"])


def downgrade() -> None:
    op.drop_table("interests")
    op.drop_table("feedbacks")
    op.drop_table("alerts")
    op.drop_table("rewards")
    op.drop_table("task_history")
    op.drop_table("matches")
    op.drop_table("needs")
    op.drop_table("institutions")
    op.drop_table("volunteers")

    # Remove os tipos ENUM do PostgreSQL
    op.execute("DROP TYPE IF EXISTS intereststatus")
    op.execute("DROP TYPE IF EXISTS interesttype")
    op.execute("DROP TYPE IF EXISTS alerttype")
    op.execute("DROP TYPE IF EXISTS rewardtype")
    op.execute("DROP TYPE IF EXISTS matchstatus")
    op.execute("DROP TYPE IF EXISTS needstatus")
    op.execute("DROP TYPE IF EXISTS urgencylevel")
    op.execute("DROP TYPE IF EXISTS institutiontype")
    op.execute("DROP TYPE IF EXISTS volunteertype")