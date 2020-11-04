from tranxFer.src.tranxFer import autoDownload, TranxFerLogger
TranxFerLogger.setLevel('c')

d = 'zips'

autoDownload(dest=d, ip='192.168.43.1')
