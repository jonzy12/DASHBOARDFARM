

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str 
    password: str 
    email: EmailStr 
    company_name: str
    is_active: bool = True


class ForgotPasswordRequest(BaseModel):
    email: str

class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str




class FieldCreate(BaseModel):
    plot_name: str
    crop_type: str
    area_size_hectares: float
    latitude: float
    longitude: float  
    sowing_date: datetime = Field(default_factory=datetime.now)
    





    