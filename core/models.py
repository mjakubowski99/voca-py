from typing import Optional
import datetime
import decimal
import uuid

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Computed,
    Double,
    ForeignKeyConstraint,
    Index,
    Integer,
    JSON,
    Numeric,
    PrimaryKeyConstraint,
    Sequence,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    Uuid,
    text,
)
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column


class Base(DeclarativeBase):
    pass


class Admins(Base):
    __tablename__ = "admins"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="admins_pkey"),
        UniqueConstraint("email", name="admins_email_unique"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email_verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    remember_token: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))

    flashcard_decks: Mapped[list["FlashcardDecks"]] = relationship(
        "FlashcardDecks", back_populates="admin"
    )
    flashcards: Mapped[list["Flashcards"]] = relationship("Flashcards", back_populates="admin")


class Exercises(Base):
    __tablename__ = "exercises"
    __table_args__ = (PrimaryKeyConstraint("id", name="exercises_pkey"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    exercise_type: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    status: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    properties: Mapped[Optional[dict]] = mapped_column(JSON)

    exercise_entries: Mapped[list["ExerciseEntries"]] = relationship(
        "ExerciseEntries", back_populates="exercise"
    )


class FailedJobs(Base):
    __tablename__ = "failed_jobs"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="failed_jobs_pkey"),
        UniqueConstraint("uuid", name="failed_jobs_uuid_unique"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    uuid: Mapped[str] = mapped_column(String(255), nullable=False)
    connection: Mapped[str] = mapped_column(Text, nullable=False)
    queue: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    exception: Mapped[str] = mapped_column(Text, nullable=False)
    failed_at: Mapped[datetime.datetime] = mapped_column(
        TIMESTAMP(precision=0), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class Migrations(Base):
    __tablename__ = "migrations"
    __table_args__ = (PrimaryKeyConstraint("id", name="migrations_pkey"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    migration: Mapped[str] = mapped_column(String(255), nullable=False)
    batch: Mapped[int] = mapped_column(Integer, nullable=False)


class PasswordResetTokens(Base):
    __tablename__ = "password_reset_tokens"
    __table_args__ = (PrimaryKeyConstraint("email", name="password_reset_tokens_pkey"),)

    email: Mapped[str] = mapped_column(String(255), primary_key=True)
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))


class PersonalAccessTokens(Base):
    __tablename__ = "personal_access_tokens"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="personal_access_tokens_pkey"),
        UniqueConstraint("token", name="personal_access_tokens_token_unique"),
        Index(
            "personal_access_tokens_tokenable_type_tokenable_id_index",
            "tokenable_type",
            "tokenable_id",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    tokenable_type: Mapped[str] = mapped_column(String(255), nullable=False)
    tokenable_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    token: Mapped[str] = mapped_column(String(64), nullable=False)
    abilities: Mapped[Optional[str]] = mapped_column(Text)
    last_used_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    expires_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))


class PulseAggregates(Base):
    __tablename__ = "pulse_aggregates"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pulse_aggregates_pkey"),
        UniqueConstraint(
            "bucket",
            "period",
            "type",
            "aggregate",
            "key_hash",
            name="pulse_aggregates_bucket_period_type_aggregate_key_hash_unique",
        ),
        Index("pulse_aggregates_period_bucket_index", "period", "bucket"),
        Index(
            "pulse_aggregates_period_type_aggregate_bucket_index",
            "period",
            "type",
            "aggregate",
            "bucket",
        ),
        Index("pulse_aggregates_type_index", "type"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    bucket: Mapped[int] = mapped_column(Integer, nullable=False)
    period: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(Text, nullable=False)
    key_hash: Mapped[uuid.UUID] = mapped_column(
        Uuid, Computed("(md5(key))::uuid", persisted=True), nullable=False
    )
    aggregate: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[decimal.Decimal] = mapped_column(Numeric(20, 2), nullable=False)
    count: Mapped[Optional[int]] = mapped_column(Integer)


class PulseEntries(Base):
    __tablename__ = "pulse_entries"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pulse_entries_pkey"),
        Index("pulse_entries_key_hash_index", "key_hash"),
        Index("pulse_entries_timestamp_index", "timestamp"),
        Index(
            "pulse_entries_timestamp_type_key_hash_value_index",
            "timestamp",
            "type",
            "key_hash",
            "value",
        ),
        Index("pulse_entries_type_index", "type"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(Text, nullable=False)
    key_hash: Mapped[uuid.UUID] = mapped_column(
        Uuid, Computed("(md5(key))::uuid", persisted=True), nullable=False
    )
    value: Mapped[Optional[int]] = mapped_column(BigInteger)


class PulseValues(Base):
    __tablename__ = "pulse_values"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="pulse_values_pkey"),
        UniqueConstraint("type", "key_hash", name="pulse_values_type_key_hash_unique"),
        Index("pulse_values_timestamp_index", "timestamp"),
        Index("pulse_values_type_index", "type"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    timestamp: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(Text, nullable=False)
    key_hash: Mapped[uuid.UUID] = mapped_column(
        Uuid, Computed("(md5(key))::uuid", persisted=True), nullable=False
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)


class Stories(Base):
    __tablename__ = "stories"
    __table_args__ = (PrimaryKeyConstraint("id", name="stories_pkey"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))

    story_flashcards: Mapped[list["StoryFlashcards"]] = relationship(
        "StoryFlashcards", back_populates="story"
    )


class Users(Base):
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="users_pkey"),
        UniqueConstraint("email", name="users_email_unique"),
        UniqueConstraint(
            "provider_id", "provider_type", name="users_provider_id_provider_type_unique"
        ),
        Index("users_provider_id_provider_type_index", "provider_id", "provider_type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    user_language: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default=text("'pl'::character varying")
    )
    learning_language: Mapped[str] = mapped_column(
        String(3), nullable=False, server_default=text("'en'::character varying")
    )
    profile_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    email_verified_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    provider_id: Mapped[Optional[str]] = mapped_column(String(255))
    provider_type: Mapped[Optional[str]] = mapped_column(String(255))
    picture: Mapped[Optional[str]] = mapped_column(String(255))
    remember_token: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))

    flashcard_decks: Mapped[list["FlashcardDecks"]] = relationship(
        "FlashcardDecks", back_populates="user"
    )
    reports: Mapped[list["Reports"]] = relationship("Reports", back_populates="user")
    flashcard_deck_activities: Mapped[list["FlashcardDeckActivities"]] = relationship(
        "FlashcardDeckActivities", back_populates="user"
    )
    flashcards: Mapped[list["Flashcards"]] = relationship("Flashcards", back_populates="user")
    learning_sessions: Mapped[list["LearningSessions"]] = relationship(
        "LearningSessions", back_populates="user"
    )
    flashcard_poll_items: Mapped[list["FlashcardPollItems"]] = relationship(
        "FlashcardPollItems", back_populates="user"
    )
    sm_two_flashcards: Mapped[list["SmTwoFlashcards"]] = relationship(
        "SmTwoFlashcards", back_populates="user"
    )
    phone = Column(String(20))


