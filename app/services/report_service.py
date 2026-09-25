import csv
import io
from datetime import date
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from app.models import db, User, Workout, FitnessRecord, Goal
from app.services.fitness_service import calculate_bmi, get_bmi_category, calculate_goal_progress
from app.services.analytics_service import get_user_analytics_summary


def generate_fitness_csv(user_id):
    """Generate CSV string of user-owned fitness records."""
    records = FitnessRecord.query.filter_by(user_id=user_id).order_by(FitnessRecord.record_date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Record Date', 'Weight (kg)', 'Water Intake (L)', 'Calories Consumed (kcal)', 'Created At'])

    for r in records:
        writer.writerow([
            r.record_date.isoformat() if r.record_date else '',
            r.weight if r.weight is not None else '',
            r.water_intake if r.water_intake is not None else '',
            r.calories_consumed if r.calories_consumed is not None else '',
            r.created_at.isoformat() if r.created_at else ''
        ])

    return output.getvalue()


def generate_workouts_csv(user_id):
    """Generate CSV string of user-owned workout sessions."""
    workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.workout_date.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Workout Date', 'Exercise Name', 'Exercise Type', 'Duration (mins)', 'Calories Burned (kcal)', 'Created At'])

    for w in workouts:
        writer.writerow([
            w.workout_date.isoformat() if w.workout_date else '',
            w.exercise_name,
            w.exercise_type,
            w.duration,
            w.calories_burned,
            w.created_at.isoformat() if w.created_at else ''
        ])

    return output.getvalue()


def generate_goals_csv(user_id):
    """Generate CSV string of user-owned goals with lifecycle progress."""
    goals = Goal.query.filter_by(user_id=user_id).order_by(Goal.created_at.desc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Goal Type', 'Target Value', 'Current Value', 'Start Value', 'Deadline', 'Progress (%)', 'Status'])

    for g in goals:
        prog = calculate_goal_progress(g.goal_type, g.target_value, g.current_value, g.start_value, g.deadline)
        writer.writerow([
            g.goal_type,
            g.target_value,
            g.current_value,
            g.start_value if g.start_value is not None else '',
            g.deadline.isoformat() if g.deadline else '',
            prog['percentage'],
            prog['status']
        ])

    return output.getvalue()


def generate_summary_csv(user_id):
    """Generate overall summary CSV for the user."""
    user = db.session.get(User, user_id)
    if not user:
        return ""

    bmi = calculate_bmi(user.weight, user.height)
    bmi_cat = get_bmi_category(bmi)
    analytics = get_user_analytics_summary(user_id)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['User Name', user.name])
    writer.writerow(['Email', user.email])
    writer.writerow(['Height (cm)', user.height or ''])
    writer.writerow(['Current Weight (kg)', user.weight or ''])
    writer.writerow(['BMI Index', bmi or ''])
    writer.writerow(['BMI Category', bmi_cat])
    writer.writerow(['Total Workouts Logged', analytics['workout_analytics']['total_workouts']])
    writer.writerow(['Workouts This Week', analytics['workout_analytics']['workouts_this_week']])
    writer.writerow(['Workouts This Month', analytics['workout_analytics']['workouts_this_month']])
    writer.writerow(['30-Day Activity Rate (%)', analytics['workout_analytics']['activity_rate_30d']])
    writer.writerow(['Average Water Intake (L)', analytics['fitness_analytics']['average_water_intake']])
    writer.writerow(['Average Calories Burned (kcal)', analytics['fitness_analytics']['average_calories_burned']])

    return output.getvalue()


def generate_fitness_pdf(user_id):
    """
    Generate an informational fitness report in PDF format using ReportLab.
    Returns bytes of the PDF file.
    """
    user = db.session.get(User, user_id)
    if not user:
        return None

    bmi = calculate_bmi(user.weight, user.height)
    bmi_cat = get_bmi_category(bmi)
    analytics = get_user_analytics_summary(user_id)
    workouts = Workout.query.filter_by(user_id=user_id).order_by(Workout.workout_date.desc()).limit(10).all()
    goals = Goal.query.filter_by(user_id=user_id).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#10b981')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#6b7280'),
        spaceAfter=15
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=12,
        spaceAfter=6
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Italic'],
        fontSize=8,
        textColor=colors.HexColor('#9ca3af'),
        spaceBefore=15
    )

    elements = []

    # Title & Header
    elements.append(Paragraph("FitTrack — Personal Fitness & Performance Report", title_style))
    elements.append(Paragraph(f"Generated for <b>{user.name}</b> ({user.email}) &bull; Date: {date.today().isoformat()}", subtitle_style))

    # 1. Profile & Health Metrics Table
    elements.append(Paragraph("User Profile & Health Summary", heading_style))
    profile_data = [
        ['Parameter', 'Current Value', 'Parameter', 'Current Value'],
        ['Name', user.name, 'Height', f"{user.height} cm" if user.height else 'N/A'],
        ['Age', str(user.age) if user.age else 'N/A', 'Weight', f"{user.weight} kg" if user.weight else 'N/A'],
        ['Gender', user.gender or 'N/A', 'BMI Index', f"{bmi} ({bmi_cat})" if bmi else 'N/A'],
        ['Primary Goal', user.fitness_goal or 'General Fitness', '30-Day Activity Rate', f"{analytics['workout_analytics']['activity_rate_30d']}%"]
    ]
    t_profile = Table(profile_data, colWidths=[130, 140, 130, 140])
    t_profile.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    elements.append(t_profile)

    # 2. Workout History Summary (Latest 10)
    elements.append(Paragraph("Recent Workout Sessions (Latest)", heading_style))
    workout_data = [['Date', 'Exercise Name', 'Type', 'Duration', 'Calories Burned']]
    if workouts:
        for w in workouts:
            workout_data.append([
                w.workout_date.isoformat(),
                w.exercise_name,
                w.exercise_type,
                f"{w.duration} mins",
                f"{w.calories_burned} kcal"
            ])
    else:
        workout_data.append(['None', 'No workouts recorded yet', '-', '-', '-'])

    t_workout = Table(workout_data, colWidths=[75, 175, 100, 90, 100])
    t_workout.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    elements.append(t_workout)

    # 3. Active Goals
    elements.append(Paragraph("Active Fitness Goals", heading_style))
    goals_data = [['Goal Type', 'Target', 'Current', 'Progress', 'Status', 'Deadline']]
    if goals:
        for g in goals:
            prog = calculate_goal_progress(g.goal_type, g.target_value, g.current_value, g.start_value, g.deadline)
            goals_data.append([
                g.goal_type,
                str(g.target_value),
                str(g.current_value),
                f"{prog['percentage']}%",
                prog['status'],
                g.deadline.isoformat() if g.deadline else 'None'
            ])
    else:
        goals_data.append(['None', '-', '-', '-', 'No active goals', '-'])

    t_goals = Table(goals_data, colWidths=[120, 80, 80, 80, 90, 90])
    t_goals.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    elements.append(t_goals)

    # Informational Disclaimer
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "Notice: FitTrack is a personal health tracking application. All fitness metrics and BMI scores are provided for general personal information and do not constitute medical diagnosis or advice.",
        disclaimer_style
    ))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
