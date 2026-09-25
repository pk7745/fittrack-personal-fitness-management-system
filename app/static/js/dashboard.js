/**
 * FitTrack v1.1 - Main Dashboard controller & Real-time update engine
 */
let weightChartInstance = null;
let activityChartInstance = null;

function getGreeting(name) {
  const hour = new Date().getHours();
  let timeStr = "Good evening";
  if (hour < 12) timeStr = "Good morning";
  else if (hour < 17) timeStr = "Good afternoon";

  return `${timeStr}, ${name || 'Athlete'} 👋`;
}

function getBmiBadgeClass(category) {
  if (!category) return 'badge-normal';
  const cat = category.toLowerCase();
  if (cat.includes('under')) return 'badge-underweight';
  if (cat.includes('over')) return 'badge-overweight';
  if (cat.includes('obese')) return 'badge-obese';
  return 'badge-normal';
}

function getGoalStatusBadgeClass(status) {
  switch (status) {
    case 'Completed': return 'badge-normal';
    case 'Overdue': return 'badge-obese';
    default: return 'badge-underweight';
  }
}

// -------------------------------------------------------------
// Real-Time Modular Refresh Handlers
// -------------------------------------------------------------
async function refreshStats() {
  try {
    const data = await apiRequest('/api/dashboard');
    if (!data.success) return;
    updateStatsDOM(data);
  } catch (err) {
    console.error('Error refreshing stats:', err);
  }
}

async function refreshWorkouts() {
  try {
    const data = await apiRequest('/api/workouts');
    if (!data.success) return;
    renderRecentWorkouts(data.workouts.slice(0, 5));
  } catch (err) {
    console.error('Error refreshing workouts:', err);
  }
}

async function refreshGoals() {
  try {
    const data = await apiRequest('/api/goals');
    if (!data.success) return;
    renderGoals(data.goals);
  } catch (err) {
    console.error('Error refreshing goals:', err);
  }
}

async function refreshCharts() {
  try {
    const data = await apiRequest('/api/dashboard');
    if (!data.success) return;
    renderWeightChart(data.charts.weight_history);
    renderActivityChart(data.charts.workout_activity);
  } catch (err) {
    console.error('Error refreshing charts:', err);
  }
}

async function refreshAnalytics() {
  if (typeof window.loadAnalytics === 'function') {
    await window.loadAnalytics();
  }
}

async function refreshReminders() {
  if (typeof window.loadReminders === 'function') {
    await window.loadReminders();
  }
}

async function refreshCalendar() {
  if (typeof window.loadCalendar === 'function') {
    await window.loadCalendar();
  }
}

async function refreshDashboard() {
  try {
    const data = await apiRequest('/api/dashboard');
    if (!data.success) return;

    const { user, fitness, workouts, recent_workouts, goals, charts } = data;

    // User greeting & Avatar
    const greetingEl = document.getElementById('user-greeting');
    if (greetingEl) greetingEl.innerText = getGreeting(user.name);

    const navNameEl = document.getElementById('nav-user-name');
    if (navNameEl) navNameEl.innerText = user.name;

    const navAvatarEl = document.getElementById('nav-user-avatar');
    if (navAvatarEl && user.name) {
      navAvatarEl.innerText = user.name.charAt(0).toUpperCase();
    }

    // Top Stat Cards
    updateStatsDOM(data);

    // Recent Workouts Table
    renderRecentWorkouts(recent_workouts);

    // Goals List
    renderGoals(goals);

    // Charts
    renderWeightChart(charts.weight_history);
    renderActivityChart(charts.workout_activity);

    // Parallel Refresh of v1.1 Enhancements
    await Promise.allSettled([
      refreshAnalytics(),
      refreshReminders(),
      refreshCalendar()
    ]);

  } catch (err) {
    console.error('Error refreshing dashboard:', err);
    Toast.error('Could not refresh dashboard data');
  }
}