class ExerciseEntries(Base):
    __tablename__ = "exercise_entries"
    __table_args__ = (
        ForeignKeyConstraint(
            ["exercise_id"],
            ["exercises.id"],
            ondelete="CASCADE",
            name="exercise_entries_exercise_id_foreign",
        ),
        PrimaryKeyConstraint("id", name="exercise_entries_pkey"),
        Index("exercise_entries_exercise_id_index", "exercise_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    exercise_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[float] = mapped_column(
        Double(53), nullable=False, server_default=text("'0'::double precision")
    )
    answers_count: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("'0'::smallint")
    )
    order: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("'0'::smallint")
    )
    last_answer: Mapped[Optional[str]] = mapped_column(String(255))
    last_answer_correct: Mapped[Optional[bool]] = mapped_column(Boolean)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))

    exercise: Mapped["Exercises"] = relationship("Exercises", back_populates="exercise_entries")


class FlashcardDecks(Base):
    __tablename__ = "flashcard_decks"
    __table_args__ = (
        CheckConstraint(
            "admin_id IS NOT NULL AND user_id IS NULL OR admin_id IS NULL AND user_id IS NOT NULL",
            name="check_flashcard_decks_user_id_admin_id_both_not_null",
        ),
        ForeignKeyConstraint(["admin_id"], ["admins.id"], name="flashcard_decks_admin_id_foreign"),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="flashcard_categories_user_id_foreign",
        ),
        PrimaryKeyConstraint("id", name="flashcard_categories_pkey"),
        Index("flashcard_categories_user_id_index", "user_id"),
    )

    id: Mapped[int] = mapped_column(
        BigInteger, Sequence("flashcard_categories_id_seq"), primary_key=True
    )
    tag: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_language_level: Mapped[str] = mapped_column(
        String(255), nullable=False, server_default=text("'B2'::character varying")
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)

    admin: Mapped[Optional["Admins"]] = relationship("Admins", back_populates="flashcard_decks")
    user: Mapped[Optional["Users"]] = relationship("Users", back_populates="flashcard_decks")
    flashcard_deck_activities: Mapped[list["FlashcardDeckActivities"]] = relationship(
        "FlashcardDeckActivities", back_populates="flashcard_deck"
    )
    flashcards: Mapped[list["Flashcards"]] = relationship(
        "Flashcards", back_populates="flashcard_deck"
    )
    learning_sessions: Mapped[list["LearningSessions"]] = relationship(
        "LearningSessions", back_populates="flashcard_deck"
    )


