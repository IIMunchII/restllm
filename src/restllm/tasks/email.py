import aiosmtplib
from email.message import EmailMessage
from ..settings import settings


async def send_email(subject: str, recipient: str, body: str):
    message = EmailMessage()
    message["From"] = settings.email_username
    message["To"] = recipient
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=settings.email_hostname,
        port=settings.email_port,
        username=settings.email_username,
        password=settings.email_password.get_secret_value(),
        start_tls=True,
    )


async def send_email_verification_url(
    recipient: str,
    verification_url: str,
) -> None:
    subject = "Email verification"
    body = f"Hi there \n\n Thanks for signing up! \n\n Please verify your email by using this link: {verification_url}"
    await send_email(subject, recipient, body)
