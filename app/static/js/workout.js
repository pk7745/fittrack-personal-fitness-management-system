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
    if (window.dashboard && window.dashboard.refresh) {
      window.dashboard.refresh();
    }
  } catch (err) {
    Toast.error(err.message || 'Failed to delete workout');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('workout-form');
  if (form) form.addEventListener('submit', handleWorkoutSubmit);
});

window.openWorkoutModal = openWorkoutModal;
window.closeWorkoutModal = closeWorkoutModal;
window.deleteWorkout = deleteWorkout;
