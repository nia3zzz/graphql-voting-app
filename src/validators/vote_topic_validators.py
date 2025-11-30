from pydantic import BaseModel, Field
from typing import List, Optional


class CreateVoteTopicArgumentTypeValidator(BaseModel):
    description: str = Field(min_length=3, max_length=500)
    options: List[str] = Field(min_length=2, max_length=12)


class DeleteVoteTopicArgumentTypeValidator(BaseModel):
    vote_topic_id: str = Field(min_length=32, max_length=36)


class GetVoteTopicsInputTypeValidator(BaseModel):
    limit: Optional[int] = Field(ge=10, le=100, default=10)
    skip: Optional[int] = Field(ge=0, default=0)


class GetVoteTopicByIdInputTypeValidator(BaseModel):
    vote_topic_id: str = Field(min_length=32, max_length=36)
