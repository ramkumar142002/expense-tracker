import datetime
import typing
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.sqltypes import Integer
from typing import Self

from sqlalchemy import DateTime, inspect
from sqlalchemy.sql.expression import text
from sqlalchemy.orm.session import Session

class SimpleBase(DeclarativeBase):
    pass

class Base(SimpleBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        nullable=False,
        autoincrement=True,
    )
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=True
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.datetime.now(datetime.timezone.utc),
        onupdate=lambda: datetime.datetime.now(datetime.timezone.utc),
        nullable=True,
    )

    printable_columns = ["id"]

    @property
    def who_am_i(self) -> str:
        """
        Returns the class name of the instance.
        Useful for logging and tracing.
        """
        return self.__class__.__name__

    def save(self, db: Session) -> Self:
        db.add(self)
        db.commit()
        return self

    def delete(self, db: Session) -> Self:
        db.delete(self)
        db.commit()
        return self

    def save_with_flush(self, db: Session) -> Self:
        db.add(self)
        db.flush()
        return self

    @property
    def str_repr(self) -> str:
        """Define a base way to print models
        Columns inside `print_filter` are excluded"""
        return f"{self.__class__.__name__}({ ({column: getattr(self, column) for column in self.printable_columns}) })"

    @property
    def dictionary(self) -> dict[str, typing.Any]:
        """This would more or less be the same as a `to_json`
        But putting it in a "private" function
        Allows to_json to be overriden without impacting __repr__
        Or the other way around
        And to add filter lists"""
        return {column.key: getattr(self, column.key) for column in inspect(self.__class__).attrs}

    def __repr__(self) -> str:
        return self.str_repr

    def __str__(self) -> str:
        return self.str_repr

    def clone(self, db: Session) -> Self:
        d = dict(self.dictionary)
        if d.get("id"):
            d.pop("id")  # get rid of id
        copy = self.__class__(**d)
        return copy.save(db)

