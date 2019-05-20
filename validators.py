import subprocess
import os


def gzip_validator(file_path):
    cmd = "gunzip -t '{}'".format(file_path)
    p = subprocess.Popen(
        cmd, shell=True,
        stdout=open(os.devnull, 'w'),
        stderr=subprocess.PIPE
    )
    errcode = p.wait()
    if errcode:
        return False
    return True
