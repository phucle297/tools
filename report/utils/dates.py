from datetime import date, datetime, time, timedelta


def today_range() -> tuple[datetime, datetime]:
    today = date.today()
    start = datetime.combine(today, time.min)
    end = datetime.combine(today, time.max)
    return start, end


def this_week_range() -> tuple[datetime, datetime]:
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # Monday
    end_of_week = start_of_week + timedelta(days=6)

    start = datetime.combine(start_of_week, time.min)
    end = datetime.combine(end_of_week, time.max)
    return start, end
