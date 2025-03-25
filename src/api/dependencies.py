from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import db_session

SessionDepend = Annotated[AsyncSession, Depends(db_session.create_session)]
