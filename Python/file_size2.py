import subprocess

path = "/sapbackups/backups/instancia/*"

def check_size():
    command = "du * -sb " + path
    res = subprocess.check_output(command, shell=True, universal_newlines=True)

    for line in res.splitlines():
        size, file = line.split("\t")
        value = int(size)
        if value < 10 * 1024 *1024:
            print ("{}\t\t{}".format(file, size))
        else:
            print("No existen archivos nuevos")

check_size()
