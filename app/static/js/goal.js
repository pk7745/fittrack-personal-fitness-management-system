/**
 * Fitness Goals management (FitTrack v1.1)
 */
function openGoalModal() {
  const modal = document.getElementById('goal-modal');
  const form = document.getElementById('goal-form');
  if (modal && form) {
    form.reset();
    modal.classList.add('active');
  }
}

function closeGoalModal() {
  const modal = document.getElementById('goal-modal');
  if (modal) modal.classList.remove('active');
}

async function handleGoalSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');

  const goalType = document.getElementById('goal_type').value;
  const targetVal = parseFloat(document.getElementById('target_value').value);
  const currentVal = parseFloat(document.getElementById('current_value').value || 0);
  const startVal = document.getElementById('start_value').value;
  const deadlineVal = document.getElementById('goal_deadline').value;

  if (!goalType) {
    Toast.error('Please select a goal type');
    return;
  }
  if (isNaN(targetVal) || targetVal <= 0) {
    Toast.error('Target value must be greater than 0');
    return;
  }

  const payload = {
    goal_type: goalType,
    target_value: targetVal,
    current_value: currentVal
  };

  if (startVal !== "") {
    payload.start_value = parseFloat(startVal);
  }
  if (deadlineVal) {
    payload.deadline = deadlineVal;
  }

  submitBtn.disabled = true;
  submitBtn.innerText = 'Saving...';

  try {
    await apiRequest('/api/goals', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    Toast.success('Goal created successfully!');
    closeGoalModal();
    if (window.dashboard && window.dashboard.refresh) {
      window.dashboard.refresh();
    }
  } catch (err) {
    Toast.error(err.message || 'Failed to create goal');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = 'Save Goal';
  }
}

async function deleteGoal(goalId) {
  if (!confirm('Are you sure you want to remove this goal?')) {
    return;
  }

  try {
    await apiRequest(`/api/goals/${goalId}`, { method: 'DELETE' });
    Toast.success('Goal removed');
    if (window.dashboard && window.dashboard.refresh) {
      window.dashboard.refresh();
    }
  } catch (err) {
    Toast.error(err.message || 'Failed to delete goal');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('goal-form');
  if (form) form.addEventListener('submit', handleGoalSubmit);
});

window.openGoalModal = openGoalModal;
window.closeGoalModal = closeGoalModal;
window.deleteGoal = deleteGoal;
