from typing import Annotated, Optional
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.database.data_types import intpk
from src.database.base import Base


class CatImageModel(Base):
    __tablename__ = "cats_images"

    id: Mapped[intpk]
    cat_id: Mapped[Annotated[int, mapped_column(ForeignKey("cats.id"))]]
    image_url: Mapped[str]
    cat: Mapped["CatModel"] = relationship(back_populates="images")
