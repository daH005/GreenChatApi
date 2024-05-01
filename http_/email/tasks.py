from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from celery import Celery

from api.config import REDIS_URL
from api.config import (
    EMAIL,
    EMAIL_PASSWORD,
    SMTP_HOST,
    SMTP_PORT,
)

__all__ = (
    'app',
    'send_code_task',
)

app: Celery = Celery(broker=REDIS_URL, broker_connection_retry_on_startup=True)


@app.task(name='send_code_task')
def send_code_task(to: str,
                   code: int | str,
                   ) -> None:
    msg = MIMEMultipart()
    msg['Subject'] = 'GreenChat - Подтверждение почты'
    msg['From'] = EMAIL
    msg.attach(MIMEText('Ваш код подтверждения: ' + str(code)))

    with SMTP_SSL(host=SMTP_HOST, port=SMTP_PORT) as server:
        server.login(user=EMAIL, password=EMAIL_PASSWORD)
        server.sendmail(from_addr=EMAIL, to_addrs=to, msg=msg.as_string())
