from pydantic import BaseModel, EmailStr, Field, model_validator

class UserRegisterRequest(BaseModel):
    fullName: str = Field(..., min_length=2, description="Ім'я є обов'язковим")
    email: EmailStr = Field(..., description="Введіть коректний email")
    password: str = Field(..., min_length=8, description="Пароль має бути не менше 8 символів")
    confirmPassword: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> 'UserRegisterRequest':
        if self.password != self.confirmPassword:
            raise ValueError('Паролі не співпадають')
        return self

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
