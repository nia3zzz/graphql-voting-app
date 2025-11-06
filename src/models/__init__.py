from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Table, Column, ForeignKey


class Base(DeclarativeBase):
    pass


voters_association_table = Table(
    "voters_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("vote_topic_id", ForeignKey("vote_topics.id"), primary_key=True),
)
