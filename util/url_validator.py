import ipaddress
import socket
from urllib.parse import urlparse

from core.config import settings
from core.exceptions import InvalidURLError

BLOCKED_HOSTNAMES = frozenset(
    {
        "localhost",
        "metadata.google.internal",
        "metadata.goog",
    }
)

def _is_restricted_ip(ip_str: str) -> bool:
    """Return True when an IP address should not be reachable from audits."""
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True

    if ip.version == 4 and int(ip) == 0:
        return True

    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _check_resolved_ips(hostname: str, port: int | None) -> None:
    """Resolve a hostname and block private or restricted destinations."""
    try:
        addrinfo = socket.getaddrinfo(hostname, port, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise InvalidURLError(f"Unable to resolve hostname '{hostname}'") from exc

    if not addrinfo:
        raise InvalidURLError(f"Unable to resolve hostname '{hostname}'")

    for _, _, _, _, sockaddr in addrinfo:
        if _is_restricted_ip(sockaddr[0]):
            raise InvalidURLError(
                f"Hostname '{hostname}' resolves to a private or restricted IP address"
            )


def validate_url(url: str) -> str:
    """Validate and normalize a user-supplied URL, blocking SSRF-style targets."""
    normalized = url.strip()
    if not normalized:
        raise InvalidURLError("URL is required")

    if len(normalized) > settings.MAX_URL_LENGTH:
        raise InvalidURLError("URL exceeds maximum length")

    parsed = urlparse(normalized)

    if parsed.scheme not in {"http", "https"}:
        raise InvalidURLError("URL must use http or https scheme")

    if not parsed.netloc or not parsed.hostname:
        raise InvalidURLError("URL must include a valid hostname")

    if parsed.username or parsed.password:
        raise InvalidURLError("URLs with embedded credentials are not allowed")

    hostname = parsed.hostname.lower()
    if hostname in BLOCKED_HOSTNAMES:
        raise InvalidURLError(f"Hostname '{hostname}' is not allowed")

    try:
        ip = ipaddress.ip_address(hostname)
        if _is_restricted_ip(str(ip)):
            raise InvalidURLError(f"IP address '{hostname}' is not allowed")
        return normalized
    except ValueError:
        pass

    _check_resolved_ips(hostname, parsed.port)

    return normalized
