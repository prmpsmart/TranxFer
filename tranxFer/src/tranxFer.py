from .tranxFerLogger import TranxFerLogger
try: from socketserver import BaseRequestHandler, TCPServer
except ImportError:
    TranxFerLogger.debug('socketserver not installed, I percieve you\'re using python2')
    from SocketServer import BaseRequestHandler, TCPServer
import socket, threading, sys, time, os

from .pathstats import LocalPathStat, Mixin, RemotePathStat, path
from .platforms import get_os_name, which_platform, python_version
from .network import NetworkMixin

class TranxFer(NetworkMixin):
    
    dn = b'<download>'
    up = b'<upload>'
    tranx = b'<pathstats>'
    st = b'<start>'
    stdir = b'<startDir>'
    spdir = b'<stopDir>'
    sp = b'<stop>'
    end = b'timilehin08085200646prmpsmart'
    
    def __init__(self, connection, path=None, which='upload', dest='', goOn=True):
        
        if path:
            self.dest = ''
            assert isinstance(path, LocalPathStat)
        else: self.dest = dest
        
        self.__socket = connection
        self.rawWhich = which
        
        if python_version() == 2: self.which = b'<' + which.encode() + b'>'
        elif python_version() == 3: self.which = ('<%s>'%which).encode()
        
        self.goOn = goOn
        
        self.path = path if (path and path.isFile) else None
        self.dirPath = path if (path and path.isDir) else None
        
        if self.dirPath and self.dirPath.compress: self.dirPath, self.path = self.path, self.dirPath
        
        self.isRemote = True if path == None else True
        
        self.onGoing = False
        self.startedReceiving = False
        self.finished = False
        
        self.tranxFered = 0
        self.tranxFeredBytes = 0
        
        self.wait = False
        self.recvDir = False
        self.finishedDir = False
        
        self.tranxFeredDetails = False
        
        self.r10 = False
        self.r20 = False
        self.r30 = False
        self.r40 = False
        self.r50 = False
        self.r60 = False
        self.r70 = False
        self.r80 = False
        self.r90 = False
        self.r100 = False
    
    def __str__(self): return 'TranxFer %s'%self.which.decode()
    
    @property
    def details(self):
        path = self.dirPath if self.dirPath else self.path
        dets = self.tranx + path.bytesDicts + self.tranx
        print(dets)
        return dets
    
    @property
    def tranxFeredPercent(self): return '{} %'.format(self.decimalPlace(self.tranxFered))
    
    def notify(self):
        if self.tranxFered <= 10:
            if not self.r10:
                self.r10 = True
                TranxFerLogger.info('TranxFered 10 %')
        elif self.tranxFered <= 20:
            if not self.r20:
                self.r20 = True
                TranxFerLogger.info('TranxFered 20 %')
        elif self.tranxFered <= 30:
            if not self.r30:
                self.r30 = True
                TranxFerLogger.info('TranxFered 30 %')
        elif self.tranxFered <= 40:
            if not self.r40:
                self.r40 = True
                TranxFerLogger.info('TranxFered 40 %')
        elif self.tranxFered <= 50:
            if not self.r50:
                self.r50 = True
                TranxFerLogger.info('TranxFered 50 %')
        elif self.tranxFered <= 60:
            if not self.r60:
                self.r60 = True
                TranxFerLogger.info('TranxFered 60 %')
        elif self.tranxFered <= 70:
            if not self.r70:
                self.r70 = True
                TranxFerLogger.info('TranxFered 70 %')
        elif self.tranxFered <= 80:
            if not self.r80:
                self.r80 = True
                TranxFerLogger.info('TranxFered 80 %')
        elif self.tranxFered <= 90:
            if not self.r90:
                self.r90 = True
                TranxFerLogger.info('TranxFered 90 %')
        elif self.tranxFered <= 100:
            if not self.r100:
                self.r100 = True
                TranxFerLogger.info('TranxFered 100 %')
    
    def setTranxFered(self):
        path = self.dirPath if self.dirPath else self.path
        self.tranxFered = self.tranxFeredBytes / path.innerSize * 100
        self.notify()
        
    def stripDets(self, dets): return dets.replace(self.tranx, b'')
    
    def parseDetails(self, dets):
        det = self.stripDets(dets).decode()
        try:
            path = RemotePathStat(det, dest=self.dest)
        
            if path.isDir: self.dirPath = path
            else: self.path = path
            
            return path.isFile
        
        except Exception as er:
            TranxFerLogger.debug('Details %s is not parseable.\nError( %s )'%(str(dets), str(er)))
            raise er

    def sendDetails(self):
        TranxFerLogger.info('Started Sending Details')
        self.socket.send(self.details)
        self.tranxFeredDetails = True
    
        # if self.dirPath: self.socket.send(self.dt)
        TranxFerLogger.info('Ended Sending Details')
    
    def receiveDetails(self, dets):
        TranxFerLogger.info('Started Receiving Details')
        
        file = self.parseDetails(dets)
        
        TranxFerLogger.info('Ended Receiving Details')
        
        self.tranxFeredDetails = True
        
        if self.goOn:
            if file == True: self.startFileReceiving()
            elif file == False: self.startDirReceiving()
        else: self.wait = True
    
    def startFileReceiving(self):
        self.startedReceiving = self.goOn = True
        self.socket.send(self.st)
        self.receiveFileTranxFer()
    
    def startDirReceiving(self):
        self.startedReceiving = self.goOn = True
        self.socket.send(self.stdir)
        # self.receiveDirTranxFer()
    
    def sendFileTranxFer(self):
        TranxFerLogger.info('Started Sending TranxFer %s'%str(self.path))
        
        self.path.open()
        size = self.path.size
        u = 0
        
        while True:
            if u == size or size == 0:
                self.finalize()
                break
            
            elif u <= size+2:
                read = self.path.read(3000)
                if read == None: break
                self.socket.send(read)
                u += len(read)
                self.tranxFeredBytes += len(read)
                self.setTranxFered()

        TranxFerLogger.info('Ended Sending TranxFer')
        self.close()
    
    def testRawRead(self, rawRead):
        if self.dn in rawRead: print('dn')
        if self.up in rawRead: print('up')
        if self.tranx in rawRead: print('tranx')
        if self.st in rawRead: print('st')
        if self.stdir in rawRead: print('stdir')
        if self.spdir in rawRead: print('spdir')
        if self.end in rawRead: print('end')
    
    def receiveFileTranxFer(self):
        TranxFerLogger.info('Started Receiving TranxFer %s'%str(self.path))
        size = self.path.size
        self.path.open('wb')
        
        u = 0
        while True:
            if size == 0: break
            rawRead = self.socket.recv(3000)
            
            # self.testRawRead(rawRead)
            
            reads = rawRead.split(self.end)
            read = reads[0]
            written = self.path.write(read)
            if written == None:
                TranxFerLogger.error('Nothing is written, so exiting.')
                break
            u += len(read)
            self.tranxFeredBytes += len(read)
            self.setTranxFered()
            
            if len(reads) > 1:
                # self.socket.send(self.sp)
                self.setTranxFered()
                break
        TranxFerLogger.info('Ended Receiving TranxFer %s'%str(self.path))
        self.path.close()
        self.close()
    
    def sendDirTranxFer(self):
        tranx = None
        files = self.dirPath.filesList
        
        for file in files:
            tranx =  self.__class__(self.socket, file, which=self.rawWhich, dest=self.dest, goOn=self.goOn)
            tranx.startTranxFer()
            
            # time.sleep(5)
        
        self.socket.send(self.spdir)
        self.finishedDir = True
    
    def receiveDirTranxFer(self):
        # tranx = None
        files = self.dirPath.filesCount
        
        for file in range(files):
            self.__class__(self.socket, which=self.rawWhich, dest=self.dest, goOn=self.goOn).startTranxFer()
            
            # time.sleep(4)
        # self.socket.send(self.up)
        # return
        # self.parseFromSocket()
        self.finishedDir = True
        self.socket.send(self.spdir)
    
    def readFromSocket(self):
        try: return self.socket.recv(3000) 
        except OSError as error:
            TranxFerLogger.error(error)
            return False
    
    def parseFromSocket(self):
        recv = self.readFromSocket()
        if isinstance(recv, bytes):
            # print(recv)
            if recv == self.dn: self.socket.send(self.up)
            elif recv == self.up: self.sendDetails()
            elif self.tranx in recv: self.receiveDetails(recv)
            elif recv == self.st: self.sendFileTranxFer()
            # elif recv == self.sp: TranxFerLogger.info('Stopped File')
            
            
            elif recv == self.stdir:
                self.recvDir = True
                self.sendDirTranxFer()
            
            elif recv == self.spdir:
                self.finishedDir = True
                TranxFerLogger.info('Stopped Dir')
            
            
            return True
        
        elif recv == False: return False
        
        return False
    
    
    def startTranxFer(self):
        self.onGoing = True
        if self.which in [self.up, self.dn]:
            up = self.which == self.up
            wh = 'Send' if up else 'Receive'
            trwh = 'Uploading' if up else 'Downloading'
            
            fn = str(self.dirPath) if self.dirPath else str(self.path)
            
            TranxFerLogger.info(trwh)
            TranxFerLogger.info('Started %s TranxFer (%s)'%(wh, fn))

            try:
                if up: self.socket.send(self.dn)
                while True:
                    if self.dirPath:
                        if self.finishedDir:
                            TranxFerLogger.info('Finished Dir')
                            break

                    else:
                        if self.finished:
                            TranxFerLogger.info('Finished File')
                            break
                        
                    if self.wait:
                        TranxFerLogger.info('Waiting')
                        break
                    y = self.parseFromSocket()
                    if y == False:
                        TranxFerLogger.critical('parsing from socket error')
                        break
                    
                fn = str(self.dirPath) if self.dirPath else str(self.path)
                TranxFerLogger.info('Ended %s TranxFer (%s)'%(wh, fn))
            except Exception as error: TranxFerLogger.error(error)
        else: raise ValueError('which should be %s or %s'%(self.up.decode(), self.dn.decode()))
    
    def startThreadedTranxFer(self): threading.Thread(target=self.startTranxFer).start()
    
    def startThreadedReceiving(self): threading.Thread(target=self.startReceiving).start()

    def finalize(self):
        self.socket.send(self.end)
        self.setTranxFered()
        self.path.close()
        self.path.delete()

    def close(self):
        self.startedReceiving = self.onGoing = False
        self.setTranxFered()
        TranxFerLogger.info('Stopped File')
        TranxFerLogger.info('Closing TranxFer')
        self.finished = True
    
    @property
    def socket(self): return self.__socket
    
    def setPath(self, path_):
        assert path.exists(path_)
        self.path = path_
    
    def shutdown(self):
        if self.socket: self.socket.shutdown(socket.SHUT_WR)


