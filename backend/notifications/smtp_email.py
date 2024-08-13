import smtplib
from email.message import EmailMessage

from core.settings import settings
from logs.get_logger import logger


class SmtpEmail:
    def __init__(
        self,
        smtp_host: str = settings.smtp.host,
        smtp_port: int = settings.smtp.port,
        smtp_user: str = settings.smtp.user,
        smtp_password: str = settings.smtp.password,
    ):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password

    def send_email(self, template) -> bool:
        try:
            with smtplib.SMTP_SSL(host=self.smtp_host, port=self.smtp_port) as server:
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(template)
                logger.info(f"Send email notify successfully, template: {template}")
                return True

        except smtplib.SMTPException as smtp_er:
            logger.exception(smtp_er)
            return False

        except Exception as er:
            logger.exception(er)
            return False

    def get_email_template(
        self, user_email: str, title: str, content: str
    ) -> EmailMessage:
        email = EmailMessage()
        email["Subject"] = title
        email["From"] = self.smtp_user
        email["To"] = user_email
        email.set_content(content, subtype="html")
        return email


smtp_email = SmtpEmail(
    smtp_host=settings.smtp.host,
    smtp_port=settings.smtp.port,
    smtp_user=settings.smtp.user,
    smtp_password=settings.smtp.password,
)
