import hashlib
from datetime import date as dt_date, datetime, timezone
from typing import Annotated

from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models  # noqa: F401
from app.database import Base, engine, get_db


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    is_superuser: bool = False


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_superuser: bool
    created_at: datetime | None


class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int
    name: str


class ExpenseCreate(BaseModel):
    category_id: int
    description: str | None = None
    amount: float
    date: dt_date


class ExpenseResponse(BaseModel):
    id: int
    name: str
    category_id: int | None
    category_name: str | None
    description: str | None
    amount: float
    date: dt_date
    user_id: int
    created_at: datetime | None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def get_current_user(
    x_user_id: Annotated[int | None, Header()] = None,
    db: Session = Depends(get_db),
) -> models.User:
    if x_user_id is None:
        raise HTTPException(status_code=401, detail="X-User-Id header is required")
    user = db.query(models.User).filter(models.User.id == x_user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_superuser(current_user: Annotated[models.User, Depends(get_current_user)]) -> models.User:
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Superuser access required")
    return current_user


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI()

Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "FastAPI is running"}


# ---------------------------------------------------------------------------
# Users
# ---------------------------------------------------------------------------

@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"description": "Validation failed"}, 409: {"description": "Duplicate user"}},
)
def create_user(payload: UserCreate, db: Annotated[Session, Depends(get_db)]):
    username = payload.username.strip()
    email = payload.email.strip().lower()
    password = payload.password

    if not username:
        raise HTTPException(status_code=400, detail="Username is required")
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Valid email is required")
    if len(password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    existing = db.query(models.User).filter(
        (models.User.username == username) | (models.User.email == email)
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username or email already exists")

    user = models.User(
        username=username,
        email=email,
        password_hash=hash_password(password),
        is_superuser=payload.is_superuser,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
    )


@app.get("/users", response_model=list[UserResponse])
def list_users(db: Annotated[Session, Depends(get_db)]):
    users = db.query(models.User).order_by(models.User.id.desc()).all()
    return [
        UserResponse(
            id=u.id,
            username=u.username,
            email=u.email,
            is_superuser=u.is_superuser,
            created_at=u.created_at,
        )
        for u in users
    ]


@app.post(
    "/login",
    response_model=UserResponse,
    responses={401: {"description": "Invalid credentials"}},
)
def login(payload: LoginRequest, db: Annotated[Session, Depends(get_db)]):
    user = db.query(models.User).filter(
        models.User.username == payload.username.strip()
    ).first()

    if not user or user.password_hash != hash_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
    )


# ---------------------------------------------------------------------------
# Categories  (create: superuser only; list: any authenticated user)
# ---------------------------------------------------------------------------

@app.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"description": "Validation failed"},
        403: {"description": "Superuser access required"},
        404: {"description": "Not found"},
        409: {"description": "Category already exists"},
    },
)
def create_category(
    payload: CategoryCreate,
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[models.User, Depends(require_superuser)],
):
    name = payload.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Category name is required")
    if db.query(models.Category).filter(models.Category.name == name).first():
        raise HTTPException(status_code=409, detail="Category already exists")

    category = models.Category(name=name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return CategoryResponse(id=category.id, name=category.name)


@app.get("/categories", response_model=list[CategoryResponse])
def list_categories(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[models.User, Depends(get_current_user)],
):
    categories = db.query(models.Category).order_by(models.Category.name).all()
    return [CategoryResponse(id=c.id, name=c.name) for c in categories]


# ---------------------------------------------------------------------------
# Expenses  (create & list: any authenticated user, tied to their user_id)
# ---------------------------------------------------------------------------

@app.post(
    "/expenses",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_expense(
    payload: ExpenseCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    category = db.query(models.Category).filter(models.Category.id == payload.category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    expense = models.Expense(
        name=category.name,
        category_id=payload.category_id,
        description=payload.description,
        amount=payload.amount,
        date=payload.date,
        user_id=current_user.id,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)

    return ExpenseResponse(
        id=expense.id,
        name=expense.name,
        category_id=expense.category_id,
        category_name=category.name,
        description=expense.description,
        amount=expense.amount,
        date=expense.date,
        user_id=expense.user_id,
        created_at=expense.created_at,
    )


@app.get("/expenses", response_model=list[ExpenseResponse])
def list_expenses(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[models.User, Depends(get_current_user)],
):
    expenses = (
        db.query(models.Expense)
        .filter(models.Expense.user_id == current_user.id)
        .order_by(models.Expense.date.desc())
        .all()
    )

    category_ids = {e.category_id for e in expenses if e.category_id}
    categories = {
        c.id: c.name
        for c in db.query(models.Category).filter(models.Category.id.in_(category_ids)).all()
    }

    return [
        ExpenseResponse(
            id=e.id,
            name=e.name,
            category_id=e.category_id,
            category_name=categories.get(e.category_id),
            description=e.description,
            amount=e.amount,
            date=e.date,
            user_id=e.user_id,
            created_at=e.created_at,
        )
        for e in expenses
    ]