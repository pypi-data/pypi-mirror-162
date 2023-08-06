"""Implements Outbound client for AWS SES."""
import os
from enum import Enum
from typing import Any, List, Optional

import boto3

from pydantic import AnyUrl, BaseModel, EmailStr, ValidationError, validator

from promail.clients.email_manager import OutBoundManager
from promail.core.embedded_attachments import EmbeddedAttachments


class AWSCredentialsError(Exception):
    """AWS Credentials Error."""

    pass


class ContactLanguageEnum(str, Enum):
    """AWS Support Languages."""

    english = "EN"
    japanese = "JP"


class MailTypeEnum(str, Enum):
    """SES Email Types."""

    marketing = "MARKETING"
    transactional = "TRANSACTIONAL"


class SesAccountDetails(BaseModel):
    """Validation for SES Account Details."""

    MailType: MailTypeEnum
    WebsiteURL: AnyUrl
    UseCaseDescription: str
    AdditionalContactEmailAddresses: List[EmailStr] = []
    ContactLanguage: ContactLanguageEnum
    ProductionAccessEnabled: bool = True

    @validator("UseCaseDescription")
    def validate_length(cls, value: str):  # noqa: B902
        """Validate UseCaseDescription length.

        Args:
            value (str): Description of use.

        Returns:
            Description of use of no errors.

        Raises:
            ValueError: if length of v < 1 or > 5000.

        """
        if len(value) not in range(1, 5001):
            raise ValueError(
                f"Description must be between 1 and 5000 characters not {len(value)}"
            )
        return value

    class Config:
        """Configure SesAccountDetails."""

        # When you see a field with an enum type
        # use the enum value instead of the enum name.
        use_enum_values = True


