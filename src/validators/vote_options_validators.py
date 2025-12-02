from pydantic import BaseModel, Field


class AddVoteOptionArgumentTypeValidator(BaseModel):
    vote_topic_id: str = Field(min_length=32, max_length=36)
    option: str


class CastVoteArgumentTypeValidator(BaseModel):
    vote_option_id: str = Field(min_length=32, max_length=36)
