from src.db.base import Base
from .association_table import voters_association_table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey
from uuid import UUID, uuid4
from typing import List


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .users_model import UserModel
    from .votes import VoteModel


class VoteTopicModel(Base):
    __tablename__ = "vote_topics"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    description: Mapped[str] = mapped_column(String(300), nullable=False)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    creator: Mapped["UserModel"] = relationship(back_populates="created_vote_topics")
    voters: Mapped[List["UserModel"]] = relationship(
        secondary=voters_association_table, back_populates="voted_vote_topics"
    )

    voting_options: Mapped[List["VoteModel"]] = relationship(
        back_populates="vote_topic"
    )
