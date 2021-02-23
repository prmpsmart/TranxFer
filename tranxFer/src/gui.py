from prmp_gui import *
from prmp_gui.dialogs import *
from .core import *

def show(title=None, msg=None, which='info', **kwargs):
    if which == 'error':
        TranxFerLogger.error(msg)
        title = title or which.title()
    elif which == 'info':
        TranxFerLogger.info(msg)
        title = title or 'Information'
    elif which == 'warn':
        TranxFerLogger.warning(msg)
        title = title or 'Warning'

    dialogFunc(title=title, msg=msg, which=which, **kwargs)

def confirm(msg='', **kwargs):
    TranxFerLogger.info(msg)
    return dialogFunc(ask=1, msg=msg, **kwargs)


class Preview(Toplevel):
    images = ['.jpg', '.png', '.jpeg', '.gif', '.jpeg', '.jpg', '.png', '.PNG', '.psd', '.tif', '.tiff', '.ico']
    audios = ['.wav', '.aif', '.cda', '.mid', '.midi', '.mp3', '.mpa', '.ogg', '.wma']
    videos = ['.mp4', '.3gp', '.mkv', '.rm', '.wmv', '.mpeg']
    texts = ['.txt', '.rtf', '.py', '.bat', '.c', '.c++', '.cpp', '.pl', '.log', '.h', '.hpp']

    def __init__(self, master, pathStat):
        ext = pathStat.type
        file = pathStat.fullName

        if not pathStat.exists:
            er = f'Path ({file}) does not exists.'
            show('Invalid Path', er, 'error')
            return

        super().__init__(master)

        self.geometry('500x500')
        self.attributes('-topmost', 1)
        loadable = 0
        if ext in self.images: self.renderImage(file); loadable = 1
        elif ext in self.audios: self.renderAudio(file)
        elif ext in self.videos: self.renderVideo(file)
        elif ext in self.texts: self.renderText(file); loadable = 1

        if loadable: self.mainloop()
        else:
            self.destroy()
            show('Load error', 'Not Loadable Yet', 'error')

    def renderImage(self, file):
        self.image = Image.open(file)
        self.image = self.image.resize((500, 500))
        self.geometry('%dx%d'%(self.image.width, self.image.height))
        self.photo = PhotoImage(self.image)
        self.label = Label(self, image=self.photo)
        self.label.place(relx=0, rely=0, relh=1, relw=1)

    def renderAudio(self, file): pass
    def renderVideo(self, file): pass
    def renderText(self, file):
        self.txt = open(file).read()
        self.text = Text(self)
        self.text.insert('insert', self.txt)
        self.text.config(state='disabled')
        self.text.place(relx=0, rely=0, relh=1, relw=1)

