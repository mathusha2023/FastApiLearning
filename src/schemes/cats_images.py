from pydantic import BaseModel, ConfigDict
from typing import Optional


class CatImageScheme(BaseModel):
    id: int
    cat_id: int
    image_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class CatImageURLScheme(BaseModel):
    image_url: str

