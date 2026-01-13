"""Date range utilities for reports"""

from datetime import date, datetime, time, timedelta


def today_range() -> tuple[datetime, datetime]:
    today = date.today()
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)
    return start, end


def yesterday_range() -> tuple[datetime, datetime]:
    yesterday = date.today() - timedelta(days=1)
    start = datetime.combine(yesterday, time.min)
    end = datetime.combine(yesterday, time.max)
    return start, end


def this_week_range() -> tuple[datetime, datetime]:
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)

    start = datetime.combine(start_of_week, time.min)
    end = datetime.combine(end_of_week, time.max)
    return start, end


def last_week_range() -> tuple[datetime, datetime]:
    today = date.today()
    start_of_this_week = today - timedelta(days=today.weekday())
    start_of_last_week = start_of_this_week - timedelta(days=7)
    end_of_last_week = start_of_last_week + timedelta(days=6)

    start = datetime.combine(start_of_last_week, time.min)
    end = datetime.combine(end_of_last_week, time.max)
    return start, end


def custom_range(from_date: str, to_date: str) -> tuple[datetime, datetime]:
    try:
        start_date = datetime.strptime(from_date, "%Y-%m-%d")
        end_date = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError as e:
        raise ValueError(f"Invalid date format. Use YYYY-MM-DD format. Error: {e}")

    if start_date > end_date:
        raise ValueError("Start date must be before or equal to end date")

    start = datetime.combine(start_date.date(), time.min)
    end = datetime.combine(end_date.date(), time.max)
    return start, end


def last_n_days_range(days: int) -> tuple[datetime, datetime]:
    if days < 1:
        raise ValueError("Days must be at least 1")

    today = date.today()
    start_date = today - timedelta(days=days - 1)

    start = datetime.combine(start_date, time.min)
    end = datetime.combine(today, time.max)
    return start, end


def month_range(year: int, month: int) -> tuple[datetime, datetime]:
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12")

    start_date = date(year, month, 1)

    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    start = datetime.combine(start_date, time.min)
    end = datetime.combine(end_date, time.max)
    return start, end
