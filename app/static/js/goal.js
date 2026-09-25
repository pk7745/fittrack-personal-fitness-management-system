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

    if (typeof loadGoalsPage === 'function' && document.getElementById('goals-page-list')) {
      loadGoalsPage();
    }
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

    if (typeof loadGoalsPage === 'function' && document.getElementById('goals-page-list')) {
      loadGoalsPage();
    }
    if (window.dashboard && window.dashboard.refresh) {
      window.dashboard.refresh();
    }
  } catch (err) {
    Toast.error(err.message || 'Failed to delete goal');
  }
}

let allPageGoals = [];
let currentGoalFilter = 'all';

async function loadGoalsPage() {
  const container = document.getElementById('goals-page-list');
  if (!container) return;

  try {
    const res = await apiRequest('/api/goals');
    if (!res || !res.success) return;

    allPageGoals = res.goals || [];

    // Summary counts
    const activeCount = allPageGoals.filter(g => g.status === 'Active' || (!g.status && !g.is_completed)).length;
    const completedCount = allPageGoals.filter(g => g.status === 'Completed' || g.is_completed).length;
    const overdueCount = allPageGoals.filter(g => g.status === 'Overdue').length;

    const totalEl = document.getElementById('goal-stat-total');
    const activeEl = document.getElementById('goal-stat-active');
    const compEl = document.getElementById('goal-stat-completed');
    const overEl = document.getElementById('goal-stat-overdue');

    if (totalEl) totalEl.innerText = allPageGoals.length;
    if (activeEl) activeEl.innerText = activeCount;
    if (compEl) compEl.innerText = completedCount;
    if (overEl) overEl.innerText = overdueCount;

    renderFilteredGoals();
  } catch (err) {
    console.error('Error loading goals page:', err);
    container.innerHTML = `<div class="empty-state"><p style="color:var(--danger)">Failed to load goals</p></div>`;
  }
}

function setGoalFilter(filter) {
  currentGoalFilter = filter;
  document.querySelectorAll('.goals-filter-btn').forEach(btn => {
    btn.classList.toggle('btn-primary', btn.dataset.filter === filter);
    btn.classList.toggle('btn-secondary', btn.dataset.filter !== filter);
  });
  renderFilteredGoals();
}

function getGoalStatusBadgeClass(status) {
  switch (status) {
    case 'Completed': return 'badge-normal';
    case 'Overdue': return 'badge-obese';
    default: return 'badge-underweight';
  }
}

function renderFilteredGoals() {
  const container = document.getElementById('goals-page-list');
  if (!container) return;

  let filtered = allPageGoals;
  if (currentGoalFilter === 'active') {
    filtered = allPageGoals.filter(g => g.status === 'Active' || (!g.status && !g.is_completed));
  } else if (currentGoalFilter === 'completed') {
    filtered = allPageGoals.filter(g => g.status === 'Completed' || g.is_completed);
  } else if (currentGoalFilter === 'overdue') {
    filtered = allPageGoals.filter(g => g.status === 'Overdue');
  }

  if (filtered.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="padding: 2.5rem 1rem;">
        <div class="empty-state-icon">🎯</div>
        <p>No goals found under this category.</p>
        <button class="btn btn-primary btn-sm" onclick="openGoalModal()">+ Create New Goal</button>
      </div>
    `;
    return;
  }

  container.innerHTML = filtered.map(g => {
    const isDone = g.is_completed;
    const pct = Math.min(100, Math.max(0, g.progress_percentage || 0));
    const status = g.status || (isDone ? 'Completed' : 'Active');

    let deadlineInfo = 'No deadline';
    if (g.deadline) {
      if (g.remaining_days !== null && g.remaining_days !== undefined) {
        if (g.remaining_days < 0) {
          deadlineInfo = `<span style="color:var(--danger); font-weight:600;">${Math.abs(g.remaining_days)}d overdue</span>`;
        } else if (g.remaining_days === 0) {
          deadlineInfo = `<span style="color:var(--accent-amber); font-weight:600;">Due today!</span>`;
        } else {
          deadlineInfo = `${g.remaining_days}d remaining (${g.deadline})`;
        }
      } else {
        deadlineInfo = g.deadline;
      }
    }

    return `
      <div class="card" style="padding: 1.25rem; margin-bottom: 1rem;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom: 0.75rem; flex-wrap:wrap; gap:0.5rem;">
          <div>
            <h3 style="font-size: 1.1rem; color:var(--text-main); display:inline-block; margin-right:0.5rem;">
              ${escapeHtml(g.goal_type)}
            </h3>
            <span class="badge ${getGoalStatusBadgeClass(status)}">${status}</span>
          </div>
          <div style="display:flex; align-items:center; gap:0.75rem;">
            <span class="badge ${isDone ? 'badge-normal' : 'badge-type'}" style="font-size:0.9rem; padding: 4px 8px;">
              ${pct.toFixed(0)}%
            </span>
            <button class="btn-icon" onclick="deleteGoal(${g.id})" title="Delete goal" aria-label="Delete goal">
              🗑
            </button>
          </div>
        </div>

        <div class="progress-container" style="height: 10px; margin-bottom: 1rem;">
          <div class="progress-bar ${isDone ? 'completed' : ''}" style="width: ${pct}%;"></div>
        </div>

        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 0.75rem; font-size: 0.85rem; color: var(--text-muted); background: var(--bg-surface); padding: 0.75rem; border-radius: var(--radius-sm); border: 1px solid var(--border-color);">
          <div>
            <span style="color:var(--text-subtle);">Target:</span>
            <strong style="color:var(--text-main); display:block;">${g.target_value}</strong>
          </div>
          <div>
            <span style="color:var(--text-subtle);">Current:</span>
            <strong style="color:var(--text-main); display:block;">${g.current_value}</strong>
          </div>
          <div>
            <span style="color:var(--text-subtle);">Baseline Start:</span>
            <strong style="color:var(--text-main); display:block;">${g.start_value !== null ? g.start_value : '--'}</strong>
          </div>
          <div>
            <span style="color:var(--text-subtle);">Deadline:</span>
            <span style="display:block;">${deadlineInfo}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');
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
  const form = document.getElementById('goal-form');
  if (form) form.addEventListener('submit', handleGoalSubmit);
  if (document.getElementById('goals-page-list')) {
    loadGoalsPage();
  }
});

window.openGoalModal = openGoalModal;
window.closeGoalModal = closeGoalModal;
window.deleteGoal = deleteGoal;
window.loadGoalsPage = loadGoalsPage;
window.setGoalFilter = setGoalFilter;

