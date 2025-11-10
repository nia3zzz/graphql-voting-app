from src.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, DateTime
from uuid import UUID, uuid4
from datetime import datetime


class VoteModel(Base):
    __tablename__ = "votes_options"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    vote_option: Mapped[str] = mapped_column(String(100), nullable=False)
    vote_count: Mapped[int] = mapped_column(nullable=False, default=0)
    vote_topic_id: Mapped[UUID] = mapped_column(
        ForeignKey("vote_topics.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), onupdate=datetime.now(), nullable=False
    )

    vote_topic = relationship("VoteTopicModel", back_populates="voting_options")
