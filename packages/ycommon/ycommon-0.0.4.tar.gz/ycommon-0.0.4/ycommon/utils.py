from django.conf import settings
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib


def get_quarter_from_month(month):
    return (month - 1) // 3 + 1


def xfloat(var):
    if var == "None" or var is None or var == "":
        var = 0
    return var


def send_noreply_email(subject, message, recipient, from_name="Yeoki notification"):
    msg = MIMEMultipart()
    msg["From"] = f"{from_name} <{settings.EMAIL_HOST_USER}>"

    msg["To"] = recipient
    msg["Subject"] = subject

    msg.attach(MIMEText(message.replace("\n", "<br/>"), "html"))

    server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT)

    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    text = msg.as_string()
    server.sendmail(settings.EMAIL_HOST_USER, recipient, text)
    server.quit()

    #NoReplyMail.objects.create(subject=subject, message=message, recipient=recipient)

    return True