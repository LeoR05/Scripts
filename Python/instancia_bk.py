import subprocess
import smtplib
from email.mime.text import MIMEText

#-----------Constants---------------------------------
Client = "Celeren"
path = "/sapbackups/backups/instancia"
path_log = "/sapbackups/backups/backup.log"
bk_size = 10 * 1024 * 1024      # en MB


#----------Mail config---------------------
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
EMAIL_SENDER = "rspalerta@celeren.com"
EMAIL_PASSWORD = "qscxhzzdcmlflfcj"
EMAIL_RECEIVER = "leonardo.rojas@celeren.com"

#----------FUNCTIONS-------------------------------------------------
def write_log(msj):
    time = subprocess.check_output("date '+[%d-%m-%Y %H:%M:%S]'", shell=True, universal_newlines=True).strip()
    with open (path_log,"a") as log_file:
            log_file.write( time + " " + msj + "\n")
#-----------------------------------------------------------------------
def send_mail(contenido):
    try:
        subject = "Alerta de Backups en " + Client
        body = contenido
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = EMAIL_SENDER
        msg["To"] = EMAIL_RECEIVER
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER,EMAIL_RECEIVER, msg.as_string())
        write_log("INFO: Correo de alerta enviado correctamente")
        print("Correo de alerta enviado correctamente")       
    except Exception as error:
        print("Error al enviar el correo " + error)
#-----------------------------------------------------------------------
def check_new_backups(path):
    flag = True
    command = "find " + path + " -type f -mtime -1 -exec ls -lh {} \\;"
    r = subprocess.check_output(command, shell=True, universal_newlines=True)
    if r.strip():
        write_log("INFO: Existen nuevos backups")
        flag = True
        return flag,r
    else:
        write_log("ERROR: No se tomaron backups")
        flag = False
        return flag,r
#-----------------------------------------------------------------------    
def check_size():
    flag2 = True        #bandera de control
    bk_failed = []      #arreglo para guardar los backups con tamaño menor a 10Mb
    command = "find " + path + "/*" + " -type f -mtime -1 -exec du -sb {} \\;"
    res = subprocess.check_output(command, shell=True, universal_newlines=True)     #resultado de la ejecución de "du -sb /sapbackups/backups/instancia/*"
    #For para iterar entre cada una de las lineas de la variable res, para buscar los archivos que su tamaño sea menor a 10Mb
    for line in res.splitlines():
        size, file = line.split("\t")
        value = int(size)
        if value > bk_size: # ¿El backup es mayor a 10Mb?
            flag2 = True
        else:
            flag2 = False
            archivo = subprocess.check_output("du -hs " + file,shell=True,universal_newlines=True) #Almacena en la variable archivo el nombre del archivo
            bk_failed.append(archivo.strip())       #Añade el contenido de la variable archivo al arreglo bk_failed
    #Condicional para mostrar el estado de los backups
    if flag2:        #si el valor de flag es True, los backups estan correctos. sino imprime todos los archivos menores a 10Mb
        write_log("INFO: El tamaño de los backups es correcto")
        print ("El tamaño es correcto, Backups tomados correctamente")
    else:
        write_log("ALERT: El tamaño del backup no es consistente")
        print("El tamaño del backup no es consistente")
    archivo = "\n".join(bk_failed)
    return flag2,archivo

#-----------------------MAIN-------------------------------------
#----------------------------------------------------------------

write_log ("\t" + "Script en ejecución...")
flag,r = check_new_backups(path)
if flag:    #la bandera de nuevo backups indica que existen nuevos backups?
    flag2,archivo = check_size()    #si?, entonces obtengo el valor del flag y los archivos para validar su tamaño
    if flag2: #la bandera del tamaño de los backups es verdadera?
        print ("Backups Correctos")    
        print ("Ta to' bien papito") 
    else:   #si no es, guarda en una variable los archivos que no cumplen con el tamaño y los manda por correo.
        contenido = "El tamaño de los backups no es correcto" + "\n\n" + archivo
        send_mail(contenido)  
else:
    contenido = "No se tomaron backups en:\n" + path
    send_mail(contenido)
write_log("\t" + "...ejecución del script finalizada")