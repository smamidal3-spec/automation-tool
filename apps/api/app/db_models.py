from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True)
    role: Mapped[str] = mapped_column(String(32), index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    repo: Mapped[str] = mapped_column(String(256), index=True)
    file_path: Mapped[str] = mapped_column(String(256), index=True)
    key_path: Mapped[str] = mapped_column(String(256), index=True)
    old_value: Mapped[str] = mapped_column(Text)
    new_value: Mapped[str] = mapped_column(Text)
    pull_request_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
