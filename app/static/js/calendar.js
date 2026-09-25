/**
 * FitTrack v1.1 - Lightweight Workout Calendar Module
 */
let currentCalYear = new Date().getFullYear();
let currentCalMonth = new Date().getMonth() + 1;
let currentMonthEvents = {};

async function loadCalendar(year = currentCalYear, month = currentCalMonth) {
  const container = document.getElementById('calendar-grid');
  const titleEl = document.getElementById('calendar-month-title');
  if (!container) return;

  currentCalYear = year;
  currentCalMonth = month;

  try {
    const res = await apiRequest(`/api/calendar/month?year=${year}&month=${month}`);
    if (!res || !res.success) return;

    const { month_name, events } = res.calendar;
    currentMonthEvents = events;

    if (titleEl) {
      titleEl.innerText = `${month_name} ${year}`;
    }

    renderCalendarGrid(year, month, events);
  } catch (err) {
    console.error('Error loading calendar:', err);
  }
}

function renderCalendarGrid(year, month, events) {
  const grid = document.getElementById('calendar-grid');
  if (!grid) return;

  grid.innerHTML = '';

  // Day of week headers
  const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  dayNames.forEach(d => {
    const headerCell = document.createElement('div');
    headerCell.className = 'calendar-day-header';
    headerCell.innerText = d;
    grid.appendChild(headerCell);
  });

  // Calculate starting day of the week
  const firstDayIndex = new Date(year, month - 1, 1).getDay();
  const totalDays = new Date(year, month, 0).getDate();

  // Blank padding cells for days before the 1st
  for (let i = 0; i < firstDayIndex; i++) {
    const blank = document.createElement('div');
    blank.className = 'calendar-cell empty';
    grid.appendChild(blank);
  }

  const todayStr = new Date().toISOString().split('T')[0];

  // Render each day cell
  for (let day = 1; day <= totalDays; day++) {
    const dStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    const dayEvent = events[dStr] || { has_workout: false, workout_count: 0, fitness_record: null, goal_deadlines: [] };

    const cell = document.createElement('div');
    cell.className = 'calendar-cell';
    if (dStr === todayStr) cell.classList.add('today');
    if (dayEvent.has_workout) cell.classList.add('has-workout');

    let indicators = '';
    if (dayEvent.has_workout) {
      indicators += `<span class="cal-dot cal-dot-workout" title="${dayEvent.workout_count} workout(s)"></span>`;
    }
    if (dayEvent.fitness_record) {
      indicators += `<span class="cal-dot cal-dot-metrics" title="Daily metrics logged"></span>`;
    }
    if (dayEvent.goal_deadlines && dayEvent.goal_deadlines.length > 0) {
      indicators += `<span class="cal-dot cal-dot-goal" title="Goal deadline"></span>`;
    }

    cell.innerHTML = `
      <div class="cal-day-num">${day}</div>
      <div class="cal-indicators">${indicators}</div>
    `;

    cell.addEventListener('click', () => showDateDetails(dStr, dayEvent));
    grid.appendChild(cell);
  }
}

function showDateDetails(dateStr, dayEvent) {
  const panel = document.getElementById('calendar-detail-panel');
  if (!panel) return;

  const dateObj = new Date(dateStr + 'T00:00:00');
  const formatted = dateObj.toLocaleDateString('en-US', { weekday: 'long', month: 'short', day: 'numeric', year: 'numeric' });

  let content = `<h4>${formatted}</h4>`;

  // Workouts
  if (dayEvent.workouts && dayEvent.workouts.length > 0) {
    content += `<div class="cal-detail-section"><strong>🏃 Workouts (${dayEvent.workouts.length}):</strong>`;
    dayEvent.workouts.forEach(w => {
      content += `
        <div class="cal-detail-item">
          <span><strong>${escapeHtml(w.exercise_name)}</strong> (${escapeHtml(w.exercise_type)})</span>
          <span>${w.duration}m &bull; ${w.calories_burned} kcal</span>
        </div>
      `;
    });
    content += `</div>`;
  } else {
    content += `<p class="cal-no-events">No workout recorded</p>`;
  }

  // Daily Metrics
  if (dayEvent.fitness_record) {
    const f = dayEvent.fitness_record;
    content += `
      <div class="cal-detail-section">
        <strong>📝 Daily Health Metrics:</strong>
        <div class="cal-detail-item">
          <span>Weight: ${f.weight !== null ? `${f.weight} kg` : '--'}</span>
          <span>Water: ${f.water_intake !== null ? `${f.water_intake} L` : '--'}</span>
          <span>Calories: ${f.calories_consumed !== null ? `${f.calories_consumed} kcal` : '--'}</span>
        </div>
      </div>
    `;
  }

  // Goal Deadlines
  if (dayEvent.goal_deadlines && dayEvent.goal_deadlines.length > 0) {
    content += `<div class="cal-detail-section"><strong>🎯 Goal Deadlines:</strong>`;
    dayEvent.goal_deadlines.forEach(g => {
      content += `
        <div class="cal-detail-item">
          <span>${escapeHtml(g.goal_type)}</span>
          <span class="badge ${g.status === 'Completed' ? 'badge-normal' : g.status === 'Overdue' ? 'badge-obese' : 'badge-underweight'}">${g.status}</span>
        </div>
      `;
    });
    content += `</div>`;
  }

  panel.innerHTML = content;
}

function prevMonth() {
  if (currentCalMonth === 1) {
    currentCalMonth = 12;
    currentCalYear -= 1;
  } else {
    currentCalMonth -= 1;
  }
  loadCalendar(currentCalYear, currentCalMonth);
}

function nextMonth() {
  if (currentCalMonth === 12) {
    currentCalMonth = 1;
    currentCalYear += 1;
  } else {
    currentCalMonth += 1;
  }
  loadCalendar(currentCalYear, currentCalMonth);
}

window.loadCalendar = loadCalendar;
window.prevMonth = prevMonth;
window.nextMonth = nextMonth;
