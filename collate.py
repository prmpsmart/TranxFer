
__author__ = 'PRMP Smart'
__email1__ = "prmpsmart@gmail.com"
__email2__ = "rockymiracy@gmail.com"
from inspect import getsource
from pprint import pformat
from shutil import copy2
from os import remove

from tranxFer.src.tranxFerMain import tranxFerMain
from tranxFer.src.tranxFer import *
from tranxFer.src.pathstats import *
from tranxFer.src.platforms import *
from tranxFer.src.tranxFerGui import *
from tranxFer.src.network import *

globals_ = globals()

all_ = ['which_platform', 'get_os_name', 'python_version', 'zipPath', 'TranxFerLogger', 'Mixin', 'NetworkMixin', 'PathStat', 'LocalPathStat', 'RemotePathStat', 'TranxFer', 'AutoUploadHandler', 'AutoUploadServer', 'Server', 'Client', 'connectedTranxFer', 'autoDownload', 'autoUpload', 'continuousDownload', 'Transmission', 'AndroidInterfaceInfo', 'AndroidNetworkInfo', 'WindowsNetworkInfo', 'family', 'font2', 'font1', 'font0', 'compStr', 'show', 'showPath', 'confirm', 'Tip', 'Preview', 'Details', 'GuiMixin', 'MiniFileTranxFer', 'FullFileTranxFer', 'FileTranxFer', 'tranxFerMain']


imports = '''import argparse, subprocess, os, sys, time, socket, threading, logging
from datetime import datetime, timedelta
from json import dumps, loads
from os import path, walk, stat, getcwd, remove, makedirs
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import os
from socketserver import BaseRequestHandler, TCPServer
from tkinter import messagebox, filedialog, Tk, Label, LabelFrame, Button, Checkbutton, Frame, Entry, StringVar, Toplevel, Message, Toplevel, Text
from tkinter.ttk import Style, Progressbar
from PIL.ImageTk import PhotoImage, Image
PATH = path

'''

last = """main = tranxFerMain\n\nif __name__ == "__main__": tranxFerMain()"""


file_all = r'C:\Users\Administrator\Coding_Projects\PYTHON\Networking\compile\file\tranxFer.py'

def collate():
    with open(file_all, 'w') as file:
        file.write(imports+'\n\n')
        for val in all_:
            object_ = globals_[val]
            
            if type(object_) == str:
                r = ''
                if '\\' in object_: r = 'r'
                file.write(f'{val} = {r}"{object_}"\n')
            elif type(object_) == bytes:
                file.write(f'{val} = b"{object_}"\n')
            elif type(object_) == list or type(object_) == dict:
                dict_ = pformat(object_)
                file.write(f'{val} = {dict_}\n')
            elif type(object_) == bool: file.write(f'{val} = {object_}\n')
            else:
                source = getsource(object_)
                file.write(source + '\n\n')
        file.write(last+'\n'*3)

file_re = r'C:\Users\Administrator\Documents\My\PRMP Smart exes\TranxFer\tranxFer.py'
def copytoprmpsmartexes():
    try: remove(file_re)
    except: pass
    copy2(file_all, file_re)

collate()
copytoprmpsmartexes()
