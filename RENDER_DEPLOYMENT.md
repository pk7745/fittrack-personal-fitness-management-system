# FitTrack — Render Web Service Deployment Guide

This guide describes how to deploy the FitTrack application to **Render Free Web Service** using your GitHub repository.

---

## 1. Push Latest Code to GitHub
Ensure all production-ready changes are committed and pushed to your `master` branch:
```bash
git push origin master
```

---

## 2. Open Render Dashboard
1. Log in to [https://dashboard.render.com/](https://dashboard.render.com/).
2. Click **New +** in the top navigation bar.
3. Select **Web Service**.

---

## 3. Connect the GitHub Repository
1. Choose **Build and deploy from a Git repository**.
2. Connect your GitHub account if prompted.
3. Search for and select:
   `pk7745/fittrack-personal-fitness-management-system`

---

## 4. Configure Web Service Settings

Configure the following fields in the Render dashboard:

| Setting | Value |
|---|---|
| **Name** | `fittrack-personal-fitness-management-system` (or your preferred name) |
| **Region** | Choose the region closest to you (e.g., *Singapore*, *Oregon*, *Frankfurt*) |
| **Branch** | `master` |
| **Root Directory** | *(Leave blank — root of repository)* |
| **Runtime** | `Python` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn --bind 0.0.0.0:$PORT run:app` |
| **Instance Type** | `Free` |

*(Note: Alternatively, if deploying using Render Blueprints, Render will automatically read `render.yaml` from the repository root).*

---

## 5. Configure Environment Variables
Under the **Environment Variables** section on Render, add:

| Key | Value | Notes |
|---|---|---|
| `FLASK_CONFIG` | `production` | Ensures `DEBUG = False` |
| `SECRET_KEY` | *(Click "Generate" or paste a random 64-char string)* | Cryptographic session encryption key |
| `PYTHON_VERSION` | `3.11.9` | Recommended stable Python runtime on Render |

---

## 6. Deploy & Monitor Build Logs
1. Click **Create Web Service**.
2. Render will initiate the build:
   - Clones repository.
   - Installs dependencies from `requirements.txt` (Flask, SQLAlchemy, Werkzeug, ReportLab, Gunicorn).
   - Starts the application using Gunicorn on the dynamically assigned `$PORT`.
3. Check the **Logs** tab. A successful startup will display:
   ```text
   [INFO] Starting gunicorn ...
   [INFO] Listening at: http://0.0.0.0:10000
   ```

---

## 7. Open Live URL & Run Smoke Tests
Once Render shows the service as **Live**, open your public URL (e.g. `https://fittrack-personal-fitness-management-system.onrender.com`):

1. **Authentication**: Register a new account (`/register`) and log in (`/login`).
2. **Dashboard**: Verify the 5 summary cards and greeting load (`/dashboard`).
3. **Workouts**: Log a workout session and verify it appears in the table (`/workouts`).
4. **Progress & Analytics**: Verify weight trajectory cards and Chart.js graphs (`/progress`).
5. **Goals**: Create a goal with a deadline and verify progress calculation (`/goals`).
6. **Calendar**: Navigate through the monthly workout calendar (`/calendar`).
7. **Reports**: Download a Workouts CSV and a formatted PDF report (`/reports`).
8. **Profile**: Update biometric data and confirm live BMI recalculation (`/profile`).

---

## Important SQLite Note for Free Tier
- **Ephemeral Storage**: Render free-tier web services use ephemeral container filesystems. The SQLite database in `instance/fittrack.db` persists while the instance is running, but spins down after 15 minutes of inactivity and resets if the container is redeployed.
- **Persistent Data**: For permanent, production-grade data storage that survives redeployments and container restarts, attach a PostgreSQL database (e.g., Render Postgres or Supabase) and supply `DATABASE_URL`.