function updateStatsDOM(data) {
  const { fitness, workouts } = data;

  // BMI Card
  const bmiValEl = document.getElementById('stat-bmi-value');
  const bmiBadgeEl = document.getElementById('stat-bmi-badge');
  if (bmiValEl) bmiValEl.innerText = fitness.bmi !== null ? fitness.bmi : '--';
  if (bmiBadgeEl) {
    bmiBadgeEl.className = `badge ${getBmiBadgeClass(fitness.bmi_category)}`;
    bmiBadgeEl.innerText = fitness.bmi_category || 'No Data';
  }

  // Weight Card
  const weightValEl = document.getElementById('stat-weight-value');
  if (weightValEl) weightValEl.innerText = fitness.weight !== null ? fitness.weight : '--';

  // Water Card
  const waterValEl = document.getElementById('stat-water-value');
  if (waterValEl) waterValEl.innerText = fitness.water !== null ? fitness.water : '0.0';

  // Calories Card
  const caloriesValEl = document.getElementById('stat-calories-value');
  if (caloriesValEl) {
    caloriesValEl.innerText = fitness.calories !== null ? fitness.calories.toLocaleString() : '0';
  }

  // Workouts Card
  const workoutTodayEl = document.getElementById('stat-workouts-today');
  const workoutWeeklyEl = document.getElementById('stat-workouts-weekly');
  if (workoutTodayEl) workoutTodayEl.innerText = workouts.today;
  if (workoutWeeklyEl) workoutWeeklyEl.innerText = `${workouts.weekly} this week`;
}

