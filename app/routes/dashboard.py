from flask import Blueprint, jsonify, render_template, session
from app.routes import login_required, get_current_user
from app.models import Goal
from app.services.fitness_service import (
    get_daily_fitness_summary,
    get_user_fitness_history,
    calculate_goal_progress
)
from app.services.workout_service import (
    get_workout_stats,
    get_recent_workouts
)

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/', methods=['GET'])
@login_required
def index():
    user = get_current_user()
    return render_template('dashboard.html', user=user)


@dashboard_bp.route('/api/dashboard', methods=['GET'])
@login_required
def api_dashboard():
    user = get_current_user()
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    # 1. Daily fitness summary (weight, water, calories, BMI, category)
    fitness_summary = get_daily_fitness_summary(user.id)

    # 2. Workout statistics (today's count, weekly count, calories, 7-day activity)
    workout_stats = get_workout_stats(user.id)

    # 3. Recent workouts (latest 5)
    recent_workouts = get_recent_workouts(user.id, limit=5)

    # 4. Goals with computed progress
    user_goals = Goal.query.filter_by(user_id=user.id).all()
    goals_data = []
    for g in user_goals:
        progress_info = calculate_goal_progress(g.goal_type, g.target_value, g.current_value)
        g_dict = g.to_dict()
        g_dict['progress_percentage'] = progress_info['percentage']
        g_dict['is_completed'] = progress_info['is_completed']
        goals_data.append(g_dict)

    # 5. Weight history for Chart.js
    fitness_history = get_user_fitness_history(user.id, limit=15)
    weight_labels = []
    weight_data = []
    for rec in fitness_history:
        if rec.get('weight') is not None:
            weight_labels.append(rec['record_date'])
            weight_data.append(rec['weight'])

    # If only 1 or 0 weight records exist, but user has profile weight, include it
    if not weight_data and user.weight:
        weight_labels.append("Initial")
        weight_data.append(user.weight)

    response_data = {
        'success': True,
        'user': user.to_dict(),
        'fitness': {
            'weight': fitness_summary['weight'],
            'bmi': fitness_summary['bmi'],
            'bmi_category': fitness_summary['bmi_category'],
            'water': fitness_summary['water'],
            'calories': fitness_summary['calories']
        },
        'workouts': {
            'today': workout_stats['today_count'],
            'weekly': workout_stats['weekly_count'],
            'today_calories': workout_stats['today_calories'],
            'weekly_calories': workout_stats['weekly_calories']
        },
        'recent_workouts': recent_workouts,
        'goals': goals_data,
        'charts': {
            'weight_history': {
                'labels': weight_labels,
                'weights': weight_data
            },
            'workout_activity': workout_stats['activity_chart']
        }
    }

    return jsonify(response_data), 200
