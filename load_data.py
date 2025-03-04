import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal
from models.credit import Payment, Credit, Dictionary, Plan, User

def load_users_from_csv(file_path: str, db: Session):
    df = pd.read_csv(file_path, delimiter="\t", names=["id", "login", "registration_date"], skiprows=1)
    for _, row in df.iterrows():
        if not db.query(User).filter_by(id=row["id"]).first():
            db.add(User(
                id=row["id"],
                login=row["login"],
                registration_date=row["registration_date"]
            ))
    db.commit()

def load_dictionary_from_csv(file_path: str, db: Session):
    df = pd.read_csv(file_path, delimiter="\t", names=["id", "name"], skiprows=1)
    for _, row in df.iterrows():
        if not db.query(Dictionary).filter_by(id=row["id"]).first():
            db.add(Dictionary(
                id=row["id"],
                name=row["name"]
            ))
    db.commit()


def load_credits_from_csv(file_path: str, db: Session):
    try:
        df = pd.read_csv(file_path, delimiter="\t", names=["id", "user_id", "issuance_date", "return_date", "actual_return_date", "body", "percent"], skiprows=1)
        df['actual_return_date'] = df['actual_return_date'].fillna(pd.NaT)
        df['issuance_date'] = df['issuance_date'].fillna(pd.NaT)
        df['return_date'] = df['return_date'].fillna(pd.NaT)
        df['body'] = df['body'].fillna(0)
        df['percent'] = df['percent'].fillna(0)

        for _, row in df.iterrows():
            if db.query(User).filter_by(id=row["user_id"]).first():
                db.add(Credit(
                    id=row["id"],
                    user_id=row["user_id"],
                    issuance_date=row["issuance_date"],
                    return_date=row["return_date"],
                    actual_return_date=row["actual_return_date"],
                    body=row["body"],
                    percent=row["percent"]
                ))
            else:
                print(f"Попередження: user_id {row['user_id']} не знайдено, кредит {row['id']} не додано.")

        db.commit()
    except Exception as e:
        print(f"Помилка при завантаженні credits: {e}")
        db.rollback()

def load_plans_from_csv(file_path: str, db: Session):
    df = pd.read_csv(file_path, delimiter="\t", names=["id", "period", "sum", "category_id"], skiprows=1)
    for _, row in df.iterrows():
        if db.query(Dictionary).filter_by(id=row["category_id"]).first():  
            db.add(Plan(
                id=row["id"],
                period=row["period"],
                sum=row["sum"],
                category_id=row["category_id"]
            ))
    db.commit()

def load_payments_from_csv(file_path: str, db: Session):
    try:
        df = pd.read_csv(file_path, delimiter="\t", names=["id", "credit_id", "payment_date", "type_id", "sum"], skiprows=1)
        df['sum'] = df['sum'].fillna(0)
        df['type_id'] = df['type_id'].fillna(pd.NaT)
        df["payment_date"] = pd.to_datetime(df["payment_date"], format="%d.%m.%Y", errors="coerce")
        for _, row in df.iterrows():
            if not db.query(Payment).filter_by(id=row["id"]).first(): 
                    db.add(Payment(
                        id=row["id"],
                        credit_id=row["credit_id"],
                        payment_date=row["payment_date"],
                        type_id=row["type_id"],
                        sum=row["sum"]
                    ))
            else:
                    print(f"Попередження: платіж з id {row['id']} вже існує.")
        else:
                print(f"Попередження: credit_id {row['credit_id']} або type_id {row['type_id']} не знайдено, платіж {row['id']} не додано.")
        db.commit()
    except Exception as e:
        print(f"Помилка при завантаженні payments: {e}")
        db.rollback()


if __name__ == "__main__":
    db = SessionLocal()
    load_users_from_csv("data/users.csv", db)
    load_dictionary_from_csv("data/dictionary.csv", db)
    load_credits_from_csv("data/credits.csv", db)
    load_plans_from_csv("data/plans.csv", db)
    load_payments_from_csv("data/payments.csv", db)
    db.close()
    print("Дані завантажено у БД!")
