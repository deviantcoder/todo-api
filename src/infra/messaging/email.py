from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from src.core.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,  # type: ignore
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True
)

mail = FastMail(conf)


async def send_email(
    subject: str, recipients: list[str], body: str
) -> None:
    """
    Send an email using FastAPI-Mail.

    Args:
        subject (str): The subject of the email.
        recipients (list[str]): A list of recipient email addresses.
        body (str): The body of the email.
    """
    message = MessageSchema(
        subject=subject,
        recipients=recipients,  # type: ignore
        body=body,
        subtype=MessageType.html
    )
    await mail.send_message(message)
