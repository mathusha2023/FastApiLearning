from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import db_session
from src.message_broker.broker_service import RabbitMQService, get_rabbitmq_service

SessionDepend = Annotated[AsyncSession, Depends(db_session.create_session)]
BrokerDepend = Annotated[RabbitMQService, Depends(get_rabbitmq_service)]