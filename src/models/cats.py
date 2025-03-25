from datetime import date
from sqlalchemy.orm import Mapped, relationship
from typing import List
from src.database.data_types import intpk
from src.database.base import Base


class CatModel(Base):
    __tablename__ = "cats"

    id: Mapped[intpk]
    name: Mapped[str]
    birthday: Mapped[date]
    color: Mapped[str]
    images: Mapped[List["CatImageModel"]] = relationship(back_populates="cat", cascade="all, delete")

