import uuid as uuid_pkg
from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7


class UUIDMixin:
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        CHAR(36), primary_key=True, default=uuid7
    )


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(UTC), server_default=func.current_timestamp()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, onupdate=datetime.now(UTC), server_default=func.current_timestamp()
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
