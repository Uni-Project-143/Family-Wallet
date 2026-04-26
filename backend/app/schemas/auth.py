import re
from pydantic import BaseModel, EmailStr, Field, model_validator, field_validator

class UserRegisterRequest(BaseModel):
    fullName: str = Field(..., min_length=2, description="Full name is required")
    email: EmailStr = Field(..., description="Enter a valid email address")
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    confirmPassword: str

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v


    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserRegisterRequest':
        if self.password != self.confirmPassword:
            raise ValueError('Passwords do not match')
        return self

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
