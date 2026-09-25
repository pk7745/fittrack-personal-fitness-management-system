import calendar
from datetime import date
from app.models import Workout, FitnessRecord, Goal
from app.services.fitness_service import calculate_goal_progress


def get_month_calendar_events(user_id, year=None, month=None):
    """
    Retrieve user-owned events (workouts, daily metrics, goal deadlines)
    grouped by date for a given year and month.
    """
    today = date.today()
    if year is None:
        year = today.year
    if month is None:
        month = today.month

    try:
        year = int(year)
        month = int(month)
        if month < 1 or month > 12:
            return None, "Month must be between 1 and 12"
        if year < 1900 or year > 2100:
            return None, "Year must be between 1900 and 2100"
    except (ValueError, TypeError):
        return None, "Invalid year or month"

    num_days = calendar.monthrange(year, month)[1]
    start_date = date(year, month, 1)
    end_date = date(year, month, num_days)

    # Initialize map for every day in the month
    events_by_date = {}
    for day in range(1, num_days + 1):
        d_str = date(year, month, day).isoformat()
        events_by_date[d_str] = {
            "date": d_str,
            "has_workout": False,
            "workout_count": 0,
            "workouts": [],
            "fitness_record": None,
            "goal_deadlines": []
        }

    # 1. Fetch user's workouts in this month
    workouts = Workout.query.filter(
        Workout.user_id == user_id,
        Workout.workout_date >= start_date,
        Workout.workout_date <= end_date
    ).order_by(Workout.workout_date.asc(), Workout.id.asc()).all()

    for w in workouts:
        d_key = w.workout_date.isoformat()
        if d_key in events_by_date:
            events_by_date[d_key]["has_workout"] = True
            events_by_date[d_key]["workout_count"] += 1
            events_by_date[d_key]["workouts"].append(w.to_dict())

    # 2. Fetch user's fitness records in this month
    fit_records = FitnessRecord.query.filter(
        FitnessRecord.user_id == user_id,
        FitnessRecord.record_date >= start_date,
        FitnessRecord.record_date <= end_date
    ).all()

    for f in fit_records:
        d_key = f.record_date.isoformat()
        if d_key in events_by_date:
            events_by_date[d_key]["fitness_record"] = f.to_dict()

    # 3. Fetch user's goals with deadlines in this month
    goals = Goal.query.filter(
        Goal.user_id == user_id,
        Goal.deadline >= start_date,
        Goal.deadline <= end_date
    ).all()

    for g in goals:
        d_key = g.deadline.isoformat()
        if d_key in events_by_date:
            prog = calculate_goal_progress(g.goal_type, g.target_value, g.current_value, g.start_value, g.deadline)
            g_dict = g.to_dict()
            g_dict["status"] = prog["status"]
            g_dict["progress_percentage"] = prog["percentage"]
            events_by_date[d_key]["goal_deadlines"].append(g_dict)

    return {
        "year": year,
        "month": month,
        "month_name": calendar.month_name[month],
        "days_in_month": num_days,
        "events": events_by_date
    }, None
