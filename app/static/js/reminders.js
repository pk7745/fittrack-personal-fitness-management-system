/**
 * FitTrack v1.1 - Smart Reminders Module
 */
async function loadReminders() {
  const container = document.getElementById('reminders-container');
  if (!container) return;

  try {
    const res = await apiRequest('/api/reminders/active');
    if (!res || !res.success) return;

    const reminders = res.reminders || [];
    if (reminders.length === 0) {
      container.style.display = 'none';
      container.innerHTML = '';
      return;
    }

    container.style.display = 'flex';
    container.innerHTML = reminders.map(r => `
      <div class="reminder-pill urgency-${r.urgency || 'normal'}">
        <span class="reminder-icon">${r.type === 'fitness' ? '📝' : r.type === 'workout' ? '🏃' : r.type === 'goal' ? '🎯' : '💧'}</span>
        <div class="reminder-body">
          <strong>${escapeHtml(r.title)}:</strong> ${escapeHtml(r.message)}
        </div>
      </div>
    `).join('');

    // Trigger Browser Notification if supported & permitted
    if (window.Notification && Notification.permission === 'granted' && reminders.length > 0) {
      const topRem = reminders[0];
      // Only notify if not already notified this session
      if (!sessionStorage.getItem(`notified_${topRem.id}`)) {
        new Notification(`FitTrack: ${topRem.title}`, {
          body: topRem.message,
          icon: '/static/favicon.ico'
        });
        sessionStorage.setItem(`notified_${topRem.id}`, '1');
      }
    }

  } catch (err) {
    console.error('Error checking reminders:', err);
  }
}

function requestBrowserNotifications() {
  if (!window.Notification) {
    Toast.info('Browser notifications are not supported on this browser.');
    return;
  }
  Notification.requestPermission().then(permission => {
    if (permission === 'granted') {
      Toast.success('Browser notifications enabled!');
      loadReminders();
    } else {
      Toast.info('Browser notifications not enabled. In-app reminders will continue to show.');
    }
  });
}

async function openRemindersModal() {
  const modal = document.getElementById('reminders-modal');
  if (!modal) return;

  try {
    const res = await apiRequest('/api/reminders/preferences');
    const p = res.preferences;

    document.getElementById('pref_daily_fitness').checked = p.daily_fitness_reminder;
    document.getElementById('pref_workout').checked = p.workout_reminder;
    document.getElementById('pref_goal_deadline').checked = p.goal_deadline_reminder;
    document.getElementById('pref_hydration').checked = p.hydration_reminder;
    document.getElementById('pref_hydration_target').value = p.hydration_target || 2.0;

    modal.classList.add('active');
  } catch (err) {
    Toast.error('Failed to load reminder settings');
  }
}

function closeRemindersModal() {
  const modal = document.getElementById('reminders-modal');
  if (modal) modal.classList.remove('active');
}

async function handleRemindersSubmit(e) {
  e.preventDefault();
  const submitBtn = e.target.querySelector('button[type="submit"]');

  const daily_fitness = document.getElementById('pref_daily_fitness').checked;
  const workout = document.getElementById('pref_workout').checked;
  const goal_deadline = document.getElementById('pref_goal_deadline').checked;
  const hydration = document.getElementById('pref_hydration').checked;
  const hydration_target = parseFloat(document.getElementById('pref_hydration_target').value || 2.0);

  submitBtn.disabled = true;
  submitBtn.innerText = 'Saving...';

  try {
    await apiRequest('/api/reminders/preferences', {
      method: 'PUT',
      body: JSON.stringify({
        daily_fitness_reminder: daily_fitness,
        workout_reminder: workout,
        goal_deadline_reminder: goal_deadline,
        hydration_reminder: hydration,
        hydration_target: hydration_target
      })
    });

    Toast.success('Reminder settings updated!');
    closeRemindersModal();
    loadReminders();
  } catch (err) {
    Toast.error(err.message || 'Failed to update reminder settings');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = 'Save Settings';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('reminders-form');
  if (form) form.addEventListener('submit', handleRemindersSubmit);
});

window.loadReminders = loadReminders;
window.openRemindersModal = openRemindersModal;
window.closeRemindersModal = closeRemindersModal;
window.requestBrowserNotifications = requestBrowserNotifications;
