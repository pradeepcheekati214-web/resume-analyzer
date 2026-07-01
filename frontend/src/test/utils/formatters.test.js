import { describe, it, expect } from 'vitest';
import { formatFileSize, truncate, getInitials, capitalize } from '@/utils/formatters';

describe('formatFileSize', () => {
  it('formats bytes correctly', () => {
    expect(formatFileSize(0)).toBe('0 B');
    expect(formatFileSize(1024)).toBe('1.0 KB');
    expect(formatFileSize(1024 * 1024)).toBe('1.0 MB');
    expect(formatFileSize(512)).toBe('512 B');
  });
});

describe('truncate', () => {
  it('returns original string if under limit', () => {
    expect(truncate('hello', 10)).toBe('hello');
  });
  it('truncates and appends ellipsis', () => {
    expect(truncate('hello world foo', 10)).toBe('hello worl…');
  });
  it('handles empty string', () => {
    expect(truncate('')).toBe('');
  });
});

describe('getInitials', () => {
  it('extracts two initials from full name', () => {
    expect(getInitials('John Doe')).toBe('JD');
  });
  it('returns single initial for single name', () => {
    expect(getInitials('Alice')).toBe('A');
  });
  it('handles empty input', () => {
    expect(getInitials('')).toBe('?');
  });
});

describe('capitalize', () => {
  it('capitalizes first letter', () => {
    expect(capitalize('hello')).toBe('Hello');
  });
  it('lowercases remaining letters', () => {
    expect(capitalize('HELLO')).toBe('Hello');
  });
});
