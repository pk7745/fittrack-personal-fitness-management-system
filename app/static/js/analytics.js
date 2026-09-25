/**
 * FitTrack v1.1 - Advanced Analytics Module
 */
async function loadAnalytics() {
  const container = document.getElementById('analytics-section');
  if (!container) return;

  try {
    const data = await apiRequest('/api/analytics/summary');
    if (!data || !data.success) return;

    const { weight_analytics, workout_analytics, fitness_analytics } = data;

    // 1. Weight Analytics
    const curW = document.getElementById('analytics-current-weight');
    const startW = document.getElementById('analytics-start-weight');
    const prevW = document.getElementById('analytics-prev-change');
    const totW = document.getElementById('analytics-total-change');
    const trend7 = document.getElementById('analytics-trend-7d');
    const trend30 = document.getElementById('analytics-trend-30d');

    if (curW) curW.innerText = weight_analytics.current_weight !== null ? `${weight_analytics.current_weight} kg` : '--';
    if (startW) startW.innerText = weight_analytics.starting_weight !== null ? `${weight_analytics.starting_weight} kg` : '--';
    if (prevW) {
      const pc = weight_analytics.change_from_previous;
      prevW.innerText = pc !== null ? `${pc > 0 ? '+' : ''}${pc} kg` : '--';
    }
    if (totW) {
      const tc = weight_analytics.total_change;
      totW.innerText = tc !== null ? `${tc > 0 ? '+' : ''}${tc} kg` : '--';
    }
    if (trend7) trend7.innerText = weight_analytics.trend_7d;
    if (trend30) trend30.innerText = weight_analytics.trend_30d;

    // 2. Workout Analytics
    const totWorkouts = document.getElementById('analytics-total-workouts');
    const weekWorkouts = document.getElementById('analytics-workouts-week');
    const monthWorkouts = document.getElementById('analytics-workouts-month');
    const avgWorkouts = document.getElementById('analytics-avg-workouts');
    const totDuration = document.getElementById('analytics-total-duration');
    const activityRate = document.getElementById('analytics-activity-rate');
    const activityBar = document.getElementById('analytics-activity-bar');

    if (totWorkouts) totWorkouts.innerText = workout_analytics.total_workouts;
    if (weekWorkouts) weekWorkouts.innerText = workout_analytics.workouts_this_week;
    if (monthWorkouts) monthWorkouts.innerText = workout_analytics.workouts_this_month;
    if (avgWorkouts) avgWorkouts.innerText = `${workout_analytics.avg_workouts_per_week} / wk`;
    if (totDuration) totDuration.innerText = `${workout_analytics.total_duration_minutes} mins`;
    if (activityRate) activityRate.innerText = `${workout_analytics.activity_rate_30d}%`;
    if (activityBar) activityBar.style.width = `${Math.min(100, workout_analytics.activity_rate_30d)}%`;

    // 3. Fitness & Nutrition Analytics
    const avgWater = document.getElementById('analytics-avg-water');
    const avgCalConsumed = document.getElementById('analytics-avg-cal-consumed');
    const avgCalBurned = document.getElementById('analytics-avg-cal-burned');

    if (avgWater) avgWater.innerText = `${fitness_analytics.average_water_intake} L`;
    if (avgCalConsumed) avgCalConsumed.innerText = `${fitness_analytics.average_calories_consumed.toLocaleString()} kcal`;
    if (avgCalBurned) avgCalBurned.innerText = `${fitness_analytics.average_calories_burned} kcal`;

  } catch (err) {
    console.error('Error loading analytics:', err);
  }
}

window.loadAnalytics = loadAnalytics;
