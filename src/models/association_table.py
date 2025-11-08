from sqlalchemy import Table, Column, ForeignKey
from src.db.base import Base


voters_association_table = Table(
    "voters_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("vote_topic_id", ForeignKey("vote_topics.id"), primary_key=True),
)