class Details(LabelFrame):
    def __init__(self, master, which='s', main=None, **kw):

        root = master.master
        super().__init__(master, **kw)

        self.main = main
        self.which = which
        self.destPath = ''

        self.indicatorLbl = Label(self, place=dict(relx=.61, rely=0, relh=.1, relw=.1))

        self.actionBtn = Button(self,  text='Send' if which == 's' else 'Receive', command=self.send if which == 's' else self.receive, place=dict(relx=.781, rely=0, relh=.1, relw=.154))

        self.browseBtn = Button(self, text='Browse' if which == 's' else 'Remote Load', command=self.main.browse if which == 's' else self.remoteLoad, place=dict(relx=.015, rely=0, relh=.1, relw=.154 if which == 's' else .26))

        if which == 'r':
            self.destDir = Checkbutton(self, text='Destination?',  command=self.setDest, place=dict(relx=.313, rely=0, relw=.255, relh=.082))

        self.detConts = Frame(self, border="2", place=dict(relx=.01, rely=.114, relh=.868, relw=.981))

        self.which = which
        self.pathStat = None

        self.nameL = Button(self.detConts, text='Name', command=self.reload, place=dict(relx=.01, rely=.01, relh=.12, relw=.164))
        self.nameS = Label(self.detConts, text='File Name', place=dict(relx=.175, rely=.01, relh=.12, relw=.82), tip='None')

        self.sizeL = Label(self.detConts, text='Size', place=dict(relx=.01, rely=.14, relh=.12, relw=.164))
        self.sizeS = Label(self.detConts, place=dict(relx=.175, rely=.14, relh=.12, relw=.274), tip='None')

        self.typeL = Label(self.detConts, text='Type', place=dict(relx=.01, rely=.27, relh=.12, relw=.164))
        self.typeS = Label(self.detConts, place=dict(relx=.175, rely=.27, relh=.12, relw=.274), tip='None')

        self.ctimeL = Label(self.detConts, text='CTime', place=dict(relx=.01, rely=.4, relh=.12, relw=.164))
        self.ctimeS = Label(self.detConts,  place=dict(relx=.175, rely=.4, relh=.12, relw=.274), tip='None')

        self.atimeL = Label(self.detConts, text='ATime', place=dict(relx=.01, rely=.53, relh=.12, relw=.164))
        self.atimeS = Label(self.detConts,  place=dict(relx=.175, rely=.53, relh=.12, relw=.274), tip='None')

        self.mtimeL = Label(self.detConts, text='MTime', place=dict(relx=.01, rely=.66, relh=.12, relw=.164))
        self.mtimeS = Label(self.detConts, place=dict(relx=.175, rely=.66, relh=.12, relw=.274), tip='None')

        self.filesCountL = Label(self.detConts, text='Files Count', place=dict(relx=.47, rely=.14, relh=.12, relw=.329))
        self.filesCountS = Label(self.detConts, place=dict(relx=.8, rely=.14, relh=.12, relw=.194))

        self.dirsCountL = Label(self.detConts, text='Dirs Count', place=dict(relx=.47, rely=.27, relh=.12, relw=.329))
        self.dirsCountS = Label(self.detConts, place=dict(relx=.8, rely=.27, relh=.12, relw=.194))

        self.innerSizeL = Label(self.detConts, text='Inner Files Size', place=dict(relx=.47, rely=.4, relh=.12, relw=.329))
        self.innerSizeS = Label(self.detConts,  place=dict(relx=.8, rely=.4, relh=.12, relw=.194), tip='None')



        text = 'Compress?' if which == 's' else 'Decompress?'
        tip = 'Compress before sending (Good for Directories).' if which == 's' else 'Decompress after receiving (Good for Directories).'


        self.detailsL = Label(self.detConts, text='Details', place=dict(relx=.493, rely=.53, relh=.12, relw=.268))
        self.detailsS = Label(self.detConts, text='No', place=dict(relx=.78, rely=.53, relh=.12, relw=.205))

        self.compress = Checkbutton(self, text=text,  place=dict(relx=.493, rely=.69, relw=.268, relh=.1), tip=tip)

        self.previewBtn = Button(self, text='Preview', command=self.preview, place=dict(relx=.77, rely=.69, relh=.1, relw=.205))

        self.level = Progressbar(self, value="30", place=dict(relx=.02, rely=.82, relh=.14, relw=.75))

        self.percent = Label(self.detConts, text='100%', place=dict(relx=.78, rely=.82, relh=.14, relw=.22))

        self.tranxFer = None
        self.pathStat = None

        self.after(100, self.update)

    def preview(self): Preview(self.main.root, self.pathStat)

    def setDest(self):
        self.destPath = ''
        if self.destDir.get():
            p = dialogFunc(path=1, folder=1)
            if  PRMP_Mixins.checkPath(None, p): self.destPath = p
            else: show('Path Error', 'The choosen directory does not exists', 'warn')

    def setDetails(self):
        def setRed(): self.detailsS.config(text='No', bg='red')
        def setGreen(text): self.detailsS.config(text=text, bg='green')

        if self.tranxFer and self.tranxFer.tranxFeredDetails:
            if self.which == 'r': setGreen('Received')
            else: setGreen('Sent')
            if self.tranxFer.finished: setRed()
        else: setRed()

    def update(self):
        self.setDetails()
        self.setOnGoing()
        self.setProgress()
        self.after(100, self.update)

    def load(self, pathStat=None):
        if pathStat: self.pathStat = pathStat
        if self.pathStat:
            self.nameS.config(text=self.pathStat.name)
            self.nameS.tip.update(self.pathStat.fullName)

            self.sizeS.config(text=self.pathStat.fSize)
            self.sizeS.tip.update(self.pathStat.fullSize)

            self.typeS.config(text=self.pathStat.type)
            self.typeS.tip.update(self.pathStat.fullType)

            self.ctimeS.config(text=self.pathStat.cTime)
            self.ctimeS.tip.update(self.pathStat.fullCTime)

            self.atimeS.config(text=self.pathStat.aTime)
            self.atimeS.tip.update(self.pathStat.fullATime)

            self.mtimeS.config(text=self.pathStat.mTime)
            self.mtimeS.tip.update(self.pathStat.fullMTime)

            self.filesCountS.config(text=self.pathStat.filesCount)

            self.dirsCountS.config(text=self.pathStat.dirsCount)

            self.innerSizeS.config(text=self.pathStat.fInnerSize)
            self.innerSizeS.tip.update(self.pathStat.fullInnerSize)
        self.after(1000, self.load)

    def localLoad(self, path):
        if isinstance(path, str): pass
        else: path = os.path.get()

        pathStat = LocalPathStat(path)
        if pathStat.exists: self.load(pathStat)
        else: show('Loading Error', 'Path is invalid', 'error')

    def reload(self):
        try: self.localLoad()
        except: pass

    def remoteLoad(self):
        if self.main.checkConnected:
            self.tranxFer = TranxFer(self.main.connection, which='download', dest=self.destPath)
            self.tranxFer.startThreadedTranxFer()

            first = time.time()

            while True:
                second = time.time()
                pathStat = self.tranxFer.remotePath

                if pathStat:
                    self.load(pathStat)
                    break
                elif (second - first) >= 3:
                    show('Parsing Error', 'Remote load error.', 'error')
                    break

    def setOnGoing(self):
        def setOff(): self.indicatorLbl.config(text='Off', bg='red')
        if self.tranxFer and self.tranxFer.onGoing: self.indicatorLbl.config(text='On', bg='green')
        else:
            setOff()

    def setProgress(self):
        if self.tranxFer and not self.tranxFer.finished:
            self.percent.config(text=self.tranxFer.tranxFeredPercent)
            self.level.config(value=self.tranxFer.tranxFered)
        else:
            self.level.config(value=0)
            self.percent.config(text='0.00 %')
        # self.level.update()

    def send(self):
        if self.main.checkConnected:
            if self.main.checkPath():
                self.tranxFer = TranxFer(self.main.connection, LocalPathStat(self.main.path, compress=self.compress.get()))
                self.tranxFer.startThreadedTranxFer()

    def receive(self):
        if self.main.checkConnected:
            if self.tranxFer and self.tranxFer.startedReceiving:
                show('Error', 'A tranxFer is still on', 'error')
                return
            if self.tranxFer: self.tranxFer.startThreadedReceiving()
            else: show('TranxFer Error', 'Load remotely first to get the path details', 'warn')