class Reports(Base):
    __tablename__ = "reports"
    __table_args__ = (
        ForeignKeyConstraint(["user_id"], ["users.id"], name="reports_user_id_foreign"),
        PrimaryKeyConstraint("id", name="reports_pkey"),
        Index("reports_reportable_id_reportable_type_index", "reportable_id", "reportable_type"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    type: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    reportable_id: Mapped[Optional[str]] = mapped_column(String(255))
    reportable_type: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))

    user: Mapped[Optional["Users"]] = relationship("Users", back_populates="reports")


class FlashcardDeckActivities(Base):
    __tablename__ = "flashcard_deck_activities"
    __table_args__ = (
        ForeignKeyConstraint(
            ["flashcard_deck_id"],
            ["flashcard_decks.id"],
            ondelete="CASCADE",
            name="flashcard_deck_activities_flashcard_deck_id_foreign",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="flashcard_deck_activities_user_id_foreign",
        ),
        PrimaryKeyConstraint("id", name="flashcard_deck_activities_pkey"),
        UniqueConstraint(
            "user_id",
            "flashcard_deck_id",
            name="flashcard_deck_activities_user_id_flashcard_deck_id_unique",
        ),
        Index("flashcard_deck_activities_flashcard_deck_id_index", "flashcard_deck_id"),
        Index("flashcard_deck_activities_user_id_index", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    flashcard_deck_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    last_viewed_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))

    flashcard_deck: Mapped["FlashcardDecks"] = relationship(
        "FlashcardDecks", back_populates="flashcard_deck_activities"
    )
    user: Mapped["Users"] = relationship("Users", back_populates="flashcard_deck_activities")


