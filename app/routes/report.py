from flask import Blueprint, Response, make_response, jsonify
from app.routes import login_required, get_current_user
from app.services.report_service import (
    generate_fitness_csv,
    generate_workouts_csv,
    generate_goals_csv,
    generate_summary_csv,
    generate_fitness_pdf
)

report_bp = Blueprint('report', __name__)


@report_bp.route('/api/reports/fitness.csv', methods=['GET'])
@login_required
def api_export_fitness_csv():
    user = get_current_user()
    csv_data = generate_fitness_csv(user.id)

    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=fittrack_fitness_records.csv'
    return response


@report_bp.route('/api/reports/workouts.csv', methods=['GET'])
@login_required
def api_export_workouts_csv():
    user = get_current_user()
    csv_data = generate_workouts_csv(user.id)

    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=fittrack_workouts.csv'
    return response


@report_bp.route('/api/reports/goals.csv', methods=['GET'])
@login_required
def api_export_goals_csv():
    user = get_current_user()
    csv_data = generate_goals_csv(user.id)

    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=fittrack_goals.csv'
    return response


@report_bp.route('/api/reports/summary.csv', methods=['GET'])
@login_required
def api_export_summary_csv():
    user = get_current_user()
    csv_data = generate_summary_csv(user.id)

    response = make_response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=fittrack_summary.csv'
    return response


@report_bp.route('/api/reports/fitness.pdf', methods=['GET'])
@login_required
def api_export_fitness_pdf():
    user = get_current_user()
    pdf_bytes = generate_fitness_pdf(user.id)
    if not pdf_bytes:
        return jsonify({'success': False, 'message': 'Failed to generate PDF report'}), 500

    response = make_response(pdf_bytes)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=fittrack_report_{user.id}.pdf'
    return response
