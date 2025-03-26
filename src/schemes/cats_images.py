from pydantic import BaseModel, ConfigDict


class CatImageScheme(BaseModel):
    id: int
    cat_id: int
    image_url: str

    model_config = ConfigDict(from_attributes=True)


class CatImageURLScheme(BaseModel):
    image_url: str

