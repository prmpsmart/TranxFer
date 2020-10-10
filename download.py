from tranxFer.src.tranxFer import autoDownload, TranxFerLogger
TranxFerLogger.setLevel('c')

d = 'zips'
# while True:
    # try: 
    # except Exception as e: print(e); continue
    # break
autoDownload(dest=d, ip='192.168.43.204')