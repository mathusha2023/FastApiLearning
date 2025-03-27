from pydantic import BaseModel


class SuccessScheme(BaseModel):
    success: bool = True
