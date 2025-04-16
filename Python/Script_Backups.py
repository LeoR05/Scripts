import subprocess
import smtplib
from email.mime.text import MIMEText

#-----------Constants---------------------------------
Client = "Celeren"
path_instancia = "/sapbackups/backups/instancia"
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
                #write_log("INFO: Existen nuevos backups en " + subdir)
                with_backups.append(subdir)
            else:
                #rite_log("ERROR: No se tomaron backups en " + subdir)
                no_backups.append(subdir)
        # Devolver listas con los directorios que tienen/no tienen backups
        return bool(with_backups), with_backups, no_backups
    except subprocess.CalledProcessError as e:
        write_log("ERROR: Falló en la ejecución del comando: " + str(e))
        return False, [], []
#----------------------------------------------------------------------- 
def check_new_backups_Instancia(path):
    flag = True
    command = "find " + path + " -type f -mtime -1 -exec ls -lh {} \\;"
    r = subprocess.check_output(command, shell=True, universal_newlines=True)
    if r.strip():
        #write_log("INFO: Existen nuevos backups")
        flag = True
        return flag,r
    else:
        #write_log("ERROR: No se tomaron backups")
        flag = False
        return flag,r
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
        #write_log("ALERT: El tamaño de algunos backups no es consistente")
        print("El tamaño de algunos backups no es consistente")
    else:
        #write_log("INFO: Todos los backups tienen el tamaño correcto")
        print("Todos los backups tienen el tamaño correcto")

    archivo = "\n".join(bk_failed)  # Lista de archivos incorrectos
    return flag2, archivo


#-----------------------MAIN-------------------------------------
#----------------------------------------------------------------
write_log("\t" + "Script en ejecución...")
err_backup = []
ok_backup = []
contenido_instancia = "" #Variable para el mensaje de correo
contenido_schema = "" #Variable para el mensaje de correo

#BACKUP SCHEMA------------------------------------------------
flag, with_backup, no_backup = check_new_backups(path)
if flag:  # ¿Existen nuevos backups?
    for subdir in with_backup:  # Iteramos por los directorios con backups nuevos
        flag2, archivo = check_size(subdir)  # Validamos tamaño de los archivos
        if flag2:  # Si flag2 es True, significa que el tamaño fue correcto
            ok_backup.append(archivo)
        else:  # Si flag2 es False, significa que hubo backups con tamaño incorrecto
            err_backup.append(archivo)

    if not err_backup and not no_backup: # pregunta ¿las listas err y no_backup estan vacios?
        contenido_schema = "Backups de Schema Correctos"  # Todos los backups son correctos, por que no hay errores y no hay paths que no tengan backups
    elif not err_backup: #¿la lista err backup está vacio? 
        contenido_schema = "No se tomaron backups de schema en:\n" + "\n".join(map(str, no_backup))  # Si, si err_backup está vacio quiere decir que hay directorio donde no se tomaron backups
        write_log("ERROR: No se tomaron backups de schema en:\n" + "\n".join(map(str, no_backup)))
    elif not no_backup: #¿la lista no_backup está vació?
        contenido_schema = "El tamaño del backup de schema no es correcto en:\n" + "\n".join(map(str, err_backup))  # Si, si no_backuu está vacio quiere decir que existen backups nuevos pero err_backup no esta vacio, entonces hay backups con errores.
        write_log("ALERT: El tamaño del backup de schema no es correcto en:\n" + "\n".join(map(str, err_backup)))
    else:       #hay los dos problemas a la vez, backups de tamaño incorrecto y no hay backups recientes
        contenido_schema = (
            "El tamaño del backup de schema no es correcto en:\n" + "\n".join(map(str, err_backup)) + "\n\n" +
            "No se tomaron backups de schema en:\n" + "\n".join(map(str, no_backup))
        )  # asignamos el contenido con al información de ambos problemas
        write_log(
            "ALERT: El tamaño del backup de schema no es correcto en:\n" + "\n".join(map(str, err_backup)) + "\n\n" +
            "ERROR: No se tomaron backups de schema en:\n" + "\n".join(map(str, no_backup))
        )
    #prueba para validar que se estáa imprimiendo
    print("Contenido del correo:\n", contenido_schema)
else:
    contenido_schema = "No se tomaron backups de schema en:\n" + "\n".join(map(str, no_backup))  # No se tomaron backups
    write_log("ERROR: No se tomaron backups de schema en:\n" + "\n".join(map(str, no_backup)))
    print("Contenido del correo:\n", contenido_schema)


#BACKUP INSTANCIA------------------------------------------------
flag,r= check_new_backups_Instancia(path_instancia)
if flag:    #la bandera de nuevo backups indica que existen nuevos backups?
    flag2,archivo = check_size(path_instancia)    #si?, entonces obtengo el valor del flag y los archivos para validar su tamaño
    if flag2: #la bandera del tamaño de los backups es verdadera?
        contenido_instancia = "Backups de Instancia Correctos"
        write_log("INFO: Backups de Instancia Correctos")
        print ("Backups de Instancia Correctos")    
    else:   #si no es, guarda en una variable los archivos que no cumplen con el tamaño y los manda por correo.
        contenido_instancia = "El tamaño del backup de instancia no es correcto" + "\n" + archivo
        write_log("ALERT: El tamaño de los backups de instancia no es correcto" + "\n" + archivo)
        #send_mail(contenido)  
else:
    contenido_instancia = "No se tomaron backups de instancia en:\n" + path_instancia
    write_log("ERROR: No se tomaron backups de instancia en:\n" + path_instancia)
    #send_mail(contenido)
send_mail("BACKUPS DE SHCEMA \n" + contenido_schema + "\n\n" +"BACKUPS DE INSTANCIA \n" +contenido_instancia)

write_log("\t" + "...ejecución del script finalizada")