class AutoUploadHandler(BaseRequestHandler):
    
    path = ''
    compress = False
    count = 0
    
    @classmethod
    def setPath(cls, path_):
        assert path.exists(path_)
        cls.path = path_
        cls.count = 0
    @classmethod
    def setCompress(cls, comp): cls.compress = comp
    
    def setup(self):
        TranxFerLogger.info('Client Connected')
        self.tranxfer = None
        
    def finish(self):
        if self.tranxfer: self.tranxfer.close()
        self.request.shutdown(socket.SHUT_WR)
        AutoUploadHandler.count += 1
        
    def handle(self):
        # print(TranxFerLogger.cmd)
        self.tranxFer = None
        assert self.path != ''
        self.tranxfer = TranxFer(self.request, LocalPathStat(self.path, latest=True, compress=self.compress))
        self.tranxfer.startTranxFer()
        # self.finishIt()

class AutoUploadServer(TCPServer, NetworkMixin):
    allow_reuse_address = True
    
    def __init__(self, addr='', port=7767, handler=None, start=False):
        Handler = AutoUploadHandler if handler == None else handler
        TCPServer.__init__(self, (addr, port), Handler)
        
        TranxFerLogger.info('Serving on %s : %d ' % (self.getNetwork().ip or self.lh, port))
        if start: self.start()
        
    def start(self): threading.Thread(target=self.serve_forever).start()

