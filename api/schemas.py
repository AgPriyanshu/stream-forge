from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class TenantCreateRequest(BaseModel):
    name: str = Field(min_length=1)


class TenantResponse(BaseModel):
    id: UUID
    name: str


class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(min_length=8)
    tenant_id: UUID


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    access_token: str
