from src.db.base import Base
from .association_table import voters_association_table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime
from datetime import datetime
from typing import List

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .vote_topics_model import VoteTopicModel
    from .refresh_token_model import RefreshTokenModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(300), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False
    )

    created_vote_topics: Mapped[List["VoteTopicModel"]] = relationship(
        back_populates="creator"
    )

    voted_vote_topics: Mapped[List["VoteTopicModel"]] = relationship(
        secondary=voters_association_table, back_populates="voters"
    )

    refresh_tokens: Mapped[List["RefreshTokenModel"]] = relationship(
        back_populates="author_user"
    )
