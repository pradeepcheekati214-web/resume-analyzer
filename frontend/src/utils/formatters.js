import { format, formatDistanceToNow, parseISO } from 'date-fns';

export function formatDate(dateString, fmt = 'MMM d, yyyy') {
  if (!dateString) return '—';
  try { return format(parseISO(dateString), fmt); } catch { return '—'; }
}

export function formatRelativeTime(dateString) {
  if (!dateString) return '—';
  try { return formatDistanceToNow(parseISO(dateString), { addSuffix: true }); } catch { return '—'; }
}

export function formatFileSize(bytes) {
  if (!bytes) return '0 B';
  const units = ['B', 'KB', 'MB', 'GB'];
  let i = 0, size = bytes;
  while (size >= 1024 && i < units.length - 1) { size /= 1024; i++; }
  return `${size.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

export function capitalize(str) {
  if (!str) return '';
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

export function truncate(str, maxLength = 60) {
  if (!str) return '';
  return str.length <= maxLength ? str : str.slice(0, maxLength) + '…';
}

export function getInitials(name) {
  if (!name) return '?';
  return name.split(' ').filter(Boolean).slice(0, 2).map((n) => n[0].toUpperCase()).join('');
}

export function toTitleCase(str) {
  if (!str) return '';
  return str.replace(/[-_]/g, ' ')
    .replace(/\w\S*/g, (txt) => txt.charAt(0).toUpperCase() + txt.slice(1).toLowerCase());
}
