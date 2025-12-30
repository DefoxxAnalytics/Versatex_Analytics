"""
Utility functions for authentication
"""
import hashlib
import logging
from django.core.cache import cache
from .models import AuditLog

logger = logging.getLogger('authentication')

# Rate limiting settings for failed login attempts
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes in seconds


def get_client_ip(request):
    """
    Get client IP address from request.
    Handles X-Forwarded-For header for proxied requests.

    Security Note: X-Forwarded-For can be spoofed. In production,
    configure your proxy to set a trusted header.
    """
    # Try trusted proxy header first (configure this in your proxy)
    x_real_ip = request.META.get('HTTP_X_REAL_IP')
    if x_real_ip:
        return x_real_ip.strip()

    # Fall back to X-Forwarded-For (take first IP only)
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        # Only trust the first IP (closest to client)
        ip = x_forwarded_for.split(',')[0].strip()
        return ip

    # Direct connection
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def get_user_agent(request):
    """Get user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')


def hash_user_agent(user_agent: str) -> str:
    """
    Hash the user agent string for privacy.
    We don't need the full UA string, just enough for fingerprinting.
    """
    if not user_agent:
        return ''
    return hashlib.sha256(user_agent.encode()).hexdigest()[:32]


def get_failed_login_key(ip: str) -> str:
    """Generate cache key for failed login tracking"""
    return f'failed_login:{ip}'


def record_failed_login(request, username: str):
    """
    Record a failed login attempt and check for lockout.

    Returns:
        tuple: (is_locked_out, remaining_attempts)
    """
    ip = get_client_ip(request)
    key = get_failed_login_key(ip)

    # Get current failed attempts
    failed_attempts = cache.get(key, 0) + 1
    cache.set(key, failed_attempts, LOCKOUT_DURATION)

    # Log the failed attempt
    logger.warning(
        f"Failed login attempt | "
        f"IP: {ip} | "
        f"Username: {username} | "
        f"Attempts: {failed_attempts}/{MAX_FAILED_ATTEMPTS} | "
        f"User-Agent: {get_user_agent(request)[:100]}"
    )

    remaining = max(0, MAX_FAILED_ATTEMPTS - failed_attempts)
    is_locked = failed_attempts >= MAX_FAILED_ATTEMPTS

    if is_locked:
        logger.warning(
            f"Account lockout triggered | "
            f"IP: {ip} | "
            f"Username: {username} | "
            f"Lockout duration: {LOCKOUT_DURATION}s"
        )

    return is_locked, remaining


def check_login_lockout(request) -> bool:
    """
    Check if IP is currently locked out due to failed attempts.

    Returns:
        bool: True if locked out, False otherwise
    """
    ip = get_client_ip(request)
    key = get_failed_login_key(ip)
    failed_attempts = cache.get(key, 0)
    return failed_attempts >= MAX_FAILED_ATTEMPTS


def clear_failed_logins(request):
    """Clear failed login attempts after successful login"""
    ip = get_client_ip(request)
    key = get_failed_login_key(ip)
    cache.delete(key)


def log_action(user, action, resource, resource_id='', details=None, request=None):
    """
    Log user action to audit log
    """
    if not hasattr(user, 'profile'):
        return None

    log_data = {
        'user': user,
        'organization': user.profile.organization,
        'action': action,
        'resource': resource,
        'resource_id': resource_id,
        'details': details or {},
    }

    if request:
        log_data['ip_address'] = get_client_ip(request)
        # Hash user agent for privacy
        log_data['user_agent'] = hash_user_agent(get_user_agent(request))

    return AuditLog.objects.create(**log_data)


def log_security_event(event_type: str, request, details: dict = None):
    """
    Log a security event (not tied to a specific user action).

    Args:
        event_type: Type of security event (e.g., 'failed_login', 'lockout')
        request: The HTTP request object
        details: Additional details to log
    """
    ip = get_client_ip(request)
    user_agent = get_user_agent(request)

    log_message = (
        f"Security Event: {event_type} | "
        f"IP: {ip} | "
        f"User-Agent: {user_agent[:100]}"
    )

    if details:
        log_message += f" | Details: {details}"

    logger.info(log_message)
