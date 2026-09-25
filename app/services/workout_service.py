from datetime import date, datetime, timedelta
from app.models import db, Workout


VALID_EXERCISE_TYPES = [
    'Strength',
    'Cardio',
    'Running',
    'Cycling',
    'Walking',
    'Yoga',
    'Other'
]


def create_workout(user_id, data):
    """
    Validate and create a new workout for a user.
    Returns (workout, error_message).
    """
    name = (data.get('exercise_name') or '').strip()
    if not name:
        return None, "Exercise name is required"
    if len(name) > 120:
        return None, "Exercise name cannot exceed 120 characters"

    ex_type = (data.get('exercise_type') or '').strip()
    if not ex_type or ex_type not in VALID_EXERCISE_TYPES:
        return None, f"Exercise type must be one of: {', '.join(VALID_EXERCISE_TYPES)}"

    # Duration validation (in minutes)
    try:
        duration = int(data.get('duration', 0))
        if duration <= 0 or duration > 1440:
            return None, "Duration must be between 1 and 1440 minutes (24 hours)"
    except (ValueError, TypeError):
        return None, "Invalid duration value"

    # Calories burned validation
    try:
        calories = float(data.get('calories_burned', 0))
        if calories < 0 or calories > 10000:
            return None, "Calories burned must be between 0 and 10,000 kcal"
    except (ValueError, TypeError):
        return None, "Invalid calories burned value"

    # Workout date validation
    w_date_raw = data.get('workout_date')
    if w_date_raw:
        try:
            if isinstance(w_date_raw, str):
                workout_date = datetime.strptime(w_date_raw, '%Y-%m-%d').date()
            elif isinstance(w_date_raw, (date, datetime)):
                workout_date = w_date_raw if isinstance(w_date_raw, date) else w_date_raw.date()
            else:
                return None, "Invalid workout date format. Use YYYY-MM-DD"
        except ValueError:
            return None, "Invalid workout date format. Use YYYY-MM-DD"
    else:
        workout_date = date.today()

    workout = Workout(
        user_id=user_id,
        exercise_name=name,
        exercise_type=ex_type,
        duration=duration,
        calories_burned=calories,
        workout_date=workout_date
    )

    try:
        db.session.add(workout)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return None, f"Database error: {str(e)}"

    return workout, None


def get_workouts(user_id, limit=None, order_desc=True):
    """Retrieve workouts for the specified user with user ownership enforcement."""
    query = Workout.query.filter_by(user_id=user_id)
    if order_desc:
        query = query.order_by(Workout.workout_date.desc(), Workout.id.desc())
    else:
        query = query.order_by(Workout.workout_date.asc(), Workout.id.asc())

    if limit:
        query = query.limit(limit)

    return query.all()


def get_workout_by_id(workout_id, user_id):
    """Retrieve a single workout, strictly verifying user ownership."""
    return Workout.query.filter_by(id=workout_id, user_id=user_id).first()


def delete_workout(workout_id, user_id):
    """
    Delete a workout record.
    Returns (success: bool, error_message: str or None).
    Enforces strict user ownership: User A cannot delete User B's workout.
    """
    workout = Workout.query.filter_by(id=workout_id, user_id=user_id).first()
    if not workout:
        # Check if it exists for another user to distinguish 403 from 404
        other_workout = Workout.query.filter_by(id=workout_id).first()
        if other_workout:
            return False, "Unauthorized access to workout record"
        return False, "Workout not found"

    try:
        db.session.delete(workout)
        db.session.commit()
        return True, None
    except Exception as e:
        db.session.rollback()
        return False, f"Database error: {str(e)}"


def get_recent_workouts(user_id, limit=5):
    """Get the most recent workouts for the dashboard."""
    workouts = get_workouts(user_id, limit=limit, order_desc=True)
    return [w.to_dict() for w in workouts]


def get_workout_stats(user_id):
    """
    Calculate today's workouts, weekly workout count, total calories,
    and a 7-day activity breakdown for Chart.js.
    """
    today = date.today()
    seven_days_ago = today - timedelta(days=6)

    # Today's workouts
    today_workouts = Workout.query.filter(
        Workout.user_id == user_id,
        Workout.workout_date == today
    ).all()
    today_count = len(today_workouts)
    today_calories = sum(w.calories_burned for w in today_workouts)

    # Last 7 days workouts
    weekly_workouts = Workout.query.filter(
        Workout.user_id == user_id,
        Workout.workout_date >= seven_days_ago,
        Workout.workout_date <= today
    ).all()
    weekly_count = len(weekly_workouts)
    weekly_calories = sum(w.calories_burned for w in weekly_workouts)

    # 7-day daily breakdown for activity chart
    daily_map = {seven_days_ago + timedelta(days=i): {"count": 0, "calories": 0.0} for i in range(7)}
    for w in weekly_workouts:
        if w.workout_date in daily_map:
            daily_map[w.workout_date]["count"] += 1
            daily_map[w.workout_date]["calories"] += w.calories_burned

    chart_labels = []
    chart_counts = []
    chart_calories = []

    for d in sorted(daily_map.keys()):
        chart_labels.append(d.strftime('%a (%b %d)'))  # e.g., 'Mon (Sep 22)'
        chart_counts.append(daily_map[d]["count"])
        chart_calories.append(round(daily_map[d]["calories"], 1))

    return {
        "today_count": today_count,
        "today_calories": round(today_calories, 1),
        "weekly_count": weekly_count,
        "weekly_calories": round(weekly_calories, 1),
        "activity_chart": {
            "labels": chart_labels,
            "counts": chart_counts,
            "calories": chart_calories
        }
    }
