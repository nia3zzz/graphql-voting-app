from . import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from uuid import UUID, uuid4


class VoteModel(Base):
    __tablename__ = "votes_options"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    vote_option: Mapped[str] = mapped_column(String(100), nullable=False)
    vote_count: Mapped[int] = mapped_column(nullable=False, default=0)
    vote_topic_id: Mapped[UUID] = mapped_column(
        ForeignKey("vote_topics.id"), nullable=False
    )

    vote_topic = relationship("VoteTopicModel", back_populates="voting_options")
