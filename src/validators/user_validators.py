from pydantic import BaseModel, EmailStr, Field


class AuthRegisterUserType(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)


class AuthLoginUserType(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=50)


class UpdateUserArgumentTypeValidator(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    email: EmailStr
