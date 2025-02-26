from datetime import date, timedelta

def calculate_overdue_days(return_date: date):
    today = date.today()
    if today > return_date:
        return (today - return_date).days
    return 0
