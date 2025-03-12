import subprocess
import smtplib
from email.mime.text import MIMEText

#Mail config
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
EMAIL_SENDER = "rspalerta@celeren.com"
EMAIL_PASSWORD = "qscxhzzdcmlflfcj"
EMAIL_RECEIVER = "leonardo.rojas@celeren.com"

path = "/sapbackups/backups/instancia"

def send_mail():
    try:
        subject = "Alerta de Backups"
        body = "No se detectaron nuevos backups"
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER,EMAIL_RECEIVER, msg.as_string())
        print("Correo enviado correctamente")       
    except Exception as error:
        print("Error al enviar el correo " + error)