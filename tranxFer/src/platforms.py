import os


def which_platform():
    android = 'ANDROID_DATA' in os.environ
    if android: return 'and'
    return os.name

def get_os_name():
    platf = which_platform()
    if platf == 'and': return 'Android'
    elif platf == 'nt': return 'Windows'

def python_version(): return os.sys.version_info[0]

py_ver = python_version()
# py_ver = 2

