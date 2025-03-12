import subprocess

path = "/sapbackups/backups/instancia/*"

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

check_size()
