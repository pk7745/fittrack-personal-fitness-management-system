/**
 * Workout tracking and CRUD management
 */
function openWorkoutModal() {
  const modal = document.getElementById('workout-modal');
  const form = document.getElementById('workout-form');
  if (modal && form) {
    form.reset();
    const dateInput = document.getElementById('workout_date');
    if (dateInput) {
      dateInput.value = new Date().toISOString().split('T')[0];
    }
    modal.classList.add('active');
  }
}

function closeWorkoutModal() {
  const modal = document.getElementById('workout-modal');
  if (modal) modal.classList.remove('active');
}

async function handleWorkoutSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');

  const name = document.getElementById('exercise_name').value.trim();
  const type = document.getElementById('exercise_type').value;
  const duration = parseInt(document.getElementById('duration').value, 10);
  const calories = parseFloat(document.getElementById('calories_burned').value || 0);
  const date = document.getElementById('workout_date').value;

  if (!name) {
    Toast.error('Please enter the exercise name');
    return;
  }
  if (!type) {
    Toast.error('Please select an exercise type');
    return;
  }
  if (!duration || duration <= 0) {
    Toast.error('Duration must be greater than 0 minutes');
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerText = 'Saving...';

  try {
    await apiRequest('/api/workouts', {
      method: 'POST',
      body: JSON.stringify({
        exercise_name: name,
        exercise_type: type,
        duration: duration,
        calories_burned: calories,
        workout_date: date
      })
    });

    Toast.success('Workout logged successfully!');
    closeWorkoutModal();

    // Real-time update for /workouts page
    if (typeof loadWorkoutsPage === 'function' && document.getElementById('page-workouts-tbody')) {
      loadWorkoutsPage();
    }
    // Real-time update for /dashboard page
    if (window.dashboard && window.dashboard.refresh) {
      window.dashboard.refresh();
    }
  } catch (err) {
    Toast.error(err.message || 'Failed to log workout');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = 'Save Workout';
  }
}

async function deleteWorkout(workoutId) {
  if (!confirm('Are you sure you want to delete this workout record?')) {
    return;
  }

  try {
    await apiRequest(`/api/workouts/${workoutId}`, {
      method: 'DELETE'
    });
    Toast.success('Workout deleted successfully');

    // Real-time update for /workouts page
    if (typeof loadWorkoutsPage === 'function' && document.getElementById('page-workouts-tbody')) {
      loadWorkoutsPage();
    }
    // Real-time update for /dashboard page
    if (window.dashboard && window.dashboard.refresh) {
      window.dashboard.refresh();
    }
  } catch (err) {
    Toast.error(err.message || 'Failed to delete workout');
  }
}

async function loadWorkoutsPage() {
  const tbody = document.getElementById('page-workouts-tbody');
  if (!tbody) return;

  try {
    const [workoutsRes, dashRes] = await Promise.all([
      apiRequest('/api/workouts'),
      apiRequest('/api/dashboard')
    ]);

    if (dashRes && dashRes.success) {
      const stats = dashRes.workouts || {};
      const totalEl = document.getElementById('workout-stat-total');
      const weekEl = document.getElementById('workout-stat-week');
      const calTodayEl = document.getElementById('workout-stat-calories-today');
      const calWeekEl = document.getElementById('workout-stat-calories-week');

      if (totalEl) totalEl.innerText = workoutsRes.count !== undefined ? workoutsRes.count : (workoutsRes.workouts ? workoutsRes.workouts.length : 0);
      if (weekEl) weekEl.innerText = stats.weekly !== undefined ? stats.weekly : 0;
      if (calTodayEl) calTodayEl.innerText = (stats.today_calories || 0).toLocaleString();
      if (calWeekEl) calWeekEl.innerText = (stats.weekly_calories || 0).toLocaleString();
    }

    const badge = document.getElementById('workout-count-badge');
    const workouts = workoutsRes.workouts || [];
    if (badge) badge.innerText = `${workouts.length} session${workouts.length === 1 ? '' : 's'}`;

    if (workouts.length === 0) {
      tbody.innerHTML = `
        <tr>
          <td colspan="6">
            <div class="empty-state">
              <div class="empty-state-icon">🏋️</div>
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

  } catch (err) {
    console.error('Error loading workouts page:', err);
    tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--danger);padding:1.5rem;">Failed to load workout history</td></tr>`;
  }
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
  const form = document.getElementById('workout-form');
  if (form) form.addEventListener('submit', handleWorkoutSubmit);
  if (document.getElementById('page-workouts-tbody')) {
    loadWorkoutsPage();
  }
});

window.openWorkoutModal = openWorkoutModal;
window.closeWorkoutModal = closeWorkoutModal;
window.deleteWorkout = deleteWorkout;
window.loadWorkoutsPage = loadWorkoutsPage;

