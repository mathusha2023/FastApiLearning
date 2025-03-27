import uvicorn
from src.app import App
from src.settings import settings

app = App()


if __name__ == "__main__":
    uvicorn.run("main:app",  host=settings.host, port=settings.port)