class Server(NetworkMixin):
    
    def __init__(self, port, hs=False):
        self.port = port
        self.socket = socket.socket()
        self.socket.bind(('', port))
        threading.Thread(target=self.acceptClient).start()
        
        self.hs = hs
        self.client = None
        
    @property
    def communicableSocket(self): return self.client
        
    def check(self):
        try:
            if self.client:
                self.client.send(b'')
                self.connected = True
            else: self.connected = False
        except Exception as er:
            self.connected = False
        
    def acceptClient(self):
        try:
            self.socket.listen(1)
            self.client, self.clientIp = self.socket.accept()
            if self.hs: self.handShake()
            else: self.check()
        except OSError as error: TranxFerLogger.debug(error)
    
    def recv(self, num=3000): return self.client.recv(num)
    
    def send(self, byts): self.client.send(byts)
    
    def handShake(self):
        hs = b''
        while True:
            hs += self.client.recv(15)
            if hs == self.conned:
                self.client.send(self.yes)
                self.connected = True
                break
    
    def shutdownClient(self):
        """Called to shutdown and close an individual client."""
        try:
            if self.client: self.client.shutdown(socket.SHUT_WR)
        except OSError as error: TranxFerLogger.debug(error)
        self.closeClient()

    def shutdown(self):
        try:
            if self.client: self.shutdownClient()
            self.socket.shutdown(socket.SHUT_WR)
            
        except OSError as error: TranxFerLogger.debug(error)
        self.close()

    def closeClient(self):
        if self.client: self.client.close()
    
    def close(self):
        if self.socket: self.socket.close()

