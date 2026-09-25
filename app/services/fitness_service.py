from datetime import date, datetime, timedelta
from app.models import db, FitnessRecord, User


def calculate_bmi(weight_kg, height_cm):
    """
    Calculate Body Mass Index (BMI).
    Formula: weight (kg) / (height (m))^2
    Returns rounded float to 1 decimal place, or None if invalid.
    """
    if weight_kg is None or height_cm is None:
        return None
    try:
        w = float(weight_kg)
        h = float(height_cm)
    except (ValueError, TypeError):
        return None

    if w <= 0 or h <= 0:
        return None

    # Convert height from cm to meters
    height_m = h / 100.0
    bmi = w / (height_m ** 2)
    return round(bmi, 1)


def get_bmi_category(bmi):
    """
    Determine the standard informational BMI category for a given BMI value:
    - Underweight: < 18.5
    - Normal: 18.5 - 24.9
    - Overweight: 25.0 - 29.9
    - Obese: >= 30.0
    Presented as a general fitness reference, not a medical diagnosis.
    """
    if bmi is None:
        return "Not Calculated"
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi <= 24.9:
        return "Normal"
    elif 25.0 <= bmi <= 29.9:
        return "Overweight"
    else:
        return "Obese"


def calculate_goal_progress(goal_type, target_value, current_value):
    """
    Calculate progress percentage and completion status for a goal.
    Handles potential division by zero, negative values, and clamps output to 0-100%.
    """
    try:
        target = float(target_value)
        current = float(current_value) if current_value is not None else 0.0
    except (ValueError, TypeError):
        return {"percentage": 0.0, "is_completed": False}

    if target <= 0:
        return {"percentage": 0.0, "is_completed": False}

    if current < 0:
        return {"percentage": 0.0, "is_completed": False}

    if goal_type and "loss" in goal_type.lower():
        # For weight loss:
        # If current <= target (and current > 0), goal is achieved (100%)
        # If current > target, progress towards target is (target / current) * 100
        if current <= target:
            pct = 100.0
        else:
            pct = max(0.0, min(100.0, round((target / current) * 100, 1))) if current > 0 else 0.0
    else:
        # Standard progress (Weight Gain, Muscle Building, General Fitness, Endurance):
        if current >= target:
            pct = 100.0
        else:
            pct = max(0.0, min(100.0, round((current / target) * 100, 1)))

    is_completed = pct >= 100.0
    return {
        "percentage": pct,
        "is_completed": is_completed
    }


def save_fitness_record(user_id, data):
    """
    Create or update a daily fitness record for a user.
    Also syncs user's current weight in the User profile if weight is supplied.
    Returns (record, error_message).
    """
    user = db.session.get(User, user_id)
    if not user:
        return None, "User not found"

    # Date parsing
    rec_date_str = data.get('record_date')
    if rec_date_str:
        try:
            if isinstance(rec_date_str, str):
                rec_date = datetime.strptime(rec_date_str, '%Y-%m-%d').date()
            elif isinstance(rec_date_str, (date, datetime)):
                rec_date = rec_date_str if isinstance(rec_date_str, date) else rec_date_str.date()
            else:
                return None, "Invalid date format. Use YYYY-MM-DD"
        except ValueError:
            return None, "Invalid date format. Use YYYY-MM-DD"
    else:
        rec_date = date.today()

    # Weight validation
    weight = data.get('weight')
    if weight is not None and weight != "":
        try:
            weight = float(weight)
            if weight <= 0 or weight > 500:
                return None, "Weight must be between 1 and 500 kg"
        except (ValueError, TypeError):
            return None, "Invalid weight value"
    else:
        weight = None

    # Water validation
    water = data.get('water_intake')
    if water is not None and water != "":
        try:
            water = float(water)
            if water < 0 or water > 20:
                return None, "Water intake must be between 0 and 20 Litres"
        except (ValueError, TypeError):
            return None, "Invalid water intake value"
    else:
        water = None

    # Calories validation
    calories = data.get('calories_consumed')
    if calories is not None and calories != "":
        try:
            calories = int(calories)
            if calories < 0 or calories > 20000:
                return None, "Calories must be between 0 and 20,000 kcal"
        except (ValueError, TypeError):
            return None, "Invalid calories value"
    else:
        calories = None

    # Check if a record exists for this date
    record = FitnessRecord.query.filter_by(user_id=user_id, record_date=rec_date).first()
    if not record:
        record = FitnessRecord(user_id=user_id, record_date=rec_date)
        db.session.add(record)

    if weight is not None:
        record.weight = weight
        user.weight = weight  # Update profile weight
    if water is not None:
        record.water_intake = water
    if calories is not None:
        record.calories_consumed = calories

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return None, f"Database error: {str(e)}"

    return record, None


def get_user_fitness_history(user_id, limit=30):
    """Get fitness records ordered by date."""
    records = FitnessRecord.query.filter_by(user_id=user_id)\
        .order_by(FitnessRecord.record_date.desc())\
        .limit(limit)\
        .all()
    # Reverse to chronological order for charts
    return [r.to_dict() for r in reversed(records)]


def get_daily_fitness_summary(user_id, target_date=None):
    """
    Get fitness overview for dashboard.
    Falls back to user profile weight if no daily record logged.
    """
    if target_date is None:
        target_date = date.today()

    user = db.session.get(User, user_id)
    if not user:
        return None

    today_record = FitnessRecord.query.filter_by(user_id=user_id, record_date=target_date).first()

    # Weight resolution: today's record -> latest recorded weight -> user profile weight
    current_weight = None
    if today_record and today_record.weight is not None:
        current_weight = today_record.weight
    else:
        latest_record = FitnessRecord.query.filter(
            FitnessRecord.user_id == user_id,
            FitnessRecord.weight.isnot(None)
        ).order_by(FitnessRecord.record_date.desc()).first()
        if latest_record and latest_record.weight is not None:
            current_weight = latest_record.weight
        else:
            current_weight = user.weight

    water = today_record.water_intake if today_record and today_record.water_intake is not None else 0.0
    calories = today_record.calories_consumed if today_record and today_record.calories_consumed is not None else 0

    bmi = calculate_bmi(current_weight, user.height)
    bmi_cat = get_bmi_category(bmi)

    return {
        "weight": current_weight,
        "bmi": bmi,
        "bmi_category": bmi_cat,
        "water": water,
        "calories": calories,
        "height": user.height,
        "record_date": target_date.isoformat()
    }
