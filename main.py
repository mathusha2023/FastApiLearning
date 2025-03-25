import uvicorn
from src.app import App

app = App()


if __name__ == "__main__":
    uvicorn.run("main:app",  host="localhost", port=8000)
