from pydantic import BaseModel, EmailStr, Field


class CreateUserMutationInput(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)


class LoginUserMutationInput(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)
