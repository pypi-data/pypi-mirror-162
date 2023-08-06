"""Imap filter."""
from typing import Optional

from promail.filters.email_filter import EmailFilter


class ImapFilter(EmailFilter):
    """Imap Filter."""

    @staticmethod
    def _get_date(term, date):
        if date is None:
            return ""
        return [term, date.strftime("%G/%m/%d")]

    @staticmethod
    def _get_string(term: str, data: Optional[str]):
        if data is None:
            return None
        return [term, data]

    @staticmethod
    def _join_tuple(term: str, data: Optional[tuple]):
        if data is None or len(data) == 0:
            q = None
        elif len(data) == 1:
            q = [term, data[0]]
        else:
            q = ["OR"] * len(data)
            for d in data:
                q.extend([term, d])
        return q

    @property
    def bcc(self) -> Optional[list]:
        """Email BCC Query."""
        return self._join_tuple("BCC", self._bcc)

    @property
    def body(self) -> Optional[list]:
        """Messages that contain the specified string in the body of the message."""
        return self._get_string("BODY", self._body)

    @property
    def cc(self) -> Optional[list]:
        """CC filter.

        Messages that contain the specified string
        in the envelope structure's CC field.

        Returns:
            list: ["CC", "emails]"
        """
        return self._join_tuple("CC", self._cc)

    @property
    def sender(self):
        """Search query based on sender."""
        return self._get_string("FROM", self._sender)

    @property
    def sent_before(self):
        """Messages whose internal date is earlier than the specified date."""
        return self._get_string("BEFORE ", self._sent_before)

    @property
    def size_larger(self):
        """Search query based on size_larger."""
        return self._get_string("LARGER", self._size_larger)

    @property
    def subject(self) -> Optional[list]:
        """Email Subject Query."""
        return self._get_string("SUBJECT", self._subject)

    @property
    def to(self) -> Optional[list]:
        """Email Subject Query."""
        return self._join_tuple("TO", self._to)

    def get_filter_list(self) -> list:
        """Combine search parameters into query."""
        f_list = []
        data = (
            self.subject,
            self.bcc,
        )
        for parameter in data:
            if parameter is not None:
                f_list.extend(parameter)
        return f_list

    def filter_results(self, messages):
        """Removes messages in self.processed."""
        return filter(lambda msg_id: msg_id not in self.processed, messages)