class Client(NetworkMixin):
    def __init__(self, addr, port, hs=False):
        self.addr, self.port = addr, port
        self.socket = socket.socket()
        self.hs = hs
        threading.Thread(target=self.connect).start()
    
    @property
    def communicableSocket(self): return self.socket
    
    def connect(self):
        try:
            self.socket.connect((self.addr, self.port))
            if self.hs: self.handShake()
            else: self.check()
        except Exception as error:
            self.error = error
            TranxFerLogger.debug(error)
    
    def shutdown(self):
        try: self.socket.shutdown(socket.SHUT_WR)
        except OSError as error: TranxFerLogger.debug(error)
        self.close()

    def close(self):
        self.socket.close()
        self.connected = False
    
    def recv(self, num=3000): 
        try: return self.socket.recv(num)
        except Exception as error: TranxFerLogger.error(error)
    
    def send(self, byts): self.socket.send(byts)
    
    def check(self):
        try:
            if self.socket:
                self.socket.send(b'')
                self.connected = True
            else: self.connected = False
        except Exception as er:
            self.connected = False
            TranxFerLogger.debug(er)
        
    def handShake(self):
        hs = b''
        first = time.time()
        self.socket.send(self.conned)
        
        while True:
            second = time.time()
            try: hs += self.recv(5)
            except: hs += b''
            if hs == self.yes:
                self.connected = True
                break
            elif (second - first) >= 3:
                self.connected = False
                break

def connectedTranxFer(dest='', which='download', ip='localhost', port=7767, goOn=False):
    soc = socket.socket()
    soc.connect((ip, port))
    tranxFer = TranxFer(soc, which='download', dest=dest, goOn=goOn)
    return tranxFer

def autoUpload(path, ip='', port=7767, compress=True):
    AutoUploadHandler.setPath(path)
    AutoUploadHandler.setCompress(compress)
    
    AutoUploadServer(start=True)

def autoDownload(dest='', ip='localhost', port=7767): connectedTranxFer(dest=dest, ip=ip, port=port, goOn=True, which='download').startTranxFer()

def continuousDownload(dest='', ip='localhost', port=7767):
    while True: autoDownload(dest=dest, ip=ip, port=port)

