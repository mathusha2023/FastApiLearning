from pydantic import BaseModel, ConfigDict, Field
from datetime import date
from typing import Annotated, List, Optional
from src.schemes.cats_images import CatImageScheme


class CatPatchScheme(BaseModel):
    name: Optional[str] = None
    birthday: Optional[Annotated[date, Field(le=date.today())]] = None
    color: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CatAddScheme(CatPatchScheme):
    name: str
    birthday: Annotated[date, Field(le=date.today())]
    color: str


class CatScheme(CatAddScheme):
    id: int


class CatFullAddScheme(CatAddScheme):
    images: List[CatImageScheme]


class CatFullScheme(CatFullAddScheme, CatScheme):
    pass

