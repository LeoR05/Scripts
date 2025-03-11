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

def check_new_backups(path):
    command = "find " + path + " -type f -mtime -1 -exec ls -lh {} \\;"
    #command = "ls -l " + path
    r = subprocess.check_output(command, shell=True, universal_newlines=True)
    if r.strip():
        print(r)
    else:
        print("No se tomaron nuevos backups en las ultimas 24hrs")
        send_mail()

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

def check_size():
    command = "du * -sb " + path
    res = subprocess.check_output(command, shell=True, universal_newlines=True)

    for line in res.splitlines():
        size, file = line.split("\t")
        value = size
        if value < 10 * 1024 *1024:
            print("Este es el valor")
            print ("{}\t\t{}".format(file, size))
        else:
            print("No existen archivos nuevos")

check_new_backups(path)
