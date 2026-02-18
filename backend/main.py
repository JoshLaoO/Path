from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Plan as PlanModel
from schemas import Plan, PlanCreate, PlanUpdate
from plan_generator import generate_plan


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


@app.post("/plans", response_model=Plan)
def create_plan(plan: PlanCreate, db: Session = Depends(get_db)):
    db_plan = PlanModel(title=plan.title, description=plan.description)
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


@app.get("/plans", response_model=list[Plan])
def list_plans(db: Session = Depends(get_db)):
    return db.query(PlanModel).all()


@app.get("/plans/{plan_id}", response_model=Plan)
def get_plan(plan_id: int, db: Session = Depends(get_db)):
    plan = db.query(PlanModel).filter(PlanModel.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@app.patch("/plans/{plan_id}", response_model=Plan)
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


@app.post("/plans/generate", response_model=Plan)
def create_plan_from_generator(
    title: str, description: str | None = None, db: Session = Depends(get_db)
):
    plan = generate_plan(title=title, description=description)
    return create_plan(plan=plan, db=db)
