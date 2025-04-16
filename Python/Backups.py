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
    flag = True     #bandera de control
    bk_failed = []  #arreglo para guardar los backups con tamaño menor a 10Mb
    command = "du -sb " + path
    res = subprocess.check_output(command, shell=True, universal_newlines=True)     #resultado de la ejecución de "du -sb /sapbackups/backups/instancia/*"

    #For para iterar entre cada una de las lineas de la variable res, para buscar los archivos que su tamaño sea menor a 10Mb
    for line in res.splitlines():
        size, file = line.split("\t")
        value = int(size)
        if value > 10 * 1024 *1024: # ¿El backup es mayor a 10Mb?
            flag = True
        else:
            flag = False
            archivo = subprocess.check_output("du -hs " + file,shell=True,universal_newlines=True) #Almacena en la variable archivo el nombre del archivo
            bk_failed.append(archivo.strip())       #Añade el contenido de la variable archivo al arreglo bk_failed
   
    #Condicional para mostrar el estado de los backups
    if flag:        #si el valor de flag es True, los backups estan correctos. sino imprime todos los archivos menores a 10Mb
        print ("El tamaño es correcto, Backups tomados correctamente")
    else:
        print("El tamaño del backup no es consistente")
        for archivo in bk_failed:
            print(archivo)

check_new_backups(path)
