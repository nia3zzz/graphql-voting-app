from src.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime
from uuid import UUID, uuid4
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users_model import UserModel


class RefreshTokenModel(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(500), nullable=False)
    last_used_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False
    )

    author_user: Mapped["UserModel"] = relationship(back_populates="refresh_tokens")