class Flashcards(Base):
    __tablename__ = "flashcards"
    __table_args__ = (
        CheckConstraint(
            "admin_id IS NOT NULL AND user_id IS NULL OR admin_id IS NULL AND user_id IS NOT NULL",
            name="check_flashcards_user_id_admin_id_both_not_null",
        ),
        ForeignKeyConstraint(["admin_id"], ["admins.id"], name="flashcards_admin_id_foreign"),
        ForeignKeyConstraint(
            ["flashcard_deck_id"],
            ["flashcard_decks.id"],
            ondelete="CASCADE",
            name="flashcards_flashcard_deck_id_foreign",
        ),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="flashcards_user_id_foreign"),
        PrimaryKeyConstraint("id", name="flashcards_pkey"),
        Index("flashcards_flashcard_category_id_index", "flashcard_deck_id"),
        Index("flashcards_user_id_index", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    front_word: Mapped[str] = mapped_column(String(255), nullable=False)
    front_lang: Mapped[str] = mapped_column(String(5), nullable=False)
    back_word: Mapped[str] = mapped_column(String(255), nullable=False)
    back_lang: Mapped[str] = mapped_column(String(255), nullable=False)
    front_context: Mapped[str] = mapped_column(String(255), nullable=False)
    back_context: Mapped[str] = mapped_column(String(255), nullable=False)
    language_level: Mapped[str] = mapped_column(
        String(255), nullable=False, server_default=text("'B2'::character varying")
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    flashcard_deck_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    admin_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    emoji: Mapped[Optional[str]] = mapped_column(String(255))

    admin: Mapped[Optional["Admins"]] = relationship("Admins", back_populates="flashcards")
    flashcard_deck: Mapped[Optional["FlashcardDecks"]] = relationship(
        "FlashcardDecks", back_populates="flashcards"
    )
    user: Mapped[Optional["Users"]] = relationship("Users", back_populates="flashcards")
    flashcard_poll_items: Mapped[list["FlashcardPollItems"]] = relationship(
        "FlashcardPollItems", back_populates="flashcard"
    )
    learning_session_flashcards: Mapped[list["LearningSessionFlashcards"]] = relationship(
        "LearningSessionFlashcards", back_populates="flashcard"
    )
    sm_two_flashcards: Mapped[list["SmTwoFlashcards"]] = relationship(
        "SmTwoFlashcards", back_populates="flashcard"
    )
    story_flashcards: Mapped[list["StoryFlashcards"]] = relationship(
        "StoryFlashcards", back_populates="flashcard"
    )


class LearningSessions(Base):
    __tablename__ = "learning_sessions"
    __table_args__ = (
        ForeignKeyConstraint(
            ["flashcard_deck_id"],
            ["flashcard_decks.id"],
            ondelete="CASCADE",
            name="learning_sessions_flashcard_deck_id_foreign",
        ),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="learning_sessions_user_id_foreign"),
        PrimaryKeyConstraint("id", name="learning_sessions_pkey"),
        Index("learning_sessions_flashcard_category_id_index", "flashcard_deck_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    status: Mapped[str] = mapped_column(String(255), nullable=False)
    device: Mapped[str] = mapped_column(String(255), nullable=False)
    cards_per_session: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    type: Mapped[str] = mapped_column(
        String(255), nullable=False, server_default=text("'flashcard'::character varying")
    )
    flashcard_deck_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))

    flashcard_deck: Mapped[Optional["FlashcardDecks"]] = relationship(
        "FlashcardDecks", back_populates="learning_sessions"
    )
    user: Mapped["Users"] = relationship("Users", back_populates="learning_sessions")
    learning_session_flashcards: Mapped[list["LearningSessionFlashcards"]] = relationship(
        "LearningSessionFlashcards", back_populates="learning_session"
    )


class FlashcardPollItems(Base):
    __tablename__ = "flashcard_poll_items"
    __table_args__ = (
        ForeignKeyConstraint(
            ["flashcard_id"],
            ["flashcards.id"],
            ondelete="CASCADE",
            name="flashcard_poll_items_flashcard_id_foreign",
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
            name="flashcard_poll_items_user_id_foreign",
        ),
        PrimaryKeyConstraint("id", name="flashcard_poll_items_pkey"),
        Index("flashcard_poll_items_flashcard_id_index", "flashcard_id"),
        Index("flashcard_poll_items_user_id_index", "user_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    flashcard_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    easy_ratings_count: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("'0'::smallint")
    )
    easy_ratings_count_to_purge: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("'0'::smallint")
    )
    leitner_level: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))

    flashcard: Mapped["Flashcards"] = relationship(
        "Flashcards", back_populates="flashcard_poll_items"
    )
    user: Mapped["Users"] = relationship("Users", back_populates="flashcard_poll_items")


