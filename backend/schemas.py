from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


# ----- User -----


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ----- Plan -----


class PlanBase(BaseModel):
    title: str
    description: str | None = None


class PlanCreate(PlanBase):
    user_id: int


class PlanUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class PlanResponse(PlanBase):
    id: int
    user_id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class GeneratePlanRequest(BaseModel):
    theme: str
    duration_days: int
    user_id: int


class PlanWithDaysResponse(PlanResponse):
    plan_days: list["PlanDayResponse"] = []

    model_config = ConfigDict(from_attributes=True)


# ----- PlanDay -----


class PlanDayCreate(BaseModel):
    plan_id: int
    day_number: int
    verse: str | None = None


class PlanDayUpdate(BaseModel):
    day_number: int | None = None
    verse: str | None = None


class PlanDayResponse(BaseModel):
    id: int
    plan_id: int
    day_number: int
    verse: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ----- Reflection -----


class ReflectionCreate(BaseModel):
    plan_day_id: int
    user_id: int
    content: str


class ReflectionUpdate(BaseModel):
    content: str | None = None


class ReflectionResponse(BaseModel):
    id: int
    plan_day_id: int
    user_id: int
    content: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# ----- JournalEntry -----


class JournalEntryCreate(BaseModel):
    plan_day_id: int
    user_id: int
    content: str


class JournalEntryUpdate(BaseModel):
    content: str | None = None


class JournalEntryResponse(BaseModel):
    id: int
    plan_day_id: int
    user_id: int
    content: str
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# Resolve forward ref for PlanWithDaysResponse
PlanWithDaysResponse.model_rebuild()
