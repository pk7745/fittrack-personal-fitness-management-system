/**
 * Authentication handlers (Login & Registration)
 */
document.addEventListener('DOMContentLoaded', () => {
  // Login Form Handler
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const submitBtn = loginForm.querySelector('button[type="submit"]');

      if (!email || !password) {
        Toast.error('Please enter both email and password');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerText = 'Signing in...';

      try {
        const res = await apiRequest('/api/auth/login', {
          method: 'POST',
          body: JSON.stringify({ email, password })
        });
        Toast.success('Login successful! Redirecting...');
        setTimeout(() => {
          window.location.href = '/';
        }, 600);
      } catch (err) {
        Toast.error(err.message || 'Login failed. Please check credentials.');
        submitBtn.disabled = false;
        submitBtn.innerText = 'Sign In';
      }
    });
  }

  // Register Form Handler
  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = registerForm.querySelector('button[type="submit"]');

      const name = document.getElementById('name').value.trim();
      const email = document.getElementById('email').value.trim();
      const password = document.getElementById('password').value;
      const age = document.getElementById('age').value;
      const gender = document.getElementById('gender').value;
      const height = document.getElementById('height').value;
      const weight = document.getElementById('weight').value;
      const fitnessGoal = document.getElementById('fitness_goal').value;

      if (!name || !email || !password) {
        Toast.error('Please fill in all required fields (Name, Email, Password)');
        return;
      }

      if (password.length < 6) {
        Toast.error('Password must be at least 6 characters');
        return;
      }

      submitBtn.disabled = true;
      submitBtn.innerText = 'Creating Account...';

      try {
        const payload = {
          name,
          email,
          password,
          age: age ? parseInt(age, 10) : null,
          gender: gender || null,
          height: height ? parseFloat(height) : null,
          weight: weight ? parseFloat(weight) : null,
          fitness_goal: fitnessGoal || 'General Fitness'
        };

        const res = await apiRequest('/api/auth/register', {
          method: 'POST',
          body: JSON.stringify(payload)
        });

        Toast.success('Account created! Welcome to FitTrack.');
        setTimeout(() => {
          window.location.href = '/';
        }, 800);
      } catch (err) {
        Toast.error(err.message || 'Registration failed.');
        submitBtn.disabled = false;
        submitBtn.innerText = 'Create Account';
      }
    });
  }
});

// Logout Helper Function
async function handleLogout() {
  try {
    await apiRequest('/api/auth/logout', { method: 'POST' });
    Toast.success('Logged out successfully');
    window.location.href = '/login';
  } catch (err) {
    window.location.href = '/login';
  }
}
window.handleLogout = handleLogout;