class FileTranxFer(PRMP_MainWindow, NetworkMixin):
    _path = ''
    _server = ''
    _port = 7767
    _name = 'gui'
    geo = (600, 270)

    def __init__(self, master=None, geo=(), title="File TranxFer", tm=1, tw=1, side='center', **kwargs):
        PRMP_MainWindow.__init__(self, master, geo=geo or self.geo, title=title, side=side, tm=tm, tw=tw, **kwargs)

        self.path = ''
        self.networkInfo = None
        self.server = None
        self.client = None
        self.connecting = False
        self.networkOn = False

        self._setupApp()

        self.serverDefault()

        self.bind('<Control-M>', os.sys.exit)
        self.bind('<Control-m>', os.sys.exit)
        self.bind('<Control-n>', self.new)
        self.bind('<Control-N>', self.new)
        self.bind('<Control-a>', self.another)
        self.bind('<Control-A>', self.another)

        # self.protocol('WM_DELETE_WINDOW', self.exiting)

        self.defaults()
        self.paint()

        self.after(10, self.update)
        # self.after(100, self.tips)

        self.mainloop()

    def _setupApp(self):
        pass

    def defaults(self):
        self.path = self._path
        self.serverS.set(self._server or '')
        self.portS.set(self._port)

    def closing(self):
        try: self.stop(1)
        except Exception as error: TranxFerLogger.debug(error)
        os.sys.exit()

    def serverDefault(self): self.serverS.set('192.168.43.')

    def new(self, e=None):
        if self.name == 'mini': MiniFileTranxFer(self)
        elif self.name == 'full': FullFileTranxFer(self)

    def another(self, e=None):
        if self.name == 'full': MiniFileTranxFer(self)
        elif self.name == 'mini': FullFileTranxFer(self)

    def tick(self):
        setTime = time.strftime('%I:%M:%S %p')
        self.clock.config(text=setTime)
        self.clock.after(200, self.tick)

    @property
    def isServing(self): return self.server

    @property
    def connection(self):
        if self.client != None: return self.client
        elif self.server != None: return self.server

    @property
    def whichConnection(self):
        if self.client: return 'client'
        elif self.server: return 'server'

    @property
    def connected(self):
        if self.connection:
            if self.connection.connected: return True

    @property
    def checkConnected(self):
        if self.connected: return True
        else:
            show('No connection', 'No current connection', 'warn')
            return False

    def update(self):
        self.setServing()
        self.testConnected()

    def setNetwork(self):
        self.networkInfo = self.getNetwork()
        if self.networkInfo: self.networkOn = self.networkInfo.on
        else: self.networkOn = False

        if self.localhostS.get():
            self.networkOn = True
            if self.networkInfo: ip = self.networkInfo.ip
            else: self.lh

            self.serverS.set(ip)
            if self.name == 'full' and self.isServerS.get(): self.serverS.config(state='disabled')
        else:
            if self.name == 'full' and self.sameAsGatewayS.get() and self.isServerS.get(): self.serverS.config(state='normal')
            elif self.name == 'mini': self.serverS.config(state='normal')

        if self.networkOn == True:
            self.networkS.config(bg='green', text='Yes', fg='white')
            return True
        else:
            self.networkS.config(bg='red', text='No', fg='white')
            return False

    def setServing(self):
        if self.isServing: self.servingS.config(text='Yes', bg='green')
        else: self.servingS.config(text='No', bg='red')

    def getPort(self):
        port = self.portS.get() or 0
        try:
                port = int(port)
                assert port > 7000
                assert port < 9001
                return port
        except ValueError as error:
            TranxFerLogger.debug(error)
            show('Invalid', error, 'error')
        except AssertionError as error: show('Invalid', 'Port should be in the range(7000, 9001)', 'error')

    def getServer(self):
        server = self.serverS.get()
        if self.checkIp(server): return server
        else: show('Invalid', 'Server IP is invalid.\nThis is an example (192.168.43.36) or \'localhost\'', 'error')

    def setConnected(self):
        if self.connected: self.connectedS.config(text='Yes', bg='green')
        else: self.connectedS.config(text='No', bg='red')

    def isNetwork(self):
        if self.networkOn: return True
        else: show('No Network Connection', 'This device is not connected to any network', 'error')

    def setServerDetails(self):
        if self.localhostS.get() =='1':
            server = self.lh
            self.serverS.set(self.lh)
        server = self.getServer()

        if server:
            port = self.getPort()
            if port:
                self.port = port
                self.serverSet = True
                return True
            else: return False
        else: return False

    def toServe(self):
        if self.connected:
            show('Connected', 'Already Connected, Stop to continue', 'warn')
        else:
            self.serverSet = False
            if self.name == 'mini' or self.isServerS.get():
                if self.localhostS.get(): ip = self.lh
                else: ip = self.networkInfo.ip if self.networkInfo else self.lh
                self.serverS.set(ip)
                self.serverS.config(state='disabled')
            else: self.serverS.config(state='normal')
            return True

    def connect(self):
        if self.isNetwork() and self.setServerDetails():
            if self.isServing: show('Serving', 'Already Serving, Stop Server to continue', 'info')
            elif self.connecting: show('Connecting', 'Making attempt to connect to the server', 'warn')
            elif self.connected: show('Connected', 'Already Connected, Stop to continue', 'warn')
            else:
                server = self.serverS.get()
                if self.checkIp(server):
                    port = self.getPort()
                    if port:
                        if self.client == None:
                            self.client = Client(server, port, True if self.handShakeS.get() else False)
                            self.connecting = True

    def serve(self):
        if self.isNetwork():
            if self.connected: show('Connected', 'Already Connected, Stop to continue', 'warn')
            else:
                if self.name == 'full': self.isServerS.set('1')
                self.toServe()
                if self.isServing: show('Serving', 'Already Serving', 'warn')
                else: return True

    def browse(self):
        self.path = ''
        _path = dialogFunc(path=1, folder=int(self.isDir.get()))
        if  PRMP_Mixins.checkPath(None, _path):
            self.path = _path
            return _path
        elif _path == '': return
        else: show('Invalid', 'The path provided is invalid', 'error')

    def testConnected(self):
        if self.connecting == False: return
        if self.connection:
            if self.connection.error:
                show(f'{self.connection.error.__class__.__name__}', f'{self.connection.error}', 'error')
                self.connecting = False
                self.connection.shutdown()
                if self.client:
                    del self.client
                    self.client = None
            elif self.connected:
                self.connecting = False
                show('Connection Successfull', 'The connection to the server was accepted successfully.')

    def stopped(self): show('Disconnected', 'Disconnection is successful', 'info')

    def stop(self, ev=0):
        if (ev != 0) or self.isNetwork():
            which = self.whichConnection
            if (which in ['client', 'server']) and confirm(title='Confirmation', msg='Are you sure to disconnect', which=1):
                if self.connection:
                    self.connection.shutdown()
                    self.client = self.server = None
                    self.stopped()
                else: show('Invalid Action', 'You\'re not currently connected or connected to', 'error')

    def checkPath(self, dir_='', event=None):
        path = self.path
        if path:
            pathStat = LocalPathStat(path)
            if dir_:
                if pathStat.isDir: return path
                else: show('Invalid Path', 'The path provided is an invalid directory', 'error')
            elif dir_ == '' and pathStat.exists: return path
            else: show('Invalid Path', 'The path provided is invalid.', 'error')
        else: show('Path Error', 'The path provided is invalid.', 'error')

