from pydantic import BaseModel, Field
from typing import List


class CreateVoteTopicArgumentTypeValidator(BaseModel):
    description: str = Field(min_length=3, max_length=500)
    options: List[str] = Field(min_length=2, max_length=12)
