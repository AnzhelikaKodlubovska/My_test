import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal
from models.credit import Payment, Credit, Dictionary, Plan, User  

def load_payments_from_csv(file_path: str, db: Session):
    df = pd.read_csv(file_path, delimiter=".", names=["idcredit", "idpayment", "datetype_id", "idsum"])
    for _, row in df.iterrows():
        db.add(Payment(
            idcredit=row["idcredit"],
            idpayment=row["idpayment"],
            datetype=row["datetype_id"],
            idsum=row["sum"]
        ))
    db.commit()

def load_credits_from_csv(file_path: str, db: Session):
    df = pd.read_csv(file_path, delimiter=".", names=["idcredit", "amount", "term", "rate"])
    for _, row in df.iterrows():
        db.add(Credit(
            idcredit=row["idcredit"],
            amount=row["amount"],
            term=row["term"],
            rate=row["rate"]
        ))
    db.commit()

def load_credits_from_csv(file_path: str, db: Session):
    df = pd.read_csv(file_path, delimiter=".", names=["idcredit", "amount", "term", "rate"])
    for _, row in df.iterrows():
        db.add(User(
            idcredit=row["idcredit"],
            amount=row["amount"],
            term=row["term"],
            rate=row["rate"]
        ))
    db.commit()
    
def load_credits_from_csv(file_path: str, db: Session):
    df = pd.read_csv(file_path, delimiter=".", names=["idcredit", "amount", "term", "rate"])
    for _, row in df.iterrows():
        db.add(Dictionary(
            idcredit=row["idcredit"],
            amount=row["amount"],
            term=row["term"],
            rate=row["rate"]
        ))
    db.commit()
    
def load_credits_from_csv(file_path: str, db: Session):
    df = pd.read_csv(file_path, delimiter=".", names=["idcredit", "amount", "term", "rate"])
    for _, row in df.iterrows():
        db.add(Plan(
            idcredit=row["idcredit"],
            amount=row["amount"],
            term=row["term"],
            rate=row["rate"]
        ))
    db.commit()
    

if __name__ == "__main__":
    db = SessionLocal()
    load_payments_from_csv("data/payments.csv", db)
    load_credits_from_csv("data/credits.csv", db)
    load_credits_from_csv("data/dictionary.csv", db)
    load_credits_from_csv("data/plans.csv", db)
    load_credits_from_csv("data/users.csv", db)
    db.close()
    print("Дані завантажено у БД!")
