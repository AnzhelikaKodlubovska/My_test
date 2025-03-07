from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import date
import pandas as pd

from models.credit import User, Credit, Dictionary, Plan, Payment
from database import get_db
from utils.helpers import calculate_overdue_days

router = APIRouter()


@router.get("/user_credits/{user_id}")
def get_user_credits(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    credits = db.query(Credit).filter(Credit.user_id == user_id).all()
    credit_list = []

    for credit in credits:
        credit_data: Dict[str, Any] = {
            "issuance_date": credit.issuance_date,
            "is_closed": bool(credit.actual_return_date),
            "body": credit.body,
            "percent": credit.percent,
        }

        if credit.actual_return_date:
            credit_data["return_date"] = credit.actual_return_date
            credit_data["total_payments"] = sum(p.sum for p in credit.payments)
        else:
            credit_data["return_date"] = credit.return_date
            credit_data["overdue_days"] = calculate_overdue_days(credit.return_date)
            credit_data["body_payments"] = sum(
                p.sum for p in credit.payments if p.type.name == "body"
            )
            credit_data["percent_payments"] = sum(
                p.sum for p in credit.payments if p.type.name == "percent"
            )

        credit_list.append(credit_data)

    return credit_list


@router.post("/plans_insert")
def insert_plans(file: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        df = pd.read_excel(file.file)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {e}")

    for index, row in df.iterrows():
        try:
            period = pd.to_datetime(row["месяць плану"]).date()
            category_name = row["назва категорії плану"]
            sum_amount = row["сума"]

            if pd.isna(sum_amount):
                raise ValueError("Sum cannot be empty")

            if period.day != 1:
                raise ValueError("Month should start with the first day")

            category = db.query(Dictionary).filter(Dictionary.name == category_name).first()
            if not category:
                raise ValueError(f"Category '{category_name}' not found")

            existing_plan = db.query(Plan).filter(Plan.period == period, Plan.category_id == category.id).first()
            if existing_plan:
                raise ValueError(f"Plan for {period} and category '{category_name}' already exists")

            new_plan = Plan(period=period, sum=sum_amount, category_id=category.id)
            db.add(new_plan)

        except (ValueError, TypeError) as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Error in row {index + 2}: {e}")
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Unexpected error in row {index + 2}: {e}")

    db.commit()
    return {"message": "Plans uploaded successfully"}


@router.get("/plans_performance")
def get_plans_performance(date_str: str, db: Session = Depends(get_db)):
    target_date = pd.to_datetime(date_str).date()
    start_of_month = target_date.replace(day=1)

    plans = db.query(Plan).filter(Plan.period == start_of_month).all()
    performance_data = []

    for plan in plans:
        category = db.query(Dictionary).filter(Dictionary.id == plan.category_id).first()
        if not category:
            continue  

        if category.name.lower() == "видача":  
            actual_sum = (
                db.query(Credit.body)
                .filter(Credit.issuance_date >= start_of_month, Credit.issuance_date <= target_date)
                .scalar() or 0
            )
        elif category.name.lower() == "збір":  
            actual_sum = (
                db.query(Payment.sum)
                .join(Credit)
                .filter(
                    Payment.payment_date >= start_of_month,
                    Payment.payment_date <= target_date
                )
                .scalar() or 0
            )
        else:
            actual_sum = 0

        performance = (actual_sum / plan.sum) * 100 if plan.sum > 0 else 0

        performance_data.append({
            "month": start_of_month.strftime("%Y-%m"),
            "category": category.name,
            "planned_sum": plan.sum,
            "actual_sum": actual_sum,
            "performance_percent": round(performance, 2)
        })

    return performance_data


@router.get("/year_performance")
def get_year_performance(year: int, db: Session = Depends(get_db)):
    start_of_year = date(year, 1, 1)
    end_of_year = date(year, 12, 31)

    plans = db.query(Plan).filter(Plan.period >= start_of_year, Plan.period <= end_of_year).all()
    performance_data = {}

    for plan in plans:
        category = db.query(Dictionary).filter(Dictionary.id == plan.category_id).first()
        if not category:
            continue  
        if category.name.lower() == "видача":
            actual_sum = (
                db.query(sum(Credit.body))
                .filter(Credit.issuance_date >= plan.period, Credit.issuance_date <= end_of_year)
                .scalar() or 0
            )
        elif category.name.lower() == "збір":
            actual_sum = (
                db.query(sum(Payment.sum))
                .join(Credit)
                .filter(Payment.payment_date >= plan.period, Payment.payment_date <= end_of_year)
                .scalar() or 0
            )
        else:
            actual_sum = 0

        if category.name not in performance_data:
            performance_data[category.name] = {"planned_sum": 0, "actual_sum": 0}

        performance_data[category.name]["planned_sum"] += plan.sum
        performance_data[category.name]["actual_sum"] += actual_sum

    for category, data in performance_data.items():
        planned = data["planned_sum"]
        actual = data["actual_sum"]
        performance_data[category]["performance_percent"] = round((actual / planned) * 100 if planned > 0 else 0, 2)

    return performance_data
