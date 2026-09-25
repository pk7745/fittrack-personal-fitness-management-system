/**
 * User Profile view & edit modal with live BMI calculation
 */
async function openProfileModal() {
  const modal = document.getElementById('profile-modal');
  if (!modal) return;

  try {
    const res = await apiRequest('/api/profile');
    const u = res.user;

    document.getElementById('profile_name').value = u.name || '';
    document.getElementById('profile_age').value = u.age || '';
    document.getElementById('profile_gender').value = u.gender || '';
    document.getElementById('profile_height').value = u.height || '';
    document.getElementById('profile_weight').value = u.weight || '';
    document.getElementById('profile_fitness_goal').value = u.fitness_goal || '';

    updateLiveBmiPreview();
    modal.classList.add('active');
  } catch (err) {
    Toast.error('Failed to load profile data');
  }
}

function closeProfileModal() {
  const modal = document.getElementById('profile-modal');
  if (modal) modal.classList.remove('active');
}

function updateLiveBmiPreview() {
  const h = parseFloat(document.getElementById('profile_height').value);
  const w = parseFloat(document.getElementById('profile_weight').value);
  const badge = document.getElementById('profile-bmi-preview');

  if (!badge) return;

  if (h > 0 && w > 0) {
    const heightM = h / 100.0;
    const bmi = (w / (heightM * heightM)).toFixed(1);
    let category = "Normal";
    let catClass = "badge-normal";

    if (bmi < 18.5) {
      category = "Underweight";
      catClass = "badge-underweight";
    } else if (bmi >= 25.0 && bmi < 30.0) {
      category = "Overweight";
      catClass = "badge-overweight";
    } else if (bmi >= 30.0) {
      category = "Obese";
      catClass = "badge-obese";
    }

    badge.className = `badge ${catClass}`;
    badge.innerText = `BMI: ${bmi} (${category})`;
  } else {
    badge.className = 'badge';
    badge.innerText = 'BMI: --';
  }
}

async function handleProfileSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const submitBtn = form.querySelector('button[type="submit"]');

  const name = document.getElementById('profile_name').value.trim();
  const age = document.getElementById('profile_age').value;
  const gender = document.getElementById('profile_gender').value;
  const height = document.getElementById('profile_height').value;
  const weight = document.getElementById('profile_weight').value;
  const fitnessGoal = document.getElementById('profile_fitness_goal').value;

  if (!name) {
    Toast.error('Name cannot be empty');
    return;
  }

  submitBtn.disabled = true;
  submitBtn.innerText = 'Updating...';

  try {
    await apiRequest('/api/profile', {
      method: 'PUT',
      body: JSON.stringify({
        name,
        age: age ? parseInt(age, 10) : null,
        gender: gender || null,
        height: height ? parseFloat(height) : null,
        weight: weight ? parseFloat(weight) : null,
        fitness_goal: fitnessGoal || 'General Fitness'
      })
    });

    Toast.success('Profile updated successfully!');
    closeProfileModal();
    if (window.dashboard && window.dashboard.refresh) {
      window.dashboard.refresh();
    }
  } catch (err) {
    Toast.error(err.message || 'Failed to update profile');
  } finally {
    submitBtn.disabled = false;
    submitBtn.innerText = 'Save Changes';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('profile-form');
  if (form) form.addEventListener('submit', handleProfileSubmit);

  const hInput = document.getElementById('profile_height');
  const wInput = document.getElementById('profile_weight');
  if (hInput) hInput.addEventListener('input', updateLiveBmiPreview);
  if (wInput) wInput.addEventListener('input', updateLiveBmiPreview);
});

window.openProfileModal = openProfileModal;
window.closeProfileModal = closeProfileModal;
