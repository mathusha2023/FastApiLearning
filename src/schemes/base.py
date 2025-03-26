from pydantic import BaseModel, ConfigDict
from typing import Optional


class SuccessScheme(BaseModel):
    success: bool = True
