import subprocess
import smtplib
from email.mime.text import MIMEText

#-----------Constants---------------------------------
Client = "Celeren"
#path = "/sapbackups/backups/instancia"
path = "/sapbackups/NDB"
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
        print("Error al enviar el correo " + str(error))
#-----------------------------------------------------------------------
def check_new_backups(path):
    with_backups = []  # Lista para los directorios con backups
    no_backups = []        # Lista para los directorios sin backups
    try:
        # Obtener los subdirectorios dentro de "path"
        command = "find " + path + " -mindepth 1 -maxdepth 1 -type d"
        dir = subprocess.check_output(command, shell=True, universal_newlines=True).strip().split("\n")
        if not dir or dir == [""]:
            #write_log("ERROR: No hay subdirectorios en " + path)
            return False, [], []
        # Iterar sobre cada subdirectorio
        for subdir in dir:
            command = "find " + subdir + " -type f -mtime -1"
            r = subprocess.check_output(command, shell=True, universal_newlines=True).strip()
            if r:
                #write_log("INFO: Existen nuevos backups en " + directory)
                with_backups.append(subdir)
            else:
                #write_log("ERROR: No se tomaron backups en " + directory)
                no_backups.append(subdir)
        # Devolver listas con los directorios que tienen/no tienen backups
        return bool(with_backups), with_backups, no_backups
    except subprocess.CalledProcessError as e:
        #write_log("ERROR: Fallo en la ejecución del comando: " + str(e))
        return False, [], []
#-----------------------------------------------------------------------    
def check_size(subdir):
    flag2 = True  # Asumimos que todos los backups son correctos
    bk_failed = []  # Lista para guardar los backups incorrectos

    command = "find " + subdir + "/*" + " -type f -mtime -1 -exec du -sb {} \\;"
    res = subprocess.check_output(command, shell=True, universal_newlines=True)

    for line in res.splitlines():
        size, file = line.split("\t")
        value = int(size)

        if value < bk_size:  # Si el tamaño es menor a 10MB, es incorrecto
            flag2 = False  # Indicamos que hay backups incorrectos
            archivo = subprocess.check_output("du -hs " + file, shell=True, universal_newlines=True).strip()
            bk_failed.append(archivo)

    if bk_failed:  # Si hay archivos con tamaño incorrecto
        write_log("ALERT: El tamaño de algunos backups no es consistente")
        print("El tamaño de algunos backups no es consistente")
    else:
        write_log("INFO: Todos los backups tienen el tamaño correcto")
        print("Todos los backups tienen el tamaño correcto")

    archivo = "\n".join(bk_failed)  # Lista de archivos incorrectos
    return flag2, archivo

#-----------------------MAIN-------------------------------------
#----------------------------------------------------------------
write_log("\t" + "Script en ejecución...")
err_backup = []
ok_backup = []

flag, with_backup, no_backup = check_new_backups(path)

if flag:  # ¿Existen nuevos backups?
    for subdir in with_backup:  # Iteramos por los directorios con backups nuevos
        flag2, archivo = check_size(subdir)  # Validamos tamaño de los archivos
        if flag2:  # Si flag2 es True, significa que el tamaño fue correcto
            ok_backup.append(archivo)
        else:  # Si flag2 es False, significa que hubo backups con tamaño incorrecto
            err_backup.append(archivo)
    
    contenido = "" #Variable para el mensaje de correo
    if not err_backup and not no_backup: # pregunta ¿las listas err y no_backup estan vacios?
        contenido = "Backups Correctos"  # Todos los backups son correctos, por que no hay errores y no hay paths que no tengan backups
    elif not err_backup: #¿la lista err backup está vacio? 
        contenido = "No se tomaron backups en:\n" + "\n".join(map(str, no_backup))  # Si, si err_backup está vacio quiere decir que hay directorio donde no se tomaron backups
    elif not no_backup: #¿la lista no_backup está vació?
        contenido = "El tamaño de los backups no es correcto en:\n" + "\n".join(map(str, err_backup))  # Si, si no_backuu está vacio quiere decir que existen backups nuevos pero err_backup no esta vacio, entonces hay backups con errores.
    else:       #hay los dos problemas a la vez, backups de tamaño incorrecto y no hay backups recientes
        contenido = (
            "El tamaño de los backups no es correcto en:\n" + "\n".join(map(str, err_backup)) + "\n\n" +
            "No se tomaron backups en:\n" + "\n".join(map(str, no_backup))
        )  # asignamos el contenido con al información de ambos problemas

    #prueba para validar que se estáa imprimiendo
    print("Contenido del correo:\n", contenido)
    send_mail(contenido)
else:
    contenido = "No se tomaron backups en:\n" + "\n".join(map(str, no_backup))  # No se tomaron backups
    print("Contenido del correo:\n", contenido)
    send_mail(contenido)

write_log("\t" + "...ejecución del script finalizada")