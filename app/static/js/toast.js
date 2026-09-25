/**
 * FitTrack Toast Notification System
 */
const Toast = {
  container: null,

  init() {
    if (!this.container) {
      let existing = document.getElementById('toast-container');
      if (!existing) {
        existing = document.createElement('div');
        existing.id = 'toast-container';
        document.body.appendChild(existing);
      }
      this.container = existing;
    }
  },

  show(message, type = 'info', duration = 3500) {
    this.init();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icon = type === 'success' ? '✓' : type === 'error' ? '⚠' : 'ℹ';

    toast.innerHTML = `
      <div style="display:flex;align-items:center;gap:0.5rem;">
        <span style="font-weight:bold;">${icon}</span>
        <span>${message}</span>
      </div>
      <button class="toast-close" aria-label="Close notification">&times;</button>
    `;

    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
      toast.remove();
    });

    this.container.appendChild(toast);

    if (duration > 0) {
      setTimeout(() => {
        if (toast.parentElement) {
          toast.style.opacity = '0';
          toast.style.transform = 'translateX(100%)';
          toast.style.transition = 'all 0.3s ease';
          setTimeout(() => toast.remove(), 300);
        }
      }, duration);
    }
  },

  success(msg, dur) { this.show(msg, 'success', dur); },
  error(msg, dur) { this.show(msg, 'error', dur); },
  info(msg, dur) { this.show(msg, 'info', dur); }
};

window.Toast = Toast;
