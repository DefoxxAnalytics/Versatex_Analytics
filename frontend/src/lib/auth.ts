/**
 * Authentication utilities for JWT-based authentication
 *
 * Security Features:
 * - JWT token management
 * - Session timeout (30 minutes inactivity)
 * - Secure token storage cleanup
 * - HTTPS enforcement in production
 */

const SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes
const LAST_ACTIVITY_KEY = 'analytics_last_activity';

/**
 * Check if user has a valid JWT token
 *
 * @returns True if access token exists
 */
export function isAuthenticated(): boolean {
  const accessToken = localStorage.getItem('access_token');
  const user = localStorage.getItem('user');

  return !!(accessToken && user);
}

/**
 * Update the last activity timestamp
 * Call this on user interactions to prevent timeout
 */
export function updateActivity(): void {
  const now = Date.now();
  localStorage.setItem(LAST_ACTIVITY_KEY, now.toString());
}

/**
 * Clear the current session (logout)
 */
export function clearSession(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  localStorage.removeItem(LAST_ACTIVITY_KEY);
}

/**
 * Get remaining session time in milliseconds
 *
 * @returns Remaining time in ms, or 0 if no session
 */
export function getRemainingSessionTime(): number {
  const lastActivity = localStorage.getItem(LAST_ACTIVITY_KEY);

  if (!lastActivity) {
    return 0;
  }

  const lastActivityTime = parseInt(lastActivity, 10);
  const now = Date.now();
  const timeSinceActivity = now - lastActivityTime;
  const remaining = SESSION_TIMEOUT_MS - timeSinceActivity;

  return Math.max(0, remaining);
}

/**
 * Check if session has timed out due to inactivity
 *
 * @returns True if session has timed out
 */
export function isSessionExpired(): boolean {
  if (!isAuthenticated()) {
    return true;
  }
  return getRemainingSessionTime() <= 0;
}

/**
 * Check if HTTPS is being used (production requirement)
 *
 * @returns True if using HTTPS or localhost
 */
export function isSecureContext(): boolean {
  // Allow localhost for development
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return true;
  }

  // Require HTTPS in production
  return window.location.protocol === 'https:';
}

/**
 * Initialize session tracking after login
 */
export function initializeSession(): void {
  updateActivity();
}
