from fastapi import FastAPI
from api import endpoints
from database import Base, engine

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    app = FastAPI()
    app.include_router(endpoints.router)
    