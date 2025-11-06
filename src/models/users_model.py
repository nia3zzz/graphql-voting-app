from . import Base, voters_association_table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid import UUID, uuid4
from sqlalchemy import String
from typing import List
from .vote_topics import VoteTopicModel


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(30), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(300), nullable=False)

    created_vote_topics: Mapped[List["VoteTopicModel"]] = relationship(
        back_populates="creator"
    )

    voted_vote_topics: Mapped[List["VoteTopicModel"]] = relationship(
        secondary=voters_association_table, back_populates="voters"
    )