class LearningSessionFlashcards(Base):
    __tablename__ = "learning_session_flashcards"
    __table_args__ = (
        ForeignKeyConstraint(
            ["flashcard_id"],
            ["flashcards.id"],
            ondelete="CASCADE",
            name="learning_session_flashcards_flashcard_id_foreign",
        ),
        ForeignKeyConstraint(
            ["learning_session_id"],
            ["learning_sessions.id"],
            ondelete="CASCADE",
            name="learning_session_flashcards_learning_session_id_foreign",
        ),
        PrimaryKeyConstraint("id", name="learning_session_flashcards_pkey"),
        Index("learning_session_flashcards_exercise_entry_id_index", "exercise_entry_id"),
        Index("learning_session_flashcards_flashcard_id_index", "flashcard_id"),
        Index("learning_session_flashcards_learning_session_id_index", "learning_session_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    learning_session_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    flashcard_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    is_additional: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    rating: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    exercise_entry_id: Mapped[Optional[int]] = mapped_column(BigInteger)
    exercise_type: Mapped[Optional[int]] = mapped_column(SmallInteger)

    flashcard: Mapped["Flashcards"] = relationship(
        "Flashcards", back_populates="learning_session_flashcards"
    )
    learning_session: Mapped["LearningSessions"] = relationship(
        "LearningSessions", back_populates="learning_session_flashcards"
    )


class SmTwoFlashcards(Base):
    __tablename__ = "sm_two_flashcards"
    __table_args__ = (
        ForeignKeyConstraint(
            ["flashcard_id"],
            ["flashcards.id"],
            ondelete="CASCADE",
            name="sm_two_flashcards_flashcard_id_foreign",
        ),
        ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", name="sm_two_flashcards_user_id_foreign"
        ),
        PrimaryKeyConstraint("user_id", "flashcard_id", name="sm_two_flashcards_pkey"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    flashcard_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    repetition_ratio: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    repetition_interval: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 6), nullable=False)
    repetition_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    min_rating: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    repetitions_in_session: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, server_default=text("'0'::smallint")
    )
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    last_rating: Mapped[Optional[int]] = mapped_column(SmallInteger)

    flashcard: Mapped["Flashcards"] = relationship("Flashcards", back_populates="sm_two_flashcards")
    user: Mapped["Users"] = relationship("Users", back_populates="sm_two_flashcards")


class StoryFlashcards(Base):
    __tablename__ = "story_flashcards"
    __table_args__ = (
        ForeignKeyConstraint(
            ["flashcard_id"],
            ["flashcards.id"],
            ondelete="CASCADE",
            name="story_flashcards_flashcard_id_foreign",
        ),
        ForeignKeyConstraint(
            ["story_id"],
            ["stories.id"],
            ondelete="CASCADE",
            name="story_flashcards_story_id_foreign",
        ),
        PrimaryKeyConstraint("id", name="story_flashcards_pkey"),
        Index("story_flashcards_flashcard_id_index", "flashcard_id"),
        Index("story_flashcards_story_id_index", "story_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    story_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    flashcard_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    sentence_override: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP(precision=0))

    flashcard: Mapped["Flashcards"] = relationship("Flashcards", back_populates="story_flashcards")
    story: Mapped["Stories"] = relationship("Stories", back_populates="story_flashcards")