class MiniFileTranxFer(FileTranxFer):
    name = 'mini'
    geo = (600, 300)

    def __init__(self, master=None, title='Mini File TranxFer', **kwargs):
        super().__init__(master, title=title,  **kwargs)

    def _setupApp(self):
        cont = self.container

        self.network = LabelFrame(cont, place=dict(relx=.02, rely=.02, relh=.47, relw=.96))

        self.clock = Label(self.network, place=dict(relx=.01, rely=.02, relh=.3, relw=.18))

        self.titleL = Label(self.network, text='''Mini FileTranxFer by PRMP Smart!!!.''', place=dict(relx=.19, rely=.02, relh=.3, relw=.61))

        self.full = Button(self.network, text='''Full''', command=self.another, place=dict(relx=.8, rely=.02, relh=.3, relw=.2))

        self.networkL = Label(self.network, text='Network?', place=dict(relx=.01, rely=.34, relh=.3, relw=.15))
        self.networkS = Label(self.network, place=dict(relx=.17, rely=.34, relh=.3, relw=.1))

        self.servingL = Label(self.network, text='Serving?', place=dict(relx=.01, rely=.66, relh=.3, relw=.15))
        self.servingS = Label(self.network, place=dict(relx=.17, rely=.66, relh=.3, relw=.1))

        self.serverL = Label(self.network, text='Server', place=dict(relx=.3, rely=.34, relh=.25, relw=.15))
        self.serverS = Entry(self.network, place=dict(relx=.45, rely=.34, relh=.25, relw=.24))

        self.portL = Label(self.network, text='Port', place=dict(relx=.3, rely=.6, relh=.25, relw=.15))
        self.portS = Entry(self.network, place=dict(relx=.45, rely=.6, relh=.25, relw=.13))

        self.localhostS = Checkbutton(cont, text='Lh?', command=self.setNetwork, place=dict(relx=.7, rely=.185, relh=.11, relw=.12))

        self.stopBtn = Button(self.network, text='Stop', command=self.stop, place=dict(relx=.595, rely=.66, relh=.3, relw=.1))

        self.sentL = Label(self.network, text='Sent', place=dict(relx=.71, rely=.6, relh=.3, relw=.1))
        self.sentS = Label(self.network, place=dict(relx=.815, rely=.6, relh=.3, relw=.175))

        self.pathCont = LabelFrame(cont, place=dict(relx=.02, rely=.5, relh=.48, relw=.96))

        self.pathEnt = Entry(self.pathCont, place=dict(relx=.02, rely=.02,relh=.25, relw=.96), _type='path')
        self.pathEnt.bind('<Return>', self.checkPath, '+')
        self.pathEnt.bind('<KeyRelease>', self.setPath, '+')

        self.browseBtn = Button(self.pathCont, text='''Browse''', command=self.browse, place=dict(relx=.02, rely=.33, relh=.25, relw=.134))

        self.isDir = Checkbutton(self.pathCont, pady="0", text='''Directory?''', place=dict(relx=.17, rely=.33, relh=.25, relw=.2))

        self.serveBtn = Button(self.pathCont, pady="0", text='''Serve''', command=self.serve, place=dict(relx=.71, rely=.33, relh=.25, relw=.134))

        self.receiveBtn = Button(self.pathCont, pady="0", text='''Receive''', command=self.receive, place=dict(relx=.85, rely=.33, relh=.25, relw=.134))

        self.receiving = Label(self.pathCont, text='''Receiving''', place=dict(relx=.02, rely=.7, relh=.25, relw=.16))

        self.progressBar = Progressbar(self.pathCont, length="450", place=dict(relx=.19, rely=.7, relh=.25, relw=.63))

        self.progressTxt = Label(self.pathCont, place=dict(relx=.84, rely=.7, relh=.25, relw=.14))

    def defaults(self):
        self.setPath()
        self.tranxFer = None
        self.setProgress()
        self.tick()

    def setPath(self, e=0):
        if e: self.path = self.pathEnt.get()
        else: self.pathEnt.set(self.path)
        if PRMP_Mixins.checkPath(None, self.path): AutoUploadHandler.setPath(self.path)

    def browse(self):
        super().browse()
        self.setPath()

    def update(self):
        super().update()
        self.setNetwork()
        self.setProgress()
        self.root.after(10, self.update)

    def setServing(self):
        super().setServing()
        self.sentS.config(text=AutoUploadHandler.count)
        if not self.isServing:
            if not self.localhostS.get():
                if not self.serverS.get() and self.networkInfo: self.serverS.set(self.networkInfo.ip)
            self.serverS.config(state='disabled')

    def stop(self, ev=0):
        super().stop(ev)
        self.serverS.config(state='normal')
        if self.server:
            self.server.shutdown()
            self.server = None

        if self.tranxFer:
            self.tranxFer.shutdown()
            self.tranxFer = None

    def serve(self):
        path = self.checkPath()
        if path:
            port = self.getPort()
            if port:
                if super().serve() and confirm(title='Serve it', msg='Do you want to serve this path (%s) for download?'%path, which=1): self.server = AutoUploadServer(start=True, port=port)

    def setDestPath(self):
        path = self.checkPath(dir_=True)
        if path and confirm(title='Destination Directory', msg=f'Do you want to save the downloaded file in this directory {path}?', which=1): return path

    def receive(self):
        port = self.getPort()
        if port:
            server = self.getServer()
            if server:
                path = self.setDestPath()
                if port and server and path:
                    try:
                        soc = socket.socket()
                        soc.connect((server, port))
                    except ConnectionRefusedError as error: show(error.__class__.__name__, error, 'error')
                    self.tranxFer = TranxFer(soc, which='download', dest=path, goOn=True)
                    self.tranxFer.startThreadedTranxFer()

    def setProgress(self):
        if self.tranxFer:
            self.progressBar.config(value=self.tranxFer.tranxFered)
            self.progressTxt.config(text=self.tranxFer.tranxFeredPercent)

            if self.tranxFer.finished:
                del self.tranxFer
                self.tranxFer = None
                show('Download Complete', 'Download completed successfully', 'info')
        else:
            self.progressBar.config(value=0)
            self.progressTxt.config(text='0.00%')
        self.progressBar.update()

