from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.database.db_session import AsyncPostgresClient
from src.api import main_router


class App(FastAPI):
    def __init__(self):
        super().__init__(lifespan=App.lifespan, debug=True)
        super().include_router(main_router)
        super().add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @staticmethod
    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        await AsyncPostgresClient.init_postgres("postgresql+asyncpg://user:user@localhost/db")
        print("All resources have been successfully initialized")
        print(AsyncPostgresClient.get_async_session())

        yield

        await AsyncPostgresClient.close_postgres()
        print("All resources have been successfully closed")
