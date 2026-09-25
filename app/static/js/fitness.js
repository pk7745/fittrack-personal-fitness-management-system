/**
 * Daily fitness metrics logging (Weight, Water, Calories)
 */
function openFitnessModal() {
  const modal = document.getElementById('fitness-modal');
  const form = document.getElementById('fitness-form');
  if (modal && form) {
    form.reset();
    const dateInput = document.getElementById('metric_date');
    if (dateInput) {
      dateInput.value = new Date().toISOString().split('T')[0];
    }
    modal.classList.add('active');
  }
}

function closeFitnessModal() {
  const modal = document.getElementById('fitness-modal');
  if (modal) modal.classList.remove('active');
}

async function handleFitnessSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');

  const weightVal = document.getElementById('metric_weight').value;
  const waterVal = document.getElementById('metric_water').value;
  const caloriesVal = document.getElementById('metric_calories').value;
  const dateVal = document.getElementById('metric_date').value;

  const payload = { record_date: dateVal };
  if (weightVal !== "") payload.weight = parseFloat(weightVal);
  if (waterVal !== "") payload.water_intake = parseFloat(waterVal);
  if (caloriesVal !== "") payload.calories_consumed = parseInt(caloriesVal, 10);

  if (payload.weight === undefined && payload.water_intake === undefined && payload.calories_consumed === undefined) {
    Toast.error('Please enter at least one metric to log');
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerText = 'Saving...';

  try {
    const res = await apiRequest('/api/fitness', {
      method: 'POST',
      body: JSON.stringify(payload)
    });

    Toast.success('Daily metrics saved successfully!');
    closeFitnessModal();
    if (typeof window.loadProgressPage === 'function') {
      window.loadProgressPage();
    }
    if (window.dashboard && window.dashboard.refresh) {
      window.dashboard.refresh();
    }
  } catch (err) {
    Toast.error(err.message || 'Failed to save fitness metrics');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = 'Save Metrics';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('fitness-form');
  if (form) form.addEventListener('submit', handleFitnessSubmit);
});

window.openFitnessModal = openFitnessModal;
window.closeFitnessModal = closeFitnessModal;
