from datetime import date as dt_date

from sqlalchemy import Float, String, Date
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)


class User(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)


class Expense(Base):
    __tablename__ = "expenses"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    date: Mapped[dt_date] = mapped_column(Date, default=dt_date.today, nullable=False)