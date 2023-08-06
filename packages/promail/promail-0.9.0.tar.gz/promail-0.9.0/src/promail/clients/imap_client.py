"""Imap Client."""
import imaplib
import logging

from imapclient import IMAPClient  # type: ignore

from promail.clients.email_manager import InBoundManager
from promail.core.messages.messages import Message
from promail.filters.email_filter import EmailFilter
from promail.filters.imap_filter import ImapFilter


class ImapClient(InBoundManager):
    """Imap Client."""

    def __init__(self, account, password, host, **kwargs):
        """Initiate IMAP client."""
        super(ImapClient, self).__init__(account)
        self._imap_host = host
        self._password = password
        self._filter_class = ImapFilter

    def _process_filter_messages(
        self, email_filter: EmailFilter, page_size=100, page_token=None
    ):
        # get emails that match search criteria
        with IMAPClient(host=self._imap_host) as client:
            client.login(self._account, self._password)
            client.select_folder("INBOX")
            results = client.search(email_filter.get_filter_list())

            # remove emails that have already been processed
            messages = email_filter.filter_results(results)
            try:
                for uid, message_data in client.fetch(messages, "RFC822").items():
                    email_message = Message({"raw": message_data[b"RFC822"]})
                    for func in self._registered_functions[email_filter]:
                        func(email_message)
                        email_filter.add_processed(uid)
            except imaplib.IMAP4.error as e:
                # FETCH command error if messages len == 0
                logging.info(e)