class AWSClient(OutBoundManager):
    """AWS Outbound Email Manager.

    AWS Account is required:https://docs.aws.amazon.com/ses/latest/dg/setting-up.html.

    Args:
            account (str): email account
            region_name  (str): aws region
            aws_access_key_id (Optional[str]): aws_access_key_id
            aws_secret_access_key (Optional[str]): aws_secret_access_key
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

    Notes:
        For setup:
            https://hands-on.cloud/working-with-amazon-ses-in-python/#h-sandbox-mode
        Boto3 Documentations:
           https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ses.html

    """

    def __init__(
        self,
        account: str,
        region_name,
        aws_access_key_id=None,
        aws_secret_access_key=None,
        *args,
        **kwargs,
    ):
        """Initializes AWSClient."""
        super(OutBoundManager, self).__init__(account, *args, **kwargs)
        self._aws_access_key_id = aws_access_key_id
        self._aws_secret_access_key = aws_secret_access_key
        self.region_name = region_name
        self.ses_client = self._get_client("ses")

    def _get_client(self, service: Any) -> Any:
        """This function returns a boto3 client object for the specified service.

        Args:
            service (Any): The name of the AWS service you want to use

        Returns:
            A boto3 client object.
        """
        return boto3.client(
            service,
            region_name=self.region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

    @property
    def aws_access_key_id(self) -> str:
        """Get aws_access_key_id.

        Will Get value from class initialization or environment variable,
        prioritises initialization.

        Raises:
            AWSCredentialsError: If neither environment variable or inital value is
                set.

        Returns:
            str:  aws_access_key_id value.

        """
        if self._aws_access_key_id is None:
            self._aws_access_key_id = os.environ.get("aws_access_key_id")
            if self._aws_access_key_id is None:
                raise AWSCredentialsError("aws_access_key_id is not set")
        return self._aws_access_key_id

    @property
    def aws_secret_access_key(self) -> str:
        """Get aws_secret_access_key.

        Will Get value from class initialization or environment variable,
        prioritises initialization.

        Raises:
            AWSCredentialsError: If neither environment variable or inital value is
                set.

        Returns:
            str:  aws_secret_access_key value.

        """
        if self._aws_secret_access_key is None:
            self._aws_secret_access_key = os.environ.get("aws_secret_access_key")
            if self._aws_secret_access_key is None:
                raise AWSCredentialsError("aws_access_key_id is not set")
        return self._aws_secret_access_key

    def verify_email(self):
        """Verify ownership of email.

        It sends an email to the email address you want to verify.
        Open the email and click on the link in the email to verify that you
        own the email address.  After which you will be able to use it to
        send outgoing SES messages.

        """
        self.ses_client.verify_email_address(EmailAddress=self._account)

    def verify_domain(self):
        """Returns list of CNAME Records to publish to Domain name provider."""
        assert self._account.count("@") == 1
        domain = self._account.split("@")[1]
        self.ses_client.verify_domain_identity(Domain=domain)
        response = self.ses_client.verify_domain_dkim(Domain=domain)
        return [
            self.construct_cname_records(domain, token)
            for token in response.get("DkimTokens", [])
        ]

    @staticmethod
    def construct_cname_records(domain: str, token: str):
        """Constructs cname records for SES verification.

        It takes a domain and a token and returns a dictionary
        with the key-value pairs needed to create a CNAME entry.

        Args:
            domain (str): The domain name that you want to verify
            token (str): The Token is a unique string generate from
                verify_domain method.

        Returns:
            dict: A dictionary with the key value pairs of Name, Type, and Value.

        """
        return {
            "Name": f"{token}._domainkey.{domain}",
            "Type": "CNAME",
            "Value": f"{token}.dkim.amazonses.com",
        }

    def send_email(
        self,
        recipients: str = "",
        cc: str = "",
        bcc: str = "",
        subject: str = "",
        htmltext: str = "",
        plaintext: str = "",
        embedded_attachments: Optional[List[EmbeddedAttachments]] = None,
        attachments: Optional[list] = None,
    ) -> None:
        """Send an email.

        Args:
            recipients (str): Semi colon seperated emails Defaults to "".
            cc (str): Carbon copy Defaults to ""
            bcc (str): Blind carbon copy.
                This is a list of email addresses that will receive the email,
                but will not be visible to the other recipients.
            subject (str): The subject of the email.
            htmltext (str): The HTML version of the email.
            plaintext (str): The plaintext version of the email.
            embedded_attachments (Optional[List[EmbeddedAttachments]]): Images
                referenced in htmltext for to be embedded inline defaults to None.
            attachments (Optional[list]): A list of file paths to be
                attached to the email.

        """
        responses = []
        msg = self.create_message(
            recipients,
            cc,
            bcc,
            subject,
            htmltext,
            plaintext,
            embedded_attachments,
            attachments,
        )
        for recipient in recipients.split(";"):
            try:
                responses.append(
                    self.ses_client.send_raw_email(
                        Source=self._account,
                        Destinations=[recipient],
                        RawMessage={"Data": msg.as_string()},
                    )
                )
            except Exception as e:
                responses.append({"email": recipient, "error": e})
        print({"responses": str(responses)})

    def update_account_details(
        self,
        mail_type: str,
        web_site_url: str,
        use_case_description: str,
        additional_contacts: List[str],
        contact_language: str,
        enable_production: bool,
    ) -> None:
        """Detail your proposed usage for SES to request production.

        Notes:
            https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/sesv2.html#SESV2.Client.put_account_details
            https://docs.aws.amazon.com/ses/latest/APIReference-V2/API_PutAccountDetails.html

        Args:
            mail_type: The type of email your account will send.
                Valid Values: MARKETING | TRANSACTIONAL
            web_site_url: The URL of your website.
                This information helps AWS to better understand
                the type of content that you plan to send.
            use_case_description: A description of the types of email
                that you plan to send.
                Minimum length of 1. Maximum length of 5000.
            additional_contacts: Additional email addresses that you would like to be
                notified regarding Amazon SES matters. Can be empty an empty list
            contact_language: The language you would prefer to be contacted with.
                Valid Values - EN | JA
            enable_production: Indicates whether your account should have production
                access in the current AWS Region.

        """
        try:
            details = dict(
                SesAccountDetails(
                    MailType=mail_type.upper(),
                    WebsiteURL=web_site_url,
                    UseCaseDescription=use_case_description,
                    AdditionalContactEmailAddresses=additional_contacts,
                    ContactLanguage=contact_language,
                    ProductionAccessEnabled=enable_production,
                )
            )
            if not details["AdditionalContactEmailAddresses"]:
                del details["AdditionalContactEmailAddresses"]
            client = self._get_client("sesv2")
            client.put_account_details(**details)
        except ValidationError as e:
            print(e)

        client = self._get_client("sesv2")
        client.put_account_details(
            MailType=mail_type,
            WebsiteURL=web_site_url,
            ContactLanguage=contact_language,
            UseCaseDescription=use_case_description,
            AdditionalContactEmailAddresses=additional_contacts,
            ProductionAccessEnabled=enable_production,
        )
