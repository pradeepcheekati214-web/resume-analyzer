export const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.doc'];
export const MAX_FILE_SIZE_MB = parseInt(import.meta.env.VITE_MAX_FILE_SIZE_MB || '10');
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

export const ATS_SCORE_THRESHOLDS = { EXCELLENT: 80, GOOD: 60, FAIR: 40 };

export function getScoreColor(score) {
  if (score >= 80) return 'text-success-600';
  if (score >= 60) return 'text-primary-600';
  if (score >= 40) return 'text-warning-600';
  return 'text-danger-600';
}
export function getScoreBgColor(score) {
  if (score >= 80) return 'bg-success-50 border-success-200';
  if (score >= 60) return 'bg-primary-50 border-primary-200';
  if (score >= 40) return 'bg-warning-50 border-warning-200';
  return 'bg-danger-50 border-danger-200';
}
export function getScoreLabel(score) {
  if (score >= 80) return 'Excellent';
  if (score >= 60) return 'Good';
  if (score >= 40) return 'Fair';
  return 'Needs Work';
}
export function getScoreStrokeColor(score) {
  if (score >= 80) return '#22c55e';
  if (score >= 60) return '#2563eb';
  if (score >= 40) return '#f59e0b';
  return '#ef4444';
}

export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'ra_access_token',
  REFRESH_TOKEN: 'ra_refresh_token',
  USER: 'ra_user',
};

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export const DEFAULT_PAGE_SIZE = 10;

export const ANALYSIS_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
};