function renderRecentWorkouts(workouts) {
  const tbody = document.getElementById('workouts-table-body');
  if (!tbody) return;

  if (!workouts || workouts.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6">
          <div class="empty-state">
            <div class="empty-state-icon">🏃</div>
            <p>No workouts recorded yet. Start tracking your fitness journey!</p>
            <button class="btn btn-primary btn-sm" onclick="openWorkoutModal()">+ Log First Workout</button>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = workouts.map(w => `
    <tr>
      <td><strong>${escapeHtml(w.exercise_name)}</strong></td>
      <td><span class="badge badge-type">${escapeHtml(w.exercise_type)}</span></td>
      <td>${w.duration} mins</td>
      <td>${w.calories_burned} kcal</td>
      <td>${w.workout_date}</td>
      <td style="text-align: right;">
        <button class="btn-icon" onclick="deleteWorkout(${w.id})" title="Delete workout" aria-label="Delete workout">
          🗑
        </button>
      </td>
    </tr>
  `).join('');
}

function renderGoals(goals) {
  const container = document.getElementById('goals-container');
  if (!container) return;

  if (!goals || goals.length === 0) {
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🎯</div>
        <p>No active fitness goals. Challenge yourself with a new target!</p>
        <button class="btn btn-secondary btn-sm" onclick="openGoalModal()">+ Set a Goal</button>
      </div>
    `;
    return;
  }

  container.innerHTML = goals.map(g => {
    const isDone = g.is_completed;
    const pct = Math.min(100, Math.max(0, g.progress_percentage || 0));
    const status = g.status || (isDone ? 'Completed' : 'Active');

    let deadlineInfo = 'No deadline';
    if (g.deadline) {
      if (g.remaining_days !== null && g.remaining_days !== undefined) {
        if (g.remaining_days < 0) {
          deadlineInfo = `<span style="color:var(--danger);">${Math.abs(g.remaining_days)}d overdue</span>`;
        } else if (g.remaining_days === 0) {
          deadlineInfo = `<span style="color:var(--accent-amber);">Due today!</span>`;
        } else {
          deadlineInfo = `${g.remaining_days}d remaining`;
        }
      } else {
        deadlineInfo = g.deadline;
      }
    }

    return `
      <div class="goal-item">
        <div class="goal-header">
          <div>
            <span class="goal-title">${escapeHtml(g.goal_type)}</span>
            <span class="badge ${getGoalStatusBadgeClass(status)}" style="margin-left: 0.5rem;">${status}</span>
          </div>
          <div style="display:flex;align-items:center;gap:0.5rem;">
            <span class="badge ${isDone ? 'badge-normal' : 'badge-type'}">
              ${pct.toFixed(0)}%
            </span>
            <button class="btn-icon" onclick="deleteGoal(${g.id})" title="Remove goal" aria-label="Remove goal">
              &times;
            </button>
          </div>
        </div>
        <div class="progress-container">
          <div class="progress-bar ${isDone ? 'completed' : ''}" style="width: ${pct}%;"></div>
        </div>
        <div class="goal-meta" style="display:flex;justify-content:space-between;align-items:center;">
          <span>Current: <strong>${g.current_value}</strong> / Target: <strong>${g.target_value}</strong></span>
          <span>📅 ${deadlineInfo}</span>
        </div>
      </div>
    `;
  }).join('');
}

function renderWeightChart(weightHistory) {
  const canvas = document.getElementById('weightProgressChart');
  if (!canvas) return;

  if (weightChartInstance) {
    weightChartInstance.destroy();
  }

  const labels = weightHistory.labels || [];
  const data = weightHistory.weights || [];

  if (labels.length === 0) {
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    return;
  }

  weightChartInstance = new Chart(canvas, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Weight (kg)',
        data: data,
        borderColor: '#10b981',
        backgroundColor: 'rgba(16, 185, 129, 0.12)',
        borderWidth: 2.5,
        pointBackgroundColor: '#10b981',
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.35,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#1f2937',
          titleColor: '#f9fafb',
          bodyColor: '#10b981',
          borderColor: '#374151',
          borderWidth: 1,
          padding: 10,
          displayColors: false
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(55, 65, 81, 0.3)' },
          ticks: { color: '#9ca3af', font: { size: 11 } }
        },
        y: {
          grid: { color: 'rgba(55, 65, 81, 0.3)' },
          ticks: { color: '#9ca3af', font: { size: 11 } }
        }
      }
    }
  });
}

function renderActivityChart(activityData) {
  const canvas = document.getElementById('workoutActivityChart');
  if (!canvas) return;

  if (activityChartInstance) {
    activityChartInstance.destroy();
  }

  const labels = activityData.labels || [];
  const counts = activityData.counts || [];
  const calories = activityData.calories || [];

  activityChartInstance = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          type: 'bar',
          label: 'Workouts',
          data: counts,
          backgroundColor: 'rgba(59, 130, 246, 0.7)',
          borderRadius: 6,
          yAxisID: 'y'
        },
        {
          type: 'line',
          label: 'Calories Burned (kcal)',
          data: calories,
          borderColor: '#f59e0b',
          backgroundColor: 'transparent',
          borderWidth: 2,
          pointBackgroundColor: '#f59e0b',
          pointRadius: 4,
          tension: 0.3,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top',
          labels: { color: '#9ca3af', boxWidth: 12 }
        },
        tooltip: {
          backgroundColor: '#1f2937',
          titleColor: '#f9fafb',
          borderColor: '#374151',
          borderWidth: 1,
          padding: 10
        }
      },
      scales: {
        x: {
          grid: { color: 'rgba(55, 65, 81, 0.2)' },
          ticks: { color: '#9ca3af', font: { size: 11 } }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          beginAtZero: true,
          ticks: { stepSize: 1, color: '#3b82f6', font: { size: 11 } },
          grid: { color: 'rgba(55, 65, 81, 0.3)' }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          beginAtZero: true,
          grid: { drawOnChartArea: false },
          ticks: { color: '#f59e0b', font: { size: 11 } }
        }
      }
    }
  });
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>'"]/g, tag => ({
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    "'": '&#39;',
    '"': '&quot;'
  }[tag] || tag));
}

document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('workouts-table-body')) {
    refreshDashboard();
  }
});

window.dashboard = {
  refresh: refreshDashboard,
  refreshStats: refreshStats,
  refreshWorkouts: refreshWorkouts,
  refreshGoals: refreshGoals,
  refreshCharts: refreshCharts,
  refreshAnalytics: refreshAnalytics,
  refreshReminders: refreshReminders,
  refreshCalendar: refreshCalendar
};
