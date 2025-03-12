import subprocess

path = "/sapbackups/backups/instancia"

def check_new_backups(path):
    command = "find " + path + " -type f -mtime -1 -exec ls -lh {} \\;"
    #command = "ls -l " + path
    r = subprocess.check_output(command, shell=True, universal_newlines=True)
    if r.strip():
        print(r)
    else:
        print("No se tomaron nuevos backups en las ultimas 24hrs")