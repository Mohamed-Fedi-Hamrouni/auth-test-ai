import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from auth_test_ai.extensions import db


def utc_now() -> datetime:
    return datetime.now(UTC)


class AuthenticationFailureReason(StrEnum):
    SUCCESS = "SUCCESS"
    UNKNOWN_LOGIN = "UNKNOWN_LOGIN"
    INVALID_PASSWORD = "INVALID_PASSWORD"
    ACCOUNT_INACTIVE = "ACCOUNT_INACTIVE"
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"
    RATE_LIMITED = "RATE_LIMITED"


class User(db.Model):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("failed_login_count >= 0", name="ck_users_failed_count"),
        Index("ix_users_active_locked", "is_active", "locked_until"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    login: Mapped[str] = mapped_column(String(100))
    login_normalized: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(512))
    is_active: Mapped[bool] = mapped_column(default=True)
    failed_login_count: Mapped[int] = mapped_column(default=0)
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
    roles: Mapped[list["Role"]] = relationship(
        secondary="user_roles", back_populates="users", lazy="selectin"
    )
    authentication_attempts: Mapped[list["AuthenticationAttempt"]] = relationship(
        back_populates="user"
    )

    def to_public_dict(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "firstName": self.first_name,
            "lastName": self.last_name,
            "login": self.login,
            "roles": sorted(role.name for role in self.roles),
            "isActive": self.is_active,
        }

    def __repr__(self) -> str:
        return f"<User id={self.id}>"


class Role(db.Model):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(32), unique=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    users: Mapped[list[User]] = relationship(
        secondary="user_roles", back_populates="roles", viewonly=True
    )

    def __repr__(self) -> str:
        return f"<Role name={self.name}>"


class UserRole(db.Model):
    __tablename__ = "user_roles"

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True
    )
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


class AuthenticationAttempt(db.Model):
    __tablename__ = "authentication_attempts"
    __table_args__ = (
        Index("ix_auth_attempt_user_created", "user_id", "created_at"),
        Index("ix_auth_attempt_success_created", "success", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    attempted_login: Mapped[str] = mapped_column(String(100))
    success: Mapped[bool]
    internal_failure_reason: Mapped[str] = mapped_column(String(32))
    ip_address_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, index=True
    )
    user: Mapped[User | None] = relationship(back_populates="authentication_attempts")

    def to_audit_dict(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "userId": str(self.user_id) if self.user_id else None,
            "attemptedLogin": self.attempted_login,
            "success": self.success,
            "createdAt": self.created_at.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<AuthenticationAttempt id={self.id} success={self.success}>"
