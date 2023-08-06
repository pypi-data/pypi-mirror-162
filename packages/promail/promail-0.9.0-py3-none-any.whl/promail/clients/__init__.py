"""Email Clients."""
from .aws import AWSClient
from .gmail import GmailClient
from .imap_client import ImapClient
from .microsoft import HotmailClient
from .smtp_client import SmtpClient

try:
    from importlib.metadata import version, PackageNotFoundError  # type: ignore
except ImportError:  # pragma: no cover
    from importlib_metadata import version, PackageNotFoundError  # type: ignore

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"

__all__ = [
    "AWSClient",
    "email_manager",
    "gmail",
    "GmailClient",
    "HotmailClient",
    "ImapClient",
    "SmtpClient",
]
