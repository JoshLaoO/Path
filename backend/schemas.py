from datetime import datetime
from pydantic import BaseModel, ConfigDict


class PlanBase(BaseModel):
    title: str
    description: str | None = None


class PlanCreate(PlanBase):
    pass


class PlanUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class Plan(PlanBase):
    id: int
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
