/**
 * FitTrack v1.1 - Responsive Navigation Handler
 */
function initNavigation() {
  const toggleBtn = document.getElementById('mobile-menu-toggle');
  const sidebar = document.getElementById('app-sidebar');
  const backdrop = document.getElementById('sidebar-backdrop');

  if (toggleBtn && sidebar) {
    toggleBtn.addEventListener('click', () => {
      const isOpen = sidebar.classList.toggle('open');
      toggleBtn.classList.toggle('active', isOpen);
      if (backdrop) backdrop.classList.toggle('active', isOpen);
      document.body.style.overflow = isOpen ? 'hidden' : '';
    });
  }

  if (backdrop && sidebar) {
    backdrop.addEventListener('click', () => {
      sidebar.classList.remove('open');
      if (toggleBtn) toggleBtn.classList.remove('active');
      backdrop.classList.remove('active');
      document.body.style.overflow = '';
    });
  }

  // Close sidebar on pressing Escape
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && sidebar && sidebar.classList.contains('open')) {
      sidebar.classList.remove('open');
      if (toggleBtn) toggleBtn.classList.remove('active');
      if (backdrop) backdrop.classList.remove('active');
      document.body.style.overflow = '';
    }
  });
}

document.addEventListener('DOMContentLoaded', initNavigation);
