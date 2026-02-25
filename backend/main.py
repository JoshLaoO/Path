from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordBearer
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from auth import create_access_token, decode_access_token, hash_password, verify_password
from database import Base, engine, get_db
from migrate import run_migrations
from models import Plan as PlanModel, PlanDay as PlanDayModel, User as UserModel
from schemas import (
    AuthResponse,
    GeneratePlanRequest,
    LoginRequest,
    PlanCreate,
    PlanResponse,
    PlanUpdate,
    PlanWithDaysResponse,
    UserCreate,
    UserResponse,
    UserUpdate,
)
from plan_generator import generate_plan, generate_plan_days

# For Swagger UI "Authorize": use OAuth2 password flow; tokenUrl is the sign-in endpoint.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
# Fallback for clients that send Bearer without using the form (e.g. frontend).
security = HTTPBearer(auto_error=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_migrations()
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


def _token_to_user(token: str | None, db: Session) -> UserModel | None:
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    try:
        user_id = int(payload["sub"])
    except (ValueError, TypeError):
        return None
    return db.query(UserModel).filter(UserModel.id == user_id).first()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    token_from_oauth2: str | None = Depends(oauth2_scheme),
) -> UserModel:
    token = token_from_oauth2 or (credentials.credentials if credentials else None)
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = _token_to_user(token, db)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


# ----- Auth (signup / login) -----


@app.post("/token")
def token_for_docs(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    OAuth2-compatible token endpoint for Swagger UI "Authorize".
    Use your **email** as username and your password. Returns a Bearer token.
    """
    user = db.query(UserModel).filter(UserModel.email == form.username).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(user.id),
        "token_type": "bearer",
    }


@app.post("/auth/signup", response_model=AuthResponse, status_code=201)
def signup(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserModel).filter(UserModel.email == body.email).first():
        raise HTTPException(
            status_code=400, detail="A user with this email already exists"
        )
    db_user = UserModel(
        email=body.email,
        hashed_password=hash_password(body.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    token = create_access_token(db_user.id)
    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(db_user),
    )


@app.post("/auth/login", response_model=AuthResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.id)
    return AuthResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@app.get("/auth/me", response_model=UserResponse)
def get_me(current_user: UserModel = Depends(get_current_user)):
    return current_user


# ----- Users -----


@app.post("/users", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(UserModel).filter(UserModel.email == user.email).first():
        raise HTTPException(
            status_code=400, detail="A user with this email already exists"
        )
    db_user = UserModel(
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/users", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    return db.query(UserModel).all()


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, user_update: UserUpdate, db: Session = Depends(get_db)
):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.email is not None:
        existing = db.query(UserModel).filter(
            UserModel.email == user_update.email, UserModel.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=400, detail="A user with this email already exists"
            )
        user.email = user_update.email
    if user_update.password is not None:
        user.hashed_password = hash_password(user_update.password)
    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return None


# ----- Plans -----


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
