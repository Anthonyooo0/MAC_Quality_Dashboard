/**
 * Convert a UTC date string to Eastern Time display string.
 * Handles various input formats including ISO 8601 and common date strings.
 */
export function toEasternTime(utcStr: string | null): string {
  if (!utcStr) return '';

  try {
    // Try parsing as-is first
    let date = new Date(utcStr);

    // If the string doesn't end with Z or have timezone info, treat as UTC
    if (!utcStr.endsWith('Z') && !utcStr.includes('+') && !utcStr.includes('-', 10)) {
      date = new Date(utcStr + 'Z');
    }

    if (isNaN(date.getTime())) return utcStr;

    return new Intl.DateTimeFormat('en-US', {
      timeZone: 'America/New_York',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      hour12: true,
    }).format(date);
  } catch {
    return utcStr;
  }
}

/**
 * Parse a date string into a Date object for comparison.
 * Returns null if parsing fails.
 */
export function parseDate(dateStr: string | null): Date | null {
  if (!dateStr) return null;
  try {
    const d = new Date(dateStr);
    return isNaN(d.getTime()) ? null : d;
  } catch {
    return null;
  }
}

/**
 * Format a Date to YYYY-MM-DD for input[type=date] value.
 */
export function toDateInputValue(date: Date): string {
  return date.toISOString().split('T')[0];
}
