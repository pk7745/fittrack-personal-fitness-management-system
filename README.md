# FitTrack — Personal Fitness Management System

> A production-grade, full-stack personal fitness tracking web application built with Python, Flask, SQLAlchemy, SQLite, HTML5, modern CSS3, and Vanilla JavaScript.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.x-green.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red.svg)](https://www.sqlalchemy.org/)
[![Tests](https://img.shields.io/badge/Tests-36%2F36%20Passed-brightgreen.svg)]()
[![Version](https://img.shields.io/badge/Version-v1.1%20Stable-emerald.svg)]()
[![License](https://img.shields.io/badge/License-MIT-purple.svg)]()

---

## 1. Overview

**FitTrack** provides individuals with an intuitive, responsive, and data-driven platform to monitor daily health and fitness metrics. Built with a clean layered architecture and zero reliance on heavy frontend frameworks, FitTrack demonstrates clean monolithic web development principles, robust session authentication, complete CRUD operations, automated BMI calculation, interactive Chart.js analytics, and strict user-data authorization boundaries.

### What is New in v1.1 (Real-Time & Productivity Enhancements)
- **Real-Time Dashboard Updates**: Granular DOM updates without page reloads after any workout, metric, or goal action.
- **Advanced Progress Analytics**: Weight trajectory trends (7-day, 30-day, previous change, total change), 30-day workout activity consistency rate, and daily nutrition averages.
- **Goal Lifecycle & Baseline Progress**: Goals support baseline `start_value` for mathematically sound progress tracking, target `deadline`, dynamic status (`Active`, `Completed`, `Overdue`), and remaining days countdown.
- **Smart Reminders**: User-configurable in-app alerts and browser notifications for daily check-ins, workouts, goal deadlines, and hydration tracking.
- **Multi-Format Reports (CSV & PDF)**: Authenticated user-owned export of fitness logs, workout sessions, goals, summary statistics, and a downloadable PDF report generated via ReportLab.
- **Workout Calendar**: Interactive monthly calendar highlighting workout sessions, health metric check-ins, and upcoming goal deadlines.

---

## 2. Key Features

- **User Authentication & Session Management**:
  - Secure registration, login, and session persistence using Werkzeug password hashing.
  - Ownership enforcement preventing cross-user data tampering (returns `403 Forbidden`).
- **Dynamic Real-Time Dashboard**:
  - Time-of-day greeting (e.g., *"Good evening, Pavan 👋"*).
  - 5 Real-time Stat Cards: BMI Index with WHO category badge, Current Weight, Daily Water Intake, Daily Calorie Consumption, and Daily/Weekly Workout count.
- **Automated Health & BMI Calculations**:
  - Automatic calculation of BMI (\(\text{weight} / \text{height}^2\)).
  - Informational WHO classifications: Underweight, Normal, Overweight, Obese.
- **Workout Tracking & Analytics (CRUD)**:
  - Log workouts with exercise type (Strength, Cardio, Running, Cycling, Walking, Yoga, Other), duration, calories burned, and date.
  - Instant UI update without full-page reloads.
  - One-click deletion with confirmation dialogs.
- **Daily Health Logging**:
  - Track weight, water intake (L), and caloric consumption (kcal) per day.
  - Automatically updates latest profile weight and recalculates live BMI.
- **Goal Management with Baseline Progress**:
  - Set goals for Weight Loss, Weight Gain, Muscle Building, General Fitness, or Endurance.
  - Precise progress calculation using `start_value` (e.g., \((80 - 75) / (80 - 70) \times 100 = 50\%\)).
  - Status classification (`Active`, `Completed`, `Overdue`) and remaining days indicator.
- **Interactive Visual Analytics & Calendar**:
  - **Weight Progress Chart**: Line graph illustrating weight trajectory over time.
  - **7-Day Workout Activity Chart**: Dual-axis bar and line chart illustrating session frequency and calories burned.
  - **Monthly Workout Calendar**: Interactive date grid highlighting logged workouts, daily metrics, and goal deadlines.

---

## 3. Technology Stack

- **Backend**: Python 3.10+, Flask 3.x, Flask-SQLAlchemy 3.x, Werkzeug (security), ReportLab 4.x (PDF export)
- **Database**: SQLite with SQLAlchemy ORM (cascade deletes, indexing, foreign keys with `PRAGMA foreign_keys=ON`)
- **Frontend**: HTML5, Modern CSS3 (custom design system), Vanilla JavaScript (ES6+, Fetch API, async/await)
- **Data Visualization**: Chart.js (via CDN)
- **Testing**: pytest

---

## 4. Architecture

FitTrack implements a clean, layered architecture with strict separation of concerns:

```
[ Frontend (HTML5 / Modern CSS3 / Vanilla JS / Chart.js) ]
                        ↓ (Fetch API)
[ REST API / Flask Blueprints (Routes & Controllers) ]
                        ↓
[ Service Layer (fitness, workout, analytics, reminders, report, calendar) ]
                        ↓
[ SQLAlchemy ORM Models (User, Workout, FitnessRecord, Goal, ReminderPreference) ]
                        ↓
[ SQLite Database (instance/fittrack.db) ]
```

---

## 5. Project Structure

```
personal-fitness-management-system/
│
├── app/
│   ├── __init__.py               # Flask Application Factory & SQLite pragma migration
│   ├── models/
│   │   ├── __init__.py           # Database instance & model exports
│   │   ├── user.py               # User model & password hashing
│   │   ├── workout.py            # Workout session model
│   │   ├── fitness_record.py     # Daily health metrics model
│   │   ├── goal.py               # Goal model with start_value & deadline (v1.1)
│   │   └── reminder.py           # Reminder preferences model (v1.1)
│   │
│   ├── routes/
│   │   ├── __init__.py           # Auth decorators (@login_required) & helpers
│   │   ├── auth.py               # Authentication views & REST endpoints
│   │   ├── dashboard.py          # Dashboard view & aggregated metrics API
│   │   ├── workout.py            # Workout CRUD endpoints
│   │   ├── fitness.py            # Fitness metrics endpoints
│   │   ├── profile.py            # User profile endpoints
│   │   ├── goal.py               # Fitness goal endpoints (v1.1 enhanced)
│   │   ├── analytics.py          # Advanced analytics endpoints (v1.1)
│   │   ├── reminder.py           # Smart reminder endpoints (v1.1)
│   │   ├── report.py             # CSV and PDF report export endpoints (v1.1)
│   │   └── calendar.py           # Workout calendar endpoints (v1.1)
│   │
│   ├── services/
│   │   ├── __init__.py           # Service exports
│   │   ├── fitness_service.py    # BMI calculation, categories & goal progress
│   │   ├── workout_service.py    # Workout queries, stats & chart aggregation
│   │   ├── analytics_service.py  # Weight trends, consistency & fitness averages (v1.1)
│   │   ├── reminders_service.py  # Active reminder evaluation & preferences (v1.1)
│   │   ├── report_service.py     # CSV and ReportLab PDF generator (v1.1)
│   │   └── calendar_service.py   # Monthly calendar event aggregator (v1.1)
│   │
│   ├── templates/
│   │   ├── base.html             # Shell layout, navbar, modals, toasts
│   │   ├── login.html            # User sign in page
│   │   ├── register.html         # User registration page
│   │   └── dashboard.html        # Interactive dashboard with analytics & calendar
│   │
│   └── static/
│       ├── css/
│       │   └── style.css         # Modern dark SaaS design system
│       └── js/
│           ├── toast.js          # Reusable toast notification system
│           ├── api.js            # Standardized fetch wrapper
│           ├── auth.js           # Authentication form handling
│           ├── dashboard.js      # Real-time dashboard state & chart controllers
│           ├── workout.js        # Workout logging & deletion
│           ├── fitness.js        # Daily health metrics modal
│           ├── profile.js        # Profile editing with live BMI preview
│           ├── goal.js           # Goal creation, lifecycle & deletion
│           ├── analytics.js      # Advanced analytics view binding (v1.1)
│           ├── reminders.js      # Reminders banner & notification controller (v1.1)
│           ├── reports.js        # Data export triggers (v1.1)
│           └── calendar.js       # Lightweight monthly calendar component (v1.1)
│
├── instance/
│   └── fittrack.db               # SQLite database file
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # Test fixtures (in-memory SQLite)
│   ├── test_auth.py              # Auth & session test suite
│   ├── test_fitness.py           # Fitness logic & BMI calculation tests
│   ├── test_workout.py           # Workout CRUD & ownership tests
│   ├── test_goal.py              # Goal progress & lifecycle tests
│   ├── test_analytics.py         # Advanced analytics & trends test suite (v1.1)
│   ├── test_reminders.py         # Smart reminders test suite (v1.1)
│   ├── test_reports.py           # CSV and PDF export test suite (v1.1)
│   └── test_calendar.py          # Calendar aggregation test suite (v1.1)
│
├── config.py                     # Dev, Test, Prod configuration classes
├── run.py                        # Application entry point & demo seeder
├── requirements.txt              # Production and test dependencies
├── README.md                     # Comprehensive technical documentation
├── .gitignore                    # Git exclusions
└── .env.example                  # Environment variables template
```

---

## 6. REST API Documentation

### Authentication
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/auth/register` | Register new user account | No |
| `POST` | `/api/auth/login` | Authenticate user & start session | No |
| `POST` | `/api/auth/logout` | Terminate active session | Yes |
| `GET` | `/api/auth/me` | Fetch authenticated user details | Yes |

### Dashboard & Analytics
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/dashboard` | Aggregated user stats, recent workouts, goals, and chart datasets | Yes |
| `GET` | `/api/analytics/summary` | Weight trends, 30-day activity rate, and nutrition averages | Yes |

### Workouts & Calendar
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/workouts` | Retrieve all workouts for logged-in user | Yes |
| `POST` | `/api/workouts` | Create a new workout session | Yes |
| `GET` | `/api/workouts/<id>` | Retrieve specific workout details | Yes |
| `DELETE`| `/api/workouts/<id>` | Delete workout (ownership enforced) | Yes |
| `GET` | `/api/calendar/month` | Monthly workout and goal event calendar | Yes |

### Fitness Metrics
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/fitness` | Retrieve historical daily fitness records | Yes |
| `POST` | `/api/fitness` | Save/update weight, water intake, calories | Yes |
| `DELETE`| `/api/fitness/<id>` | Delete fitness record (ownership enforced) | Yes |

### Profile & Reminders
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/profile` | Retrieve user profile & current BMI | Yes |
| `PUT` | `/api/profile` | Update profile attributes | Yes |
| `GET` | `/api/reminders/preferences` | Retrieve user reminder preferences | Yes |
| `PUT` | `/api/reminders/preferences` | Update reminder preferences | Yes |
| `GET` | `/api/reminders/active` | Get dynamically triggered reminders | Yes |

### Goals
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/goals` | Retrieve all goals with status & remaining days | Yes |
| `POST` | `/api/goals` | Create a new goal with start_value & deadline | Yes |
| `GET` | `/api/goals/<id>` | Retrieve single goal details | Yes |
| `PUT` | `/api/goals/<id>` | Update goal attributes | Yes |
| `DELETE`| `/api/goals/<id>` | Remove fitness goal | Yes |

### Reports & Exports
| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/reports/workouts.csv` | Export workout history to CSV | Yes |
| `GET` | `/api/reports/fitness.csv` | Export health metrics to CSV | Yes |
| `GET` | `/api/reports/goals.csv` | Export goals and lifecycle progress to CSV | Yes |
| `GET` | `/api/reports/summary.csv` | Export overall performance summary to CSV | Yes |
| `GET` | `/api/reports/fitness.pdf` | Download formatted PDF fitness report | Yes |

---

## 7. Installation & Running

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run Application
```bash
python run.py
```
Open your browser at: `http://127.0.0.1:5000`

### Step 3: Seed Demo Data (Optional for Evaluation)
```bash
python run.py seed-demo
python run.py
```
**Demo Account**:
- **Email**: `demo@fittrack.com`
- **Password**: `Password123!`

---

## 8. Automated Testing

FitTrack includes a 36-test automated suite covering authentication, authorization boundaries, BMI calculations, goal lifecycle progress, advanced analytics trends, smart reminders, report generation, and calendar grouping.

Execute tests:
```bash
python -m pytest -v tests/
```

### Test Suite Output:
```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\pky45\.gemini\antigravity\scratch\personal-fitness-management-system
collected 36 items

tests/test_analytics.py::test_unauthenticated_analytics_rejection PASSED [  2%]
tests/test_analytics.py::test_empty_analytics PASSED                     [  5%]
tests/test_analytics.py::test_analytics_aggregation_and_trends PASSED    [  8%]
tests/test_analytics.py::test_analytics_user_isolation PASSED            [ 11%]
tests/test_auth.py::test_register_success PASSED                         [ 13%]
tests/test_auth.py::test_register_duplicate_email PASSED                 [ 16%]
tests/test_auth.py::test_register_validation PASSED                      [ 19%]
tests/test_auth.py::test_login_success PASSED                            [ 22%]
tests/test_auth.py::test_login_invalid_password PASSED                   [ 25%]
tests/test_auth.py::test_logout PASSED                                   [ 27%]
tests/test_auth.py::test_unauthorized_access PASSED                      [ 30%]
tests/test_calendar.py::test_unauthenticated_calendar_rejection PASSED   [ 33%]
tests/test_calendar.py::test_calendar_month_events PASSED                [ 36%]
tests/test_calendar.py::test_calendar_invalid_month PASSED               [ 38%]
tests/test_calendar.py::test_calendar_user_isolation PASSED              [ 41%]
tests/test_fitness.py::test_bmi_calculation PASSED                       [ 44%]
tests/test_fitness.py::test_bmi_categories_and_boundaries PASSED         [ 47%]
tests/test_fitness.py::test_goal_progress_audit_cases PASSED             [ 50%]
tests/test_fitness.py::test_save_fitness_record PASSED                   [ 52%]
tests/test_fitness.py::test_save_fitness_record_invalid PASSED           [ 55%]
tests/test_goal.py::test_create_and_list_goals PASSED                    [ 58%]
tests/test_goal.py::test_update_and_delete_goal PASSED                   [ 61%]
tests/test_goal.py::test_unauthorized_goal_access PASSED                 [ 63%]
tests/test_goal.py::test_goal_with_start_value_and_deadline PASSED       [ 66%]
tests/test_reminders.py::test_reminder_preferences PASSED                [ 69%]
tests/test_reminders.py::test_invalid_hydration_target PASSED            [ 72%]
tests/test_reminders.py::test_active_reminders_triggering PASSED         [ 75%]
tests/test_reports.py::test_unauthenticated_reports_rejection PASSED     [ 77%]
tests/test_reports.py::test_csv_export_structure PASSED                  [ 80%]
tests/test_reports.py::test_pdf_export PASSED                            [ 83%]
tests/test_reports.py::test_report_user_isolation PASSED                 [ 86%]
tests/test_workout.py::test_create_and_get_workout PASSED                [ 88%]
tests/test_workout.py::test_create_workout_validation PASSED             [ 91%]
tests/test_workout.py::test_delete_workout PASSED                        [ 94%]
tests/test_workout.py::test_unauthorized_workout_access PASSED           [ 97%]
tests/test_workout.py::test_user_cascade_deletion PASSED                 [100%]

============================= 36 passed in 5.70s ==============================
```

---

## 9. Security & User Isolation

- **Password Hashing**: PBKDF2 with SHA-256 via Werkzeug.
- **Resource Ownership**: Every API endpoint strictly filters queries by `session['user_id']`. Attempting to read, update, delete, or export another user's resources returns `403 Forbidden`.
- **Session Security**: Session cookies configured with `HttpOnly` and `SameSite=Lax`.
- **SQL Injection Prevention**: 100% parameterized queries via SQLAlchemy ORM.

---

## 10. Limitations

- **Email/SMS Notifications**: As designed for the offline/local MVP architecture, reminders use browser notifications and in-app alerts without external SMTP/SMS services.
- **Wearable API Sync**: Direct Bluetooth or cloud sync with third-party wearables (e.g., Apple Health, Garmin) is not implemented.

---

## 11. License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
