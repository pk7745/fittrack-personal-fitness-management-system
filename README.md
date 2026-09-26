# FitTrack — Personal Fitness Management System

A production-grade, full-stack personal fitness tracking web application built with Python, Flask, SQLAlchemy, SQLite, HTML5, modern CSS3, and Vanilla JavaScript.

FitTrack provides individuals with an intuitive, responsive, and data-driven platform to monitor daily health and fitness metrics. Built with a clean layered architecture, FitTrack demonstrates clean monolithic web development principles, robust session authentication, complete CRUD operations, automated BMI calculation, interactive Chart.js analytics, smart reminder preferences, multi-format CSV/PDF reporting, interactive calendar tracking, and strict user-data authorization boundaries.

---

## Features

- **User Authentication**: Secure registration, login, and session persistence using Werkzeug password hashing.
- **Secure User Isolation**: Multi-tenant authorization checks ensuring User A cannot read, modify, or delete User B's workouts, goals, or records.
- **Personal Fitness Profile**: Maintain biometrics including height, weight, age, gender, and primary fitness goal.
- **BMI Calculation**: Automated BMI score calculation (\(\text{weight} / \text{height}^2\)) with World Health Organization categorization (Underweight, Normal, Overweight, Obese).
- **Workout Tracking**: Log workout sessions with exercise type (Strength, Cardio, Running, Cycling, Walking, Yoga, Other), duration, calories burned, and date.
- **Fitness Metrics**: Daily health logging for body weight, hydration water intake (L), and caloric consumption (kcal).
- **Goal Tracking**: Set and manage fitness goals with target values and current values.
- **Goal Deadlines**: Target completion dates, baseline initial values, dynamic status lifecycle (`Active`, `Completed`, `Overdue`), and countdown remaining days.
- **Progress Analytics**: Advanced trend calculations including 7-day and 30-day weight trajectory, change from previous record, and total recorded change.
- **7-Day / 30-Day Trends**: 30-day workout consistency scoring (`(active_days / 30) * 100`) and 7-day nutritional intake averages.
- **Smart Reminders**: User-configurable in-app alerts and browser notifications for daily check-ins, workouts, goal deadlines, and hydration tracking.
- **Interactive Calendar**: Monthly workout calendar visualizing training days, health check-in entries, and approaching goal deadlines with click-to-view date inspection.
- **CSV Reports**: On-demand CSV data streaming for Workouts, Daily Fitness Records, Goals, and Aggregated Summary metrics.
- **PDF Reports**: Comprehensive, publication-quality multi-page PDF generation built with ReportLab featuring user biometrics, metric summaries, and workout history tables.
- **Responsive Multi-Page UI**: Clean desktop sidebar navigation with active page indicators, collapsible mobile hamburger drawer, and fluid responsive card grids.
- **Real-Time In-Page Updates**: Asynchronous DOM and Chart.js updates on all CRUD actions without full page reloads.

---

## Tech Stack

- **Python**: Primary programming language (v3.10+)
- **Flask**: Lightweight WSGI web application framework
- **SQLAlchemy**: Object-relational mapping (ORM) with SQLite foreign keys and cascade deletion
- **SQLite**: Embedded relational database
- **HTML5**: Semantic document structure
- **CSS3**: Custom modern dark-theme SaaS design system with CSS grid and flexbox
- **JavaScript**: Modular vanilla JavaScript (ES6+, async/await)
- **Fetch API**: Asynchronous client-server communication
- **Chart.js**: Client-side interactive data visualizations via CDN
- **ReportLab**: Server-side PDF document generation engine
- **pytest**: Automated testing framework *(The application was validated with an automated pytest suite during development)*

---

## Architecture

FitTrack implements a clean, layered architecture with strict separation of concerns:

```text
Frontend (HTML5 / CSS3 / Vanilla JS / Chart.js)
                      ↓ (Fetch API)
Flask Routes & Blueprints (Page Views & REST APIs)
                      ↓
Service Layer (fitness, workout, analytics, reminders, report, calendar)
                      ↓
SQLAlchemy ORM (User, Workout, FitnessRecord, Goal, ReminderPreference)
                      ↓
SQLite Database (instance/fittrack.db)
```

---

## Application Pages

FitTrack is organized into dedicated, focused views:

