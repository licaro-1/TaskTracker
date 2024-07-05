from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class JWTTokenInfo(BaseModel):
    access_token: str
    token_type: str
