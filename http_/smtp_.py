from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from api.config import EMAIL, EMAIL_PASSWORD

__all__ = (
    'SMTP_URL',
    'send_code',
)

SMTP_URL = 'smtp.' + EMAIL[EMAIL.index('@') + 1:]


def send_code(to: str,
              code: int | str,
              ) -> None:
    """Отправляет код подтверждения на указанную почту."""
    # Оформляем сообщение:
    msg = MIMEMultipart()
    msg['Subject'] = 'GreenChat - Подтверждение почты'
    msg['From'] = EMAIL
    msg.attach(MIMEText('Ваш код подтверждения: ' + str(code)))
    # Устанавливаем соединение, логинимся и отправляем сообщение:
    with SMTP_SSL(host=SMTP_URL, port=465) as server:
        server.login(user=EMAIL, password=EMAIL_PASSWORD)
        server.sendmail(from_addr=EMAIL, to_addrs=to, msg=msg.as_string())


if __name__ == '__main__':
    send_code(EMAIL, 55)
