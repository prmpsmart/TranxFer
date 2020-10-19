import argparse
from .tranxFer import autoDownload, autoUpload
from .tranxFerGui import FileTranxFer, GuiMixin
from .tranxFerGui import path as PATH
from .tranxFerLogger import TranxFerLogger

def tranxFerMain():
    parser = argparse.ArgumentParser(prog='TranxFer', description="TranxFer by PRMP Smart", epilog="By PRMP Smart < prmpsmart@gmail.com >")
    
    parser.add_argument("-A", "--address", type=str, dest="addr", help="address to connect to")
    parser.add_argument("-P", "--port", type=int, dest="port", help="port of the address")
    parser.add_argument("-v", "--version", action="version", version="TranxFer by PRMP Smart Version = 2.1.0")
    parser.add_argument("-l", "--log", nargs='*', choices=('i', 'e', 'd', 'c', 'w'), help='Log level. i=info, e=error, d=debug, c=critical, w=warning.')
    parser.add_argument("-c", "--compress", action="store_true", help="Compress before TranxFer")
    
    group1 = parser.add_mutually_exclusive_group()
    group1.add_argument("-p", "--path", type=str, dest="path", help="path to send")
    group1.add_argument("-s", "--save", type=str, dest="dest", help="destination to save the downloaded file")
    
    group2 = parser.add_mutually_exclusive_group()
    group2.add_argument("-U", "--upload", action="store_true", help="uploading")
    group2.add_argument("-D", "--download", action="store_true", help="downloading")
    group2.add_argument("-f", "--full", action="store_true", help="Full  File TranxFer")
    group2.add_argument("-m", "--mini", action="store_true", help="Mini File TranxFer")
    
    

    args = parser.parse_args()
    
    if args.path: assert PATH.exists(args.path)
    
    path = args.path
    addr = args.addr
    port = args.port
    compress = args.compress
    dest = args.dest
    download = args.download
    upload = args.upload
    
    port = port if port else 7767
    dest = dest if dest else ''
    
    full = args.full
    mini = args.mini
    
    log = TranxFerLogger._log.get(args.log[0]) if args.log else None
    TranxFerLogger.setLevel(log)
    args.log = TranxFerLogger.getLevel()
    
    if ((upload == False) and (download == False) and (full == False) and (mini == False)): args.full = full = True
    
    result = str(args).replace('Namespace', 'TranxFer') + '\n'
    print(result)
    
    if full or mini:
        GuiMixin._path = path or dest
        GuiMixin._port = port
        GuiMixin._server = addr
        GuiMixin._compress = compress
        if mini: FileTranxFer(0)
        else: FileTranxFer()
    
    else:
        if download:
            if addr: autoDownload(dest=dest, ip=addr, port=port)
            else: TranxFerLogger.error('Address to connect to is missing -a')
        
        elif upload:
            if path: autoUpload(path, port=port, compress=compress)
            else: TranxFerLogger.error('Path to send is missing -f')


