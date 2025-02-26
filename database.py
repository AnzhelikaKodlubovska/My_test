from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
    
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
try:
    conn = engine.connect()
    print("Успішно підключено до бази даних!")
    conn.close()
except Exception as e:
    print(f"Помилка підключення до бази даних: {e}")
 
