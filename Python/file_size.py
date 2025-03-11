import subprocess

def size(path):
    try:
        # Usamos format() para insertar la variable 'path' en el comando
        comando = "du -hs {}/{}".format(path, "*")  # Inserta 'path' en el comando
        resultado = subprocess.check_output(comando, shell=True, universal_newlines=True)  # Usar universal_newlines en lugar de text
        print("Este es el espacio en {}:\n".format(path))  # Usamos format() en el mensaje
        print(resultado)

    except subprocess.CalledProcessError as Err:
        print("Error al ejecutar el comando: {}".format(Err))  # Usamos format() para mostrar el error

path = "/sapbackups/backups"
size(path)
