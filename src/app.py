from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from src.database.db_session import AsyncPostgresClient
from src.api import main_router
from src.s3.s3_service import S3Service


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
        await S3Service.init_s3(bucket_name="bucket", endpoint_url="http://localhost:9000", access_key="user", secret_key="123456789")
        print("All resources have been successfully initialized")

        yield

        await AsyncPostgresClient.close_postgres()
        await S3Service.close_s3()
        print("All resources have been successfully closed")
