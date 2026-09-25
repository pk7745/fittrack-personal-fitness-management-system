/**
 * FitTrack v1.1 - Reports & Data Export Module
 */
function exportReport(type) {
  let endpoint = '';
  let filename = '';

  switch (type) {
    case 'workouts':
      endpoint = '/api/reports/workouts.csv';
      filename = 'fittrack_workouts.csv';
      break;
    case 'fitness':
      endpoint = '/api/reports/fitness.csv';
      filename = 'fittrack_fitness.csv';
      break;
    case 'goals':
      endpoint = '/api/reports/goals.csv';
      filename = 'fittrack_goals.csv';
      break;
    case 'summary':
      endpoint = '/api/reports/summary.csv';
      filename = 'fittrack_summary.csv';
      break;
    case 'pdf':
      endpoint = '/api/reports/fitness.pdf';
      filename = 'fittrack_report.pdf';
      break;
    default:
      Toast.error('Unknown export type');
      return;
  }

  Toast.info(`Generating ${type.toUpperCase()} report...`);

  // Direct download trigger
  const link = document.createElement('a');
  link.href = endpoint;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

window.exportReport = exportReport;
