"""Outlook/Hotmail Mail Client."""
from promail.clients.imap_client import ImapClient
from promail.clients.smtp_client import SmtpClient


class HotmailClient(SmtpClient, ImapClient):
    """Hotmail/Outlook.com Client.

    Should work on most SMTP/IMAP based if correct hosts are set.
    """

    def __init__(
        self,
        account,
        password,
        smtp_host="smtp-mail.outlook.com",
        imap_host="outlook.office365.com",
    ):
        """Hotmail Email Client Initiation."""
        SmtpClient.__init__(self, account=account, password=password, host=smtp_host)
        ImapClient.__init__(self, account=account, password=password, host=imap_host)