class FullFileTranxFer(FileTranxFer):
    name = 'full'
    geo = (500, 900)

    def __init__(self, master=None, title='Full File TranxFer', **kwargs):
        super().__init__(master, title=title,  **kwargs)

    def defaults(self):

        self.serverSet = False

    def _setupApp(self):
        cont = self.container

        self.clock = Label(cont, place=dict(relx=.02, rely=.01, relh=.029, relw=.24)); self.tick()

        self.titleL = Label(cont,  text='FileTranxFer by PRMPSmart', place=dict(relx=.26, rely=.01, relh=.029, relw=.54))

        self.miniBtn = Button(cont, text='''Mini''', command=self.another, place=dict(relx=.8, rely=.01, relh=.029, relw=.2))

        self.localhostS = Checkbutton(cont,  text='Localhost?', place=dict(relx=.02, rely=.045, relh=.04, relw=.3))

        self.osL = Label(cont, text='OS', place=dict(relx=.69, rely=.045, relh=.04, relw=.1))
        self.osS = Label(cont, text=get_os_name(), place=dict(relx=.79, rely=.045, relh=.04, relw=.2))


        self.network = LabelFrame(cont, text='Network Details', place=dict(relx=.013, rely=.085, relh=.27, relw=.98))

        self.networkL = Label(self.network, text='Network?', place=dict(relx=.01, rely=.02, relh=.12, relw=.2))
        self.networkS = Label(self.network, place=dict(relx=.22, rely=.02, relh=.12, relw=.1))

        self.connectedL = Label(self.network, text='Connected?', place=dict(relx=.37, rely=.02, relh=.12, relw=.2))
        self.connectedS = Label(self.network, place=dict(relx=.58, rely=.02, relh=.12, relw=.1))

        self.servingL = Label(self.network, text='Serving?', place=dict(relx=.7, rely=.02, relh=.12, relw=.18))
        self.servingS = Label(self.network, place=dict(relx=.89, rely=.02, relh=.12, relw=.1))

        self.ipAddressL = Label(self.network,  text='IP4 Address', place=dict(relx=.01, rely=.15, relh=.12, relw=.25))

        self.ipAddressS = Label(self.network, place=dict(relx=.26, rely=.15, relh=.12, relw=.3), asEntry=1, font='DEFAULT_FONT')

        self.gatewayL = Label(self.network,  text='Gateway', place=dict(relx=.01, rely=.28, relh=.12, relw=.25))
        self.gatewayS = Label(self.network, place=dict(relx=.26, rely=.28, relh=.12, relw=.3), asEntry=1, font='DEFAULT_FONT')

        self.reloadNetworkBtn = Button(self.network, text='Reload', command=lambda: self.loadNetworkInfo(1), place=dict(relx=.01, rely=.43, relh=.12, relw=.18))

        self.handShakeS = Checkbutton(self.network,  text='HS?', command=self.toServe, place=dict(relx=.2, rely=.43, relh=.12, relw=.15), tip='Do you want Hand Shake security?')

        self.isServerS = Checkbutton(self.network,  text='Server?', command=self.toServe, place=dict(relx=.36, rely=.43, relh=.12, relw=.2))

        self.serverL = Label(self.network,  text='Server', place=dict(relx=.01, rely=.56, relh=.12, relw=.18))
        self.serverS = Entry(self.network, place=dict(relx=.2, rely=.56, relh=.12, relw=.3))

        self.sameAsGatewayS = Checkbutton(self.network,  text='Gateway?', command=self.isGateway, place=dict(relx=.51, rely=.56, relh=.12, relw=.23))

        self.portL = Label(self.network,  text='Port', place=dict(relx=.01, rely=.69, relh=.12, relw=.18))
        self.portS = Entry(self.network, place=dict(relx=.2, rely=.69, relh=.12, relw=.3))

        self.transRateL = Label(self.network, text='Transmission Rates', place=dict(relx=.58, rely=.15, relh=.12, relw=.41))
        self.upRateL = Label(self.network, text='TX / UP', place=dict(relx=.58, rely=.28, relh=.12, relw=.15))
        self.upRateS = Label(self.network, place=dict(relx=.74, rely=.28, relh=.12, relw=.25))
        self.dnRateL = Label(self.network, text='RX / DN', place=dict(relx=.58, rely=.41, relh=.12, relw=.15))
        self.dnRateS = Label(self.network, place=dict(relx=.74, rely=.41, relh=.12, relw=.25))

        self.serverDetailL = Label(self.network,  text='Server IP : Port', place=dict(relx=.01, rely=.87, relh=.12, relw=.313))
        self.serverDetailS = Label(self.network, place=dict(relx=.33, rely=.87, relh=.12, relw=.42), asEntry=1, font='DEFAULT_FONT')

        self.setBtn = Button(self.network, text='Set', command=self.setServerDetails, place=dict(relx=.51, rely=.7, relh=.12, relw=.18))

        self.serveBtn = Button(self.network, text='Serve', command=self.serve, place=dict(relx=.77, rely=.56, relh=.12, relw=.18))

        self.stopBtn = Button(self.network, text='Stop', command=self.stop, place=dict(relx=.77, rely=.7, relh=.12, relw=.18))

        self.connectBtn = Button(self.network, text='Connect', command=self.connect, place=dict(relx=.77, rely=.87, relh=.12, relw=.18))



        self.sendDetails = Details(cont,text='Send', main=self, place=dict(relx=.01, rely=.358, relh=.33, relw=.98))

        if self._path: self.sendDetails.localLoad(self._path)

        self.isDir = Checkbutton(self.sendDetails, text='Directory?', place=dict(relx=.313, rely=0, relw=.255, relh=.082))

        self.receiveDetails = Details(cont, text='Receive', main=self, which='r', place=dict(relx=.013, rely=.695, relh=.3, relw=.98))

    def defaults(self):
        super().defaults()
        self.after(1000, self.loadNetworkInfo)

    def update(self):
        super().update()
        self.setConnected()
        self.root.after(100, self.update)

    def mini(self): MiniFileTranxFer(self)

    def browse(self):
        super().browse()
        if self.path: self.sendDetails.localLoad(self.path)

    def setNetwork(self):
        d = super().setNetwork()
        if d:
            if self.networkInfo: self.gatewayS.config(text=self.networkInfo.gateway)
            else:  self.gatewayS.config(text='No network.')
            return d

    def loadNetworkInfo(self, e=0):
        self.setNetwork()
        if self.networkInfo:
            self.ipAddressS.config(text=self.networkInfo.ip)
            self.gatewayS.config(text=self.networkInfo.gateway)
            if which_platform() != 'nt':
                self.upRateS.config(text=self.networkInfo.tx.fBytes)
                self.dnRateS.config(text=self.networkInfo.rx.fBytes)
        if e==0: self.root.after(1000, self.loadNetworkInfo)

    def isGateway(self):
        d = self.setNetwork()
        if self.connected: show('Connected', 'Already Connected, Stop to continue', 'warn')
        else:
            if not d:
                show(title='Network Error', msg='Network not ON', which='error')
                return
            self.serverSet = False
            self.isServerS.set('0')
            if self.sameAsGatewayS.get():
                ip = self.lh
                if self.networkInfo.gateway:
                    ip = self.networkInfo.gateway or ''
                self.serverS.set(ip)
                self.serverS.config(state='disabled')
            else: self.serverS.config(state='normal')

    def toServe(self):
        if super().toServe(): self.sameAsGatewayS.set('0')

    def setServerDetails(self):
        self.serverDetailS.config(text='')
        if super().setServerDetails():
            self.serverDetailS.config(text=f'{self.serverS.get()} : {self.getPort()}')
            return True

    def serve(self):
        if super().serve():
            if self.setServerDetails():
                self.server = Server(self.port, True if self.handShakeS.get() else False)
                self.setServing()
                return True
            else: show('Not Set', 'Server and Port not set.', 'warn')

class GuiFileTranxFer:
    def __init__(self, full=True, **kwargs):
        TranxFerLogger.setLevel('critical')
        FullFileTranxFer(**kwargs) if full else MiniFileTranxFer(**kwargs)









