from datetime import date, timedelta
from app.models import User, Workout, FitnessRecord, db


def get_user_analytics_summary(user_id):
    """
    Generate comprehensive progress analytics for a user.
    Never fabricates data; returns 'Not enough data yet' where records are sparse.
    Strictly queries only records owned by user_id.
    """
    user = db.session.get(User, user_id)
    if not user:
        return None

    today = date.today()
    seven_days_ago = today - timedelta(days=6)
    thirty_days_ago = today - timedelta(days=29)

    # -------------------------------------------------------------
    # 1. Weight Analytics
    # -------------------------------------------------------------
    weight_records = FitnessRecord.query.filter(
        FitnessRecord.user_id == user_id,
        FitnessRecord.weight.isnot(None)
    ).order_by(FitnessRecord.record_date.asc(), FitnessRecord.id.asc()).all()

    if weight_records:
        starting_weight = weight_records[0].weight
        current_weight = weight_records[-1].weight
        total_change = round(current_weight - starting_weight, 1)

        if len(weight_records) >= 2:
            change_from_prev = round(current_weight - weight_records[-2].weight, 1)
        else:
            change_from_prev = 0.0
    elif user.weight:
        starting_weight = user.weight
        current_weight = user.weight
        total_change = 0.0
        change_from_prev = 0.0
    else:
        starting_weight = None
        current_weight = None
        total_change = None
        change_from_prev = None

    # 7-day trend
    rec_7d = [r for r in weight_records if r.record_date >= seven_days_ago]
    if len(rec_7d) >= 2:
        trend_7d = f"{round(rec_7d[-1].weight - rec_7d[0].weight, 1):+0.1f} kg"
    else:
        trend_7d = "Not enough data yet"

    # 30-day trend
    rec_30d = [r for r in weight_records if r.record_date >= thirty_days_ago]
    if len(rec_30d) >= 2:
        trend_30d = f"{round(rec_30d[-1].weight - rec_30d[0].weight, 1):+0.1f} kg"
    else:
        trend_30d = "Not enough data yet"

    # -------------------------------------------------------------
    # 2. Workout Analytics
    # -------------------------------------------------------------
    all_workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.workout_date.asc()).all()
    total_workouts = len(all_workouts)
    total_duration_mins = sum(w.duration for w in all_workouts)

    workouts_7d = [w for w in all_workouts if w.workout_date >= seven_days_ago]
    workouts_30d = [w for w in all_workouts if w.workout_date >= thirty_days_ago]

    workouts_this_week = len(workouts_7d)
    workouts_this_month = len(workouts_30d)

    # Calculate average workouts per week based on date span
    if total_workouts > 0:
        first_w_date = all_workouts[0].workout_date
        span_days = max(1, (today - first_w_date).days + 1)
        span_weeks = max(1.0, span_days / 7.0)
        avg_workouts_per_week = round(total_workouts / span_weeks, 1)
    else:
        avg_workouts_per_week = 0.0

    # 30-Day Workout Activity Rate (Consistency metric)
    # Distinct active workout days out of the last 30 calendar days
    active_days_30d = len(set(w.workout_date for w in workouts_30d))
    activity_rate_30d = round((active_days_30d / 30.0) * 100, 1)

    # -------------------------------------------------------------
    # 3. Fitness & Nutrition Analytics
    # -------------------------------------------------------------
    fitness_records = FitnessRecord.query.filter_by(user_id=user_id).order_by(FitnessRecord.record_date.desc()).all()

    water_vals = [r.water_intake for r in fitness_records if r.water_intake is not None]
    avg_water = round(sum(water_vals) / len(water_vals), 2) if water_vals else 0.0

    cal_vals = [r.calories_consumed for r in fitness_records if r.calories_consumed is not None]
    avg_cal_consumed = int(sum(cal_vals) / len(cal_vals)) if cal_vals else 0

    cals_burned_vals = [w.calories_burned for w in all_workouts]
    avg_cal_burned = round(sum(cals_burned_vals) / len(cals_burned_vals), 1) if cals_burned_vals else 0.0

    latest_rec = fitness_records[0] if fitness_records else None
    latest_metrics = {
        "weight": latest_rec.weight if latest_rec else user.weight,
        "water": latest_rec.water_intake if latest_rec else 0.0,
        "calories": latest_rec.calories_consumed if latest_rec else 0,
        "date": latest_rec.record_date.isoformat() if latest_rec else None
    }

    return {
        "success": True,
        "weight_analytics": {
            "current_weight": current_weight,
            "starting_weight": starting_weight,
            "change_from_previous": change_from_prev,
            "total_change": total_change,
            "trend_7d": trend_7d,
            "trend_30d": trend_30d
        },
        "workout_analytics": {
            "total_workouts": total_workouts,
            "workouts_this_week": workouts_this_week,
            "workouts_this_month": workouts_this_month,
            "avg_workouts_per_week": avg_workouts_per_week,
            "total_duration_minutes": total_duration_mins,
            "activity_rate_30d": activity_rate_30d,
            "active_days_last_30": active_days_30d
        },
        "fitness_analytics": {
            "average_water_intake": avg_water,
            "average_calories_consumed": avg_cal_consumed,
            "average_calories_burned": avg_cal_burned,
            "latest_metrics": latest_metrics
        }
    }
