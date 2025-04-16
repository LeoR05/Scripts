import subprocess

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


path = "/sapbackups/NDB"
flag, con_backups, sin_backups = check_new_backups(path)
print("¿Existen nuevos backups?", flag)
print("Directorios con backups:", con_backups)
print("Directorios sin backups:", sin_backups)