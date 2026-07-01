import { ALLOWED_EXTENSIONS, MAX_FILE_SIZE_BYTES, MAX_FILE_SIZE_MB } from './constants';

export function validateResumeFile(file) {
  if (!file) return { valid: false, error: 'No file selected.' };
  const ext = '.' + file.name.split('.').pop().toLowerCase();
  if (!ALLOWED_EXTENSIONS.includes(ext))
    return { valid: false, error: 'Unsupported file type. Please upload a PDF or DOCX file.' };
  if (file.size > MAX_FILE_SIZE_BYTES)
    return { valid: false, error: `File too large. Maximum size is ${MAX_FILE_SIZE_MB} MB.` };
  return { valid: true };
}

export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

export function checkPasswordStrength(password) {
  if (!password) return { score: 0, label: '', color: '' };
  let score = 0;
  if (password.length >= 8) score++;
  if (password.length >= 12) score++;
  if (/[A-Z]/.test(password)) score++;
  if (/[0-9]/.test(password)) score++;
  if (/[^A-Za-z0-9]/.test(password)) score++;
  const levels = [
    { score: 0, label: 'Too short', color: 'bg-danger-500' },
    { score: 1, label: 'Weak',      color: 'bg-danger-500' },
    { score: 2, label: 'Fair',      color: 'bg-warning-500' },
    { score: 3, label: 'Good',      color: 'bg-secondary-500' },
    { score: 4, label: 'Strong',    color: 'bg-success-500' },
    { score: 5, label: 'Very Strong', color: 'bg-success-600' },
  ];
  return levels[Math.min(score, 5)];
}
