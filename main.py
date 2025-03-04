from fastapi import FastAPI
from api import endpoints
from database import Base, engine

def init_db():
    Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(endpoints.router)

init_db()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

    