- **/dashboard**: Daily performance overview, quick statistic cards, active reminders, compact goal status, recent workouts, and quick-action shortcuts.
- **/workouts**: Detailed exercise logging, lifetime workout statistics, weekly duration, calories burned, and full interactive workout history.
- **/progress**: Advanced biometric analytics, 7-day and 30-day weight trends, 30-day workout consistency rates, nutrition averages, and Chart.js visualizations.
- **/goals**: Complete fitness goal management with filterable tabs (All, Active, Completed, Overdue), baseline starting values, and deadline tracking.
- **/calendar**: Monthly interactive calendar displaying daily workout badges, health check-ins, and goal deadlines with a date detail inspector.
- **/reports**: Dedicated data export center supporting instant downloads of Workouts CSV, Fitness CSV, Goals CSV, Summary CSV, and ReportLab PDF.
- **/profile**: Biometric profile editing with live BMI calculation preview, plus configurable Smart Reminder Preferences and push notification controls.

---

## REST API Endpoints

### Authentication
- `POST /api/auth/register` — Create a new user account
- `POST /api/auth/login` — Authenticate user and initialize session
- `POST /api/auth/logout` — Terminate current session
- `GET /api/auth/me` — Fetch current user details

### Dashboard & Analytics
- `GET /api/dashboard` — Aggregated biometric stats, recent workouts, and chart datasets
- `GET /api/analytics/summary` — Advanced 7d/30d weight trends, consistency rate, and nutrition averages

### Workouts & Calendar
- `GET /api/workouts` — Retrieve all workouts for authenticated user
- `POST /api/workouts` — Log a new workout session
- `GET /api/workouts/<id>` — Retrieve single workout details
- `DELETE /api/workouts/<id>` — Delete workout session (ownership enforced)
- `GET /api/calendar/month` — Retrieve monthly calendar events

### Fitness Metrics
- `GET /api/fitness` — Retrieve historical daily fitness records
- `POST /api/fitness` — Save or update weight, water intake, and calories
- `DELETE /api/fitness/<id>` — Delete fitness record (ownership enforced)

### Goals
- `GET /api/goals` — Retrieve all goals with status and deadline countdown
- `POST /api/goals` — Create a new goal with baseline start value and deadline
- `GET /api/goals/<id>` — Retrieve single goal details
- `PUT /api/goals/<id>` — Update goal values and deadline
- `DELETE /api/goals/<id>` — Remove fitness goal

### Reminders
- `GET /api/reminders/preferences` — Retrieve reminder settings
- `PUT /api/reminders/preferences` — Update reminder settings
- `GET /api/reminders/active` — Evaluate and return pending alerts

### Reports & Exports
- `GET /api/reports/workouts.csv` — Export workouts in CSV format
- `GET /api/reports/fitness.csv` — Export daily fitness metrics in CSV format
- `GET /api/reports/goals.csv` — Export fitness goals in CSV format
- `GET /api/reports/summary.csv` — Export consolidated summary metrics in CSV format
- `GET /api/reports/fitness.pdf` — Export styled biometric and workout summary in PDF format

---

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/pk7745/fittrack-personal-fitness-management-system.git
cd fittrack-personal-fitness-management-system
```

### 2. Create and Activate Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy the sample environment file:
```bash
cp .env.example .env
```

*(On Windows PowerShell, use `Copy-Item .env.example .env`)*

Review `.env` and configure a secret key for production use.

### 5. Run the Application
```bash
python run.py
```

The application will start at `http://127.0.0.1:5000/`.

---

## Deployment (Render Web Service)

FitTrack is pre-configured for deployment on **Render Free Web Service**.

### Configuration Settings
- **Build Command**: pip install -r requirements.txt
- **Start Command**: gunicorn --bind 0.0.0.0: run:app
- **Environment Variables**:
  - FLASK_CONFIG: production (enforces DEBUG = False)
  - SECRET_KEY: *(Set to a secure, random 64-character secret)*
  - PYTHON_VERSION: 3.11.9

### SQLite Free Tier Limitation
The initial deployment uses SQLite (instance/fittrack.db), which automatically initializes upon startup. Please note that Render's free tier uses an ephemeral filesystem: data will persist across regular user sessions while the service is active, but resets if the free container spins down or is redeployed. For permanent data persistence across restarts and redeployments, connect a persistent PostgreSQL database via the DATABASE_URL environment variable.

For step-by-step instructions, refer to [RENDER_DEPLOYMENT.md](RENDER_DEPLOYMENT.md).

---

## Demo Credentials
For testing and evaluation, a pre-seeded account is available upon first launch:
- **Email**: `demo@fittrack.com`
- **Password**: `Password123!`

---

## License
This project is licensed under the MIT License.
