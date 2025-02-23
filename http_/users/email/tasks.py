from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP_SSL, SMTPAuthenticationError
from typing import Final

from celery import Celery

from config.api import REDIS_URL, SMTP_HOST, SMTP_PORT, EMAIL, EMAIL_PASSWORD

__all__ = (
    'app',
    'send_code_task',
)

app: Celery = Celery(broker=REDIS_URL, broker_connection_retry_on_startup=True)

_MESSAGE_TITLE: Final[str] = 'GreenChat - Подтверждение почты'
_MESSAGE_TEXT_TEMPLATE: Final[str] = 'Ваш код подтверждения: {}'


@app.task(name='send_code_task', max_retries=0)
def send_code_task(to: str,
                   code: int | str,
                   ) -> None:
    msg = MIMEMultipart()
    msg['Subject'] = _MESSAGE_TITLE
    msg['From'] = EMAIL
    msg.attach(MIMEText(_MESSAGE_TEXT_TEMPLATE.format(str(code))))

    try:
        connection: SMTP_SSL = SMTP_SSL(SMTP_HOST, SMTP_PORT)
    except SMTPAuthenticationError:
        return

    connection.login(EMAIL, EMAIL_PASSWORD)
    connection.sendmail(EMAIL, to, msg.as_string())

    connection.close()
