from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Plan as PlanModel, PlanDay as PlanDayModel
from schemas import (
    GeneratePlanRequest,
    PlanCreate,
    PlanResponse,
    PlanUpdate,
    PlanWithDaysResponse,
)
from plan_generator import generate_plan, generate_plan_days


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Path API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Path API"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/plans", response_model=PlanResponse)
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    db_plan = PlanModel(
        user_id=plan.user_id,
        title=plan.title,
        description=plan.description,
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@app.get("/plans", response_model=list[PlanResponse])
def list_plans(db: Session = Depends(get_db)):
    return db.query(PlanModel).all()


@app.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(PlanModel).filter(PlanModel.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@app.patch("/plans/{plan_id}", response_model=PlanResponse)
def update_plan(plan_id: int, plan_update: PlanUpdate, db: Session = Depends(get_db)):
    plan = db.query(PlanModel).filter(PlanModel.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    if plan_update.title is not None:
        plan.title = plan_update.title
    if plan_update.description is not None:
        plan.description = plan_update.description
    db.commit()
    db.refresh(plan)
    return plan


@app.delete("/plans/{plan_id}", status_code=204)
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(PlanModel).filter(PlanModel.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    db.delete(plan)
    db.commit()
    return None


@app.post("/plans/generate", response_model=PlanResponse)
def create_plan_from_generator(
    user_id: int,
    title: str,
    description: str | None = None,
    db: Session = Depends(get_db),
):
    plan = generate_plan(user_id=user_id, title=title, description=description)
    return create_plan(plan=plan, db=db)


@app.post("/generate-plan", response_model=PlanWithDaysResponse)
def generate_plan_with_days(
    body: GeneratePlanRequest,
    db: Session = Depends(get_db),
):
    """Create a plan from a theme and duration, with plan days and placeholder verses."""
    title = body.theme.strip() or "New Plan"
    db_plan = PlanModel(
        user_id=body.user_id,
        title=title,
        description=f"{body.duration_days}-day plan on {body.theme}",
    )
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)

    for day_schema in generate_plan_days(
        plan_id=db_plan.id,
        theme=body.theme,
        duration_days=body.duration_days,
    ):
        db_day = PlanDayModel(
            plan_id=day_schema.plan_id,
            day_number=day_schema.day_number,
            verse=day_schema.verse,
        )
        db.add(db_day)
    db.commit()
    db.refresh(db_plan)
    return db_plan
