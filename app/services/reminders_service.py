from datetime import date, timedelta
from app.models import db, User, Workout, FitnessRecord, Goal, ReminderPreference


def get_or_create_reminder_preferences(user_id):
    """Retrieve or initialize default reminder settings for a user."""
    pref = ReminderPreference.query.filter_by(user_id=user_id).first()
    if not pref:
        pref = ReminderPreference(
            user_id=user_id,
            workout_reminder=True,
            daily_fitness_reminder=True,
            goal_deadline_reminder=True,
            hydration_reminder=True,
            hydration_target=2.0
        )
        try:
            db.session.add(pref)
            db.session.commit()
        except Exception:
            db.session.rollback()
            pref = ReminderPreference.query.filter_by(user_id=user_id).first()

    return pref


def update_reminder_preferences(user_id, data):
    """
    Update user-configured reminder settings.
    Enforces user ownership and validates values.
    """
    pref = get_or_create_reminder_preferences(user_id)

    if 'workout_reminder' in data:
        pref.workout_reminder = bool(data['workout_reminder'])
    if 'daily_fitness_reminder' in data:
        pref.daily_fitness_reminder = bool(data['daily_fitness_reminder'])
    if 'goal_deadline_reminder' in data:
        pref.goal_deadline_reminder = bool(data['goal_deadline_reminder'])
    if 'hydration_reminder' in data:
        pref.hydration_reminder = bool(data['hydration_reminder'])

    if 'hydration_target' in data:
        try:
            val = float(data['hydration_target'])
            if val <= 0 or val > 20.0:
                return None, "Hydration target must be between 0.1 and 20.0 Litres"
            pref.hydration_target = round(val, 2)
        except (ValueError, TypeError):
            return None, "Invalid hydration target number"

    try:
        db.session.commit()
        return pref, None
    except Exception as e:
        db.session.rollback()
        return None, f"Database error: {str(e)}"


def get_active_reminders(user_id):
    """
    Dynamically evaluate user reminders based on enabled preferences
    and actual logged records for today.
    """
    pref = get_or_create_reminder_preferences(user_id)
    today = date.today()
    active_reminders = []

    # 1. Daily Fitness Record Reminder
    if pref.daily_fitness_reminder:
        today_record = FitnessRecord.query.filter_by(user_id=user_id, record_date=today).first()
        if not today_record or (today_record.weight is None and today_record.water_intake is None and today_record.calories_consumed is None):
            active_reminders.append({
                "id": "daily_fitness",
                "type": "fitness",
                "title": "Daily Health Check-in",
                "message": "You haven't logged today's health metrics yet.",
                "urgency": "normal"
            })

    # 2. Workout Reminder
    if pref.workout_reminder:
        today_workouts = Workout.query.filter_by(user_id=user_id, workout_date=today).all()
        if not today_workouts:
            active_reminders.append({
                "id": "daily_workout",
                "type": "workout",
                "title": "Workout Reminder",
                "message": "Remember to stay active today! No workouts logged yet.",
                "urgency": "normal"
            })

    # 3. Goal Deadline Reminders
    if pref.goal_deadline_reminder:
        goals = Goal.query.filter(Goal.user_id == user_id, Goal.deadline.isnot(None)).all()
        for g in goals:
            days_left = (g.deadline - today).days
            # Check if achieved
            is_done = False
            if "loss" in g.goal_type.lower():
                is_done = g.current_value <= g.target_value if g.current_value > 0 else False
            else:
                is_done = g.current_value >= g.target_value

            if not is_done:
                if days_left < 0:
                    active_reminders.append({
                        "id": f"goal_overdue_{g.id}",
                        "type": "goal",
                        "title": "Goal Overdue",
                        "message": f"'{g.goal_type}' target deadline passed {abs(days_left)} days ago.",
                        "urgency": "high"
                    })
                elif days_left <= 3:
                    active_reminders.append({
                        "id": f"goal_due_{g.id}",
                        "type": "goal",
                        "title": "Goal Deadline Approaching",
                        "message": f"'{g.goal_type}' deadline is in {days_left} day{'s' if days_left != 1 else ''}!",
                        "urgency": "medium"
                    })

    # 4. Hydration Tracking Reminder
    if pref.hydration_reminder:
        today_record = FitnessRecord.query.filter_by(user_id=user_id, record_date=today).first()
        today_water = today_record.water_intake if today_record and today_record.water_intake is not None else 0.0
        if today_water < pref.hydration_target:
            active_reminders.append({
                "id": "hydration",
                "type": "hydration",
                "title": "Hydration Reminder",
                "message": f"Stay hydrated! Logged {today_water:0.1f}L toward your {pref.hydration_target:0.1f}L target.",
                "urgency": "low"
            })

    return active_reminders
