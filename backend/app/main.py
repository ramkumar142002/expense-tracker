import hashlib
from typing import Annotated
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app import models  # noqa: F401
from app.database import Base, engine, get_db


class UserCreate(BaseModel):
    username: str
    email: str
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    created_at: datetime | None


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

app = FastAPI()

Base.metadata.create_all(bind=engine)

# Allow Vue frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FastAPI is running 🚀"}


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
        created_at=user.created_at,
    )


@app.get("/users", response_model=list[UserResponse])
def list_users(db: Annotated[Session, Depends(get_db)]):
    users = db.query(models.User).order_by(models.User.id.desc()).all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            created_at=user.created_at,
        )
        for user in users
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
        created_at=user.created_at,
    )