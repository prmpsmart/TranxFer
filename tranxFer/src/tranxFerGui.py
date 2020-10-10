import os, sys, time, threading
from tkinter import messagebox, filedialog, Tk, Label, LabelFrame, Button, Checkbutton, Frame, Entry, StringVar, Toplevel, Message, Toplevel, Text
from tkinter.ttk import Style, Progressbar
from PIL.ImageTk import PhotoImage, Image
from .network import NetworkMixin
from .tranxFer import AutoUploadServer, Server, Client, TranxFer, LocalPathStat, path, which_platform, get_os_name, time, socket, AutoUploadHandler
from .tranxFerLogger import TranxFerLogger

family = '{Times New Roman}'

font2 = f"-family {family} -size {5 if which_platform() == 'and' else 11} -weight bold"
font1 = f"-family {family} -size {4 if which_platform() == 'and' else 10} -weight bold"
font0 = f"-family {family} -size {2 if which_platform() == 'and' else 7} -weight bold"
compStr = '      ' if (which_platform() == 'and') else ''

def show(title=None, msg=None, which='info'):
    if which == 'error':
        TranxFerLogger.error(msg)
        messagebox.showerror(title, msg)
    elif which == 'info':
        TranxFerLogger.info(msg)
        messagebox.showinfo('Information', msg)
    elif which == 'warn':
        TranxFerLogger.warning(msg)
        messagebox.showwarning('Warning', msg)

def showPath(opened=False, folder=False, many=False, save=False):
    if folder == False:
        if opened == False:
            if many == False:
                if save == False: return filedialog.askopenfilename()
                else: return filedialog.asksaveasfilename()
            else: return filedialog.askopenfilenames()
        else:
            if many == False:
                if save == False: return filedialog.askopenfile()
                else: return filedialog.asksaveasfile()
            else: return filedialog.askopenfiles()
    else: return filedialog.askdirectory()

def confirm(title=None, msg=None, num=None):
    TranxFerLogger.info(msg)
    if num == 1: return messagebox.askyesno(title, msg)
    if num == 2: return messagebox.askquestion(title, msg)
    if num == 3: return messagebox.askokcancel(title, msg)
    if num == 4: return messagebox.askretrycancel(title, msg)
    if num == 5: return messagebox.askyesnocancel(title, msg)

class Tip(Toplevel):
    def __init__(self, wdgt, msg=None, delay=.2, follow=True, root=None):
        self.wdgt = wdgt
        self.parent = self.wdgt.master if root == None else root
        
        super().__init__(self.parent, background='black', padx=1, pady=1)
        self.attributes('-topmost', True)
        self.msg = msg
        self.withdraw()
        self.overrideredirect(True)
        self.msgVar = StringVar()
        if msg is None: self.msgVar.set('No loaded File or Directory.')
        else: self.msgVar.set(msg)
        
        self.delay = delay
        self.follow = follow
        self.visible = 0
        self.lastMotion = 0
        Message(self, textvariable=self.msgVar, background="#d9d9d9", font=font2, aspect=1000).grid()
        self.wdgt.bind('<Enter>', self.spawn, '+')
        self.wdgt.bind('<Leave>', self.hide, '+')
        self.wdgt.bind('<Motion>', self.move, '+')
        
    def update(self, msg): self.msgVar.set(msg)

    def spawn(self, event=None):
        self.visible = 1
        self.after(int(self.delay * 1000), self.show)

    def show(self):
        if self.visible == 1 and time.time() - self.lastMotion > self.delay: self.visible = 2
        if self.visible == 2: self.deiconify()

    def move(self, event):
        self.lastMotion = time.time()
        if self.follow is False:
            self.withdraw()
            self.visible = 1
        self.geometry('+%i+%i' % (event.x_root+20, event.y_root-10))
        
        #To get the present event coordinates
        # print(event.x_root,event.y_root)
        
        self.after(int(self.delay * 1000), self.show)

    def hide(self, event=None):
        self.visible = 0
        self.withdraw()

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

        super().__init__(master, relief='groove', font=font2, foreground="black", background="#d9d9d9", highlightbackground="#d9d9d9", highlightcolor="black", **kw)
        
        self.main = main
        self.which = which
        self.destDir = StringVar()
        self.destDir.set('0')
        self.destPath = ''
        
        self.indicatorLbl = Label(self, activebackground="#ececec", activeforeground="#000000", background="red", disabledforeground="#a3a3a3", font=font2, foreground="white", highlightbackground="#d9d9d9", highlightcolor="black", pady="0", relief='groove')
        self.indicatorLbl.place(relx=.61, rely=0, relh=.1, relw=.1)
        
        self.actionBtn = Button(self, activebackground="#ececec", activeforeground="#000000", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", relief='ridge', highlightcolor="black",  text='Send' if which == 's' else 'Receive', command=self.send if which == 's' else self.receive)
        self.actionBtn.place(relx=.781, rely=0, relh=.1, relw=.154)
        
        self.browseBtn = Button(self, activebackground="#ececec", activeforeground="#000000", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", relief='ridge',text='Browse' if which == 's' else 'Remote Load', command=self.main.browse if which == 's' else self.remoteLoad)
        self.browseBtn.place(relx=.015, rely=0, relh=.1, relw=.154 if which == 's' else .26)
        
        if which == 'r':
            self.destDirChk = Checkbutton(self, text=f'{compStr} Destination?', activebackground="#ececec", activeforeground="#000000", background="#d9d9d9", disabledforeground="#a3a3a3", font=font1, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0", relief="groove", variable=self.destDir, command=self.setDest)
            self.destDirChk.place(relx=.313, rely=0, relw=.255, relh=.082)
        
        self.detConts = Frame(self, relief='groove', border="2", background="#d9d9d9")
        self.detConts.place(relx=.01, rely=.114, relh=.868, relw=.981)
        
        self.which = which
        self.pathStat = None
        
        self.decompAndComp = StringVar()
        self.decompAndComp.set('0')

        self.nameL = Button(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Name', command=self.reload)
        self.nameL.place(relx=.01, rely=.01, relh=.12, relw=.164)
        self.nameS = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='File Name')
        self.nameS.place(relx=.175, rely=.01, relh=.12, relw=.82)
        self.nameTip = Tip(self.nameS, root=root)

        self.sizeL = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Size')
        self.sizeL.place(relx=.01, rely=.14, relh=.12, relw=.164)
        self.sizeS = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", anchor='ne')
        self.sizeS.place(relx=.175, rely=.14, relh=.12, relw=.274)
        self.sizeTip = Tip(self.sizeS, root=root)

        self.typeL = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Type')
        self.typeL.place(relx=.01, rely=.27, relh=.12, relw=.164)
        self.typeS = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", anchor='ne', justify='right')
        self.typeS.place(relx=.175, rely=.27, relh=.12, relw=.274)
        self.typeTip = Tip(self.typeS, root=root)

        self.ctimeL = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='CTime')
        self.ctimeL.place(relx=.01, rely=.4, relh=.12, relw=.164)
        self.ctimeS = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font0, relief="groove", anchor='nw', justify='right')
        self.ctimeS.place(relx=.175, rely=.4, relh=.12, relw=.274)
        self.ctimeTip = Tip(self.ctimeS, root=root)

        self.atimeL = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='ATime')
        self.atimeL.place(relx=.01, rely=.53, relh=.12, relw=.164)
        self.atimeS = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font0, relief="groove", anchor='nw', justify='right')
        self.atimeS.place(relx=.175, rely=.53, relh=.12, relw=.274)
        self.atimeTip = Tip(self.atimeS, root=root)

        self.mtimeL = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='MTime')
        self.mtimeL.place(relx=.01, rely=.66, relh=.12, relw=.164)
        self.mtimeS = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font0, relief="groove", anchor='nw', justify='right')
        self.mtimeS.place(relx=.175, rely=.66, relh=.12, relw=.274)
        self.mtimeTip = Tip(self.mtimeS, root=root)

        self.filesCountL = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Files Count')
        self.filesCountL.place(relx=.47, rely=.14, relh=.12, relw=.329)
        self.filesCountS = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", anchor='ne')
        self.filesCountS.place(relx=.8, rely=.14, relh=.12, relw=.194)

        self.dirsCountL = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Dirs Count')
        self.dirsCountL.place(relx=.47, rely=.27, relh=.12, relw=.329)
        self.dirsCountS = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", anchor='ne')
        self.dirsCountS.place(relx=.8, rely=.27, relh=.12, relw=.194)
        
        self.innerSizeL = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Inner Files Size')
        self.innerSizeL.place(relx=.47, rely=.4, relh=.12, relw=.329)
        self.innerSizeS = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font1, relief="groove", anchor='ne')
        self.innerSizeS.place(relx=.8, rely=.4, relh=.12, relw=.194)
        self.innerSizeTip = Tip(self.innerSizeS, root=root)
        
        
        
        text = 'Compress?' if which == 's' else 'Decompress?'
        compText = compStr + text
        tip = 'Compress before sending (Good for Directories).' if which == 's' else 'Decompress after receiving (Good for Directories).'
        
        
        self.detailsL = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Details')
        self.detailsL.place(relx=.493, rely=.53, relh=.12, relw=.268)
        self.detailsS = Label(self.detConts, background="red", foreground="white", font=font2, relief="groove", text='No')
        self.detailsS.place(relx=.78, rely=.53, relh=.12, relw=.205)
        
        self.compress = Checkbutton(self, text=compText, activebackground="#ececec", activeforeground="#000000", background="#d9d9d9", disabledforeground="#a3a3a3", font=font1, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", relief="groove", variable=self.decompAndComp)
        self.compress.place(relx=.493, rely=.69, relw=.268, relh=.1)
        self.compressTip = Tip(self.compress, msg=tip, root=root)

        self.previewBtn = Button(self, activebackground="#ececec", activeforeground="#000000", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0", relief="ridge", text='Preview', command=self.preview)
        self.previewBtn.place(relx=.77, rely=.69, relh=.1, relw=.205)

        self.level = Progressbar(self, value="30")
        self.level.place(relx=.02, rely=.82, relh=.14, relw=.75)

        self.percent = Label(self.detConts, background="#d9d9d9", foreground="#000000", font=font1, relief="groove", anchor='center', text='100%')
        self.percent.place(relx=.78, rely=.82, relh=.14, relw=.22)
        
        self.tranxFer = None
        self.pathStat = None
        
        self.after(100, self.update)
     
    def preview(self): Preview(self.main.root, self.pathStat)
    
    def setDest(self):
        self.destPath = ''
        if self.destDir.get() == '1':
            p = showPath(folder=1)
            if path.exists(p): self.destPath = p
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
            self.nameTip.update(self.pathStat.fullName)
            
            self.sizeS.config(text=self.pathStat.fSize)
            self.sizeTip.update(self.pathStat.fullSize)
            
            self.typeS.config(text=self.pathStat.type)
            self.typeTip.update(self.pathStat.fullType)
            
            self.ctimeS.config(text=self.pathStat.cTime)
            self.ctimeTip.update(self.pathStat.fullCTime)
            
            self.atimeS.config(text=self.pathStat.aTime)
            self.atimeTip.update(self.pathStat.fullATime)
            
            self.mtimeS.config(text=self.pathStat.mTime)
            self.mtimeTip.update(self.pathStat.fullMTime)
            
            self.filesCountS.config(text=self.pathStat.filesCount)
            
            self.dirsCountS.config(text=self.pathStat.dirsCount)
            
            self.innerSizeS.config(text=self.pathStat.fInnerSize)
            self.innerSizeTip.update(self.pathStat.fullInnerSize)
        self.after(1000, self.load)
    
    def localLoad(self, path):
        if isinstance(path, str): pass
        else: path = path.get()
        
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
                self.tranxFer = TranxFer(self.main.connection, LocalPathStat(self.main.path.get()))
                self.tranxFer.startThreadedTranxFer()
    
    def receive(self):
        if self.main.checkConnected:
            if self.tranxFer and self.tranxFer.startedReceiving:
                show('Error', 'A tranxFer is still on', 'error')
                return
            if self.tranxFer: self.tranxFer.startThreadedReceiving()
            else: show('TranxFer Error', 'Load remotely first to get the path details', 'warn')

class GuiMixin(NetworkMixin):
    _path = ''
    _server = ''
    _port = 7767
    
    def __init__(self, root, name='gui'):
        self.name = name
        
        self.isDir = StringVar()
        self.isServer = StringVar()
        self.handShake = StringVar()
        self.serverEnt = StringVar()
        self.portEnt = StringVar()
        self.path = StringVar()
        self.localhost = StringVar()
        self.sameAsGateway = StringVar()
        
        self.sameAsGateway.set('0')
        self.isDir.set('0')
        self.isServer.set('0')
        self.handShake.set('0')
        self.localhost.set('0')
        self.portEnt.set('7767')
        self.path.set(self._path)
        
        self.serverDefault()
        
        self.networkInfo = None
        self.server = None
        self.client = None
        self.connecting = False
        self.networkOn = False
        
        self.root.attributes('-topmost', True)
        
        if get_os_name() != 'Android':  self.root.attributes('-tool', True)
        
        self.root.configure(background="#d9d9d9")
        self.root.bind('<Control-m>', sys.exit)
        self.root.bind('<Control-M>', sys.exit)
        self.root.bind('<Control-n>', self.new)
        self.root.bind('<Control-N>', self.new)
        self.root.bind('<Control-a>', self.another)
        self.root.bind('<Control-A>', self.another)
        
        if root == None: self.root.protocol('WM_DELETE_WINDOW', self.exiting)
        
        self.root.resizable(0, 0)
        
        self.cmds()
    
    def cmds(self):
        self.path.set(self._path)
        self.serverEnt.set(self._server)
        self.portEnt.set(self._port)
    
    def exiting(self):
        try: self.stop(1)
        except Exception as error: TranxFerLogger.debug(error)
        sys.exit()
    
    def serverDefault(self): self.serverEnt.set('192.168.43.')
    
    def new(self, e=None):
        if self.name == 'mini': MiniFileTranxFer(root=self.root)
        elif self.name == 'full': FullFileTranxFer(root=self.root)
    
    def another(self, e=None):
        if self.name == 'full': MiniFileTranxFer(root=self.root)
        elif self.name == 'mini': FullFileTranxFer(root=self.root)

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
       
        if self.localhost.get() == '1':
            self.networkOn = True
            self.serverEnt.set(self.networkInfo.ip if self.networkInfo else self.lh)
            self.serverS.config(state='disabled')
        else:
            if self.sameAsGateway.get() == '0' and self.isServer.get() == '0': self.serverS.config(state='normal')
        
        if self.networkOn == True:
            self.networkS.config(bg='green', text='Yes', fg='white')
        else: self.networkS.config(bg='red', text='No', fg='white')
    
    def setServing(self):
        if self.isServing: self.servingS.config(text='Yes', bg='green')
        else: self.servingS.config(text='No', bg='red')
    
    def getPort(self):
        port = self.portEnt.get()
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
        server = self.serverEnt.get()
        if self.checkIp(server): return server
        else: show('Invalid', 'Server IP is invalid.\nThis is an example (192.168.43.36) or \'localhost\'', 'error')
    
    def setConnected(self):
        if self.connected: self.connectedS.config(text='Yes', bg='green')
        else: self.connectedS.config(text='No', bg='red')
    
    def isNetwork(self):
        if self.networkOn: return True
        else: show('No Network Connection', 'This device is not connected to any network', 'error')
    
    def setServerDetails(self):
        if self.localhost.get() =='1':
            server = self.lh
            self.serverEnt.set(self.lh)
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
            if self.isServer.get() == '1':
                if self.localhost.get() == '1': ip = self.lh
                else: ip = self.networkInfo.ip if self.networkInfo else self.lh
                self.serverEnt.set(ip)
                self.serverS.config(state='disabled')
            else: self.serverS.config(state='normal')
            return True
    
    def connect(self):
        if self.isNetwork() and self.setServerDetails():
            if self.isServing: show('Serving', 'Already Serving, Stop Server to continue', 'info')
            elif self.connecting: show('Connecting', 'Making attempt to connect to the server', 'warn')
            elif self.connected: show('Connected', 'Already Connected, Stop to continue', 'warn')
            else:
                server = self.serverEnt.get()
                if self.checkIp(server):
                    port = self.getPort()
                    if port:
                        if self.client == None:
                            self.client = Client(server, port, True if self.handShake.get() == '1' else False)
                            self.connecting = True
    
    def serve(self):
        if self.isNetwork():
            if self.connected: show('Connected', 'Already Connected, Stop to continue', 'warn')
            else:
                self.isServer.set('1')
                self.toServe()
                if self.isServing: show('Serving', 'Already Serving', 'warn')
                else: return True

    def browse(self):
        self.path.set('')
        _path = showPath(folder=int(self.isDir.get()))
        if path.exists(_path):
            self.path.set(_path)
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
            if (which in ['client', 'server']) and confirm('Confirmation', 'Are you sure to disconnect', 1):
                if self.connection:
                    self.connection.shutdown()
                    self.client = self.server = None
                    self.stopped()
                else: show('Invalid Action', 'You\'re not currently connected or connected to', 'error')
    
    def checkPath(self, dir_='', event=None):
        path = self.path.get()
        if path:
            pathStat = LocalPathStat(path)
            if dir_:
                if pathStat.isDir: return path
                else: show('Invalid Path', 'The path provided is an invalid directory', 'error')
            elif dir_ == '' and pathStat.exists: return path
            else: show('Invalid Path', 'The path provided is invalid.', 'error')
        else: show('Path Error', 'The path provided is invalid.', 'error')

class MiniFileTranxFer(GuiMixin):
    
    def __init__(self, root=None):
        if root: self.root = Toplevel(root)
        else: self.root = Tk()
        
        self.isReceive = StringVar()
        self.isReceive.set('0')
        
        super().__init__(root, name='mini')
        
        self.root.geometry("506x200")
        self.root.title("Mini File TranxFer")
        # self.root.attributes('-alpha', .3)
        
        self.network = LabelFrame(self.root, relief='groove', background="#d9d9d9")
        self.network.place(relx=.02, rely=.02, relh=.47, relw=.96)
        
        self.titleL = Label(self.network, background="#0000ff", bd="3", disabledforeground="#a3a3a3", font=font2, foreground="#ffffff", relief="ridge", text='''Mini FileTranxFer by PRMP Smart!!!.''', anchor='center')
        self.titleL.place(relx=.01, rely=.02, relh=.3, relw=.98)
        
        self.clock = Label(self.titleL, font=font1, fg="black", bg='white', relief='solid')
        self.clock.place(relx=.01, rely=.04, relh=.9, relw=.2)
        self.tick()
        
        self.full = Button(self.titleL, activebackground="#ececec", activeforeground="#000000", background="blue", disabledforeground="#a3a3a3", font=font2, foreground="white", highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Full''', relief='groove', overrelief='groove', command=self.another)
        self.full.place(relx=.8, rely=.04, relh=.9, relw=.2)
        
        self.networkL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font1, relief="groove", anchor='center', text='Network?')
        self.networkL.place(relx=.01, rely=.34, relh=.3, relw=.15)
        self.networkS = Label(self.network, background="#008000", foreground="#ffffff", font=font1, relief="groove", anchor='center')
        self.networkS.place(relx=.17, rely=.34, relh=.3, relw=.1)
        
        self.servingL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", anchor='center', text='Serving?')
        self.servingL.place(relx=.01, rely=.66, relh=.3, relw=.15)
        self.servingS = Label(self.network, background="#008000", foreground="#ffffff", font=font1, relief="groove", anchor='center')
        self.servingS.place(relx=.17, rely=.66, relh=.3, relw=.1)

        self.serverL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Server')
        self.serverL.place(relx=.3, rely=.34, relh=.25, relw=.15)
        self.serverS = Entry(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", textvariable=self.serverEnt)
        self.serverS.place(relx=.45, rely=.34, relh=.25, relw=.24)

        self.portL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Port')
        self.portL.place(relx=.3, rely=.6, relh=.25, relw=.15)
        self.portS = Entry(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", textvariable=self.portEnt)
        self.portS.place(relx=.45, rely=.6, relh=.25, relw=.13)
        
        self.localhostS = Checkbutton(self.root, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Lh?', variable=self.localhost, command=self.setNetwork)
        self.localhostS.place(relx=.7, rely=.185, relh=.11, relw=.12)
        
        self.stopBtn = Button(self.network, activebackground="#ececec", activeforeground="#0000ff", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='Stop', command=self.stop, relief='groove')
        self.stopBtn.place(relx=.595, rely=.66, relh=.3, relw=.1)
        
        self.sentL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Sent')
        self.sentL.place(relx=.71, rely=.6, relh=.3, relw=.1)
        self.sentS = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove")
        self.sentS.place(relx=.815, rely=.6, relh=.3, relw=.175)
        
        self.pathCont = LabelFrame(self.root, relief='groove', background="#d9d9d9")
        self.pathCont.place(relx=.02, rely=.5, relh=.48, relw=.96)
        
        self.pathEnt = Entry(self.pathCont, background="white", disabledforeground="#a3a3a3", font="-family {Courier New} -size 10", foreground="#000000", insertbackground="black", textvariable=self.path)
        self.pathEnt.place(relx=.02, rely=.02,relh=.25, relw=.96)
        self.pathEnt.bind('<Return>', self.checkPath)
        self.pathEnt.bind('<KeyRelease>', self.setPath)

        self.browseBtn = Button(self.pathCont, activebackground="#ececec", activeforeground="#0000ff", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Browse''', command=self.browse, relief='groove')
        self.browseBtn.place(relx=.02, rely=.33, relh=.25, relw=.134)
        
        self.isDirBtn = Checkbutton(self.pathCont, activebackground="#ececec", activeforeground="#0000ff", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Directory?''', variable=self.isDir, relief='groove')
        self.isDirBtn.place(relx=.17, rely=.33, relh=.25, relw=.2)

        self.serveBtn = Button(self.pathCont, activebackground="#ececec", activeforeground="#0000ff", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Serve''', command=self.serve, relief='groove')
        self.serveBtn.place(relx=.71, rely=.33, relh=.25, relw=.134)
        
        self.receiveBtn = Button(self.pathCont, activebackground="#ececec", activeforeground="#0000ff", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Receive''', command=self.receive, relief='groove')
        self.receiveBtn.place(relx=.85, rely=.33, relh=.25, relw=.134)

        self.receiving = Label(self.pathCont, background="#d9d9d9", foreground="#000000", font=font1, relief="groove", text='''Receiving''')
        self.receiving.place(relx=.02, rely=.7, relh=.25, relw=.16)
        
        self.progressBar = Progressbar(self.pathCont, length="450")
        self.progressBar.place(relx=.19, rely=.7, relh=.25, relw=.63)

        self.progressTxt = Label(self.pathCont, background="#d9d9d9", foreground="#000000", font=font1, relief="groove")
        self.progressTxt.place(relx=.84, rely=.7, relh=.25, relw=.14)
        
        self.setPath()
        
        self.tranxFer = None
        self.setProgress()
        self.root.after(10, self.update)
        self.root.mainloop()
    
    def setPath(self, e=0): 
        path_ = self.path.get()
        if path.exists(path_):
            AutoUploadHandler.setPath(path_)
    
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
        if self.isServing:
            if self.localhost.get() == '0': self.serverEnt.set(self.networkInfo.ip)
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
        port = self.getPort()
        if super().serve() and path and port and confirm('Serve it', 'Do you want to serve this path (%s) for download?'%path, 1): self.server = AutoUploadServer(start=True, port=port)

    def setDestPath(self):
        path = self.checkPath(dir_=True)
        if path and confirm('Destination Directory', f'Do you want to save the downloaded file in this directory {path}?', 1): return path

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

class FullFileTranxFer(GuiMixin):
    
    def __init__(self, root=None):
        if root: self.root = Toplevel(root)
        else: self.root = Tk()
        
        super().__init__(root, name='full')
        
        self.root.geometry("400x800")
        self.root.title("FileTranxFer")
        
        self.serverSet = False
        
        self.titleL = Label(self.root, background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", relief="groove", text='FileTranxFer by PRMPSmart')
        self.titleL.place(relx=.01, rely=.01, relh=.029, relw=.98)
        
        self.clock = Label(self.titleL, font=font1, fg="black", bg='white', relief='solid', anchor='center')
        self.clock.place(relx=.01, rely=.04, relh=.9, relw=.24)
        self.tick()
        
        self.miniBtn = Button(self.titleL, activebackground="#ececec", activeforeground="#000000", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0", text='''Mini''', relief='flat', overrelief='groove', command=self.another)
        self.miniBtn.place(relx=.8, rely=.04, relh=.9, relw=.2)
        
        self.localhostS = Checkbutton(self.root, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Localhost?', variable=self.localhost)
        self.localhostS.place(relx=.02, rely=.045, relh=.04, relw=.3)
        
        self.osL = Label(self.root, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", anchor='center', text='OS')
        self.osL.place(relx=.69, rely=.045, relh=.04, relw=.1)
        self.osS = Label(self.root, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", anchor='center', text=get_os_name())
        self.osS.place(relx=.79, rely=.045, relh=.04, relw=.2)
        

        self.network = LabelFrame(self.root, relief='groove', font=font2, foreground="black", text='Network Details', background="#d9d9d9")
        self.network.place(relx=.013, rely=.085, relh=.27, relw=.98)
        
        self.networkL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font1, relief="groove", anchor='center', text='Network?')
        self.networkL.place(relx=.01, rely=.02, relh=.12, relw=.2)
        self.networkS = Label(self.network, background="#008000", foreground="#ffffff", font=font1, relief="groove", anchor='center')
        self.networkS.place(relx=.22, rely=.02, relh=.12, relw=.1)
        
        self.connectedL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font1, relief="groove", anchor='center', text='Connected?')
        self.connectedL.place(relx=.37, rely=.02, relh=.12, relw=.2)
        self.connectedS = Label(self.network, background="#008000", foreground="#ffffff", font=font1, relief="groove", anchor='center')
        self.connectedS.place(relx=.58, rely=.02, relh=.12, relw=.1)
        
        self.servingL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", anchor='center', text='Serving?')
        self.servingL.place(relx=.7, rely=.02, relh=.12, relw=.18)
        self.servingS = Label(self.network, background="#008000", foreground="#ffffff", font=font1, relief="groove", anchor='center')
        self.servingS.place(relx=.89, rely=.02, relh=.12, relw=.1)

        self.ipAddressL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='IP4 Address')
        self.ipAddressL.place(relx=.01, rely=.15, relh=.12, relw=.25)

        self.ipAddressS = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove")
        self.ipAddressS.place(relx=.26, rely=.15, relh=.12, relw=.3)
        
        self.gatewayL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Gateway')
        self.gatewayL.place(relx=.01, rely=.28, relh=.12, relw=.25)
        self.gatewayS = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove")
        self.gatewayS.place(relx=.26, rely=.28, relh=.12, relw=.3)
        
        self.reloadNetworkBtn = Button(self.network, activebackground="#ececec", activeforeground="#0000ff", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", relief='ridge',highlightcolor="black", pady="0", text='Reload', command=lambda: self.loadNetworkInfo(1))
        self.reloadNetworkBtn.place(relx=.01, rely=.43, relh=.12, relw=.18)
        
        # self.handShakeS = Checkbutton(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='HS?', variable=self.handShake, command=self.toServe)
        # self.handShakeS.place(relx=.2, rely=.43, relh=.12, relw=.15)
        # Tip(self.handShakeS, 'Do you want Hand Shake security?')
        
        self.isServerS = Checkbutton(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Server?', variable=self.isServer, command=self.toServe)
        self.isServerS.place(relx=.36, rely=.43, relh=.12, relw=.2)
        
        self.serverL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Server')
        self.serverL.place(relx=.01, rely=.56, relh=.12, relw=.18)
        self.serverS = Entry(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", textvariable=self.serverEnt)
        self.serverS.place(relx=.2, rely=.56, relh=.12, relw=.3)
        
        self.gatewayAsServerS = Checkbutton(self.network, background="#d9d9d9", foreground="#000000", font=font1, relief="groove", text='Gateway?', variable=self.sameAsGateway, command=self.isGateway)
        self.gatewayAsServerS.place(relx=.51, rely=.56, relh=.12, relw=.23)
        
        self.portL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Port')
        self.portL.place(relx=.01, rely=.69, relh=.12, relw=.18)
        self.portS = Entry(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", textvariable=self.portEnt)
        self.portS.place(relx=.2, rely=.69, relh=.12, relw=.3)

        self.transRateL = Label(self.network, background="blue", foreground="white", font=font2, relief="groove", anchor='center', text='Transmission Rates')
        self.transRateL.place(relx=.58, rely=.15, relh=.12, relw=.41)
        self.upRateL = Label(self.network, background="green", foreground="white", font=font1, relief="groove", anchor='center', text='TX / UP')
        self.upRateL.place(relx=.58, rely=.28, relh=.12, relw=.15)
        self.upRateS = Label(self.network, background="green", foreground="white", font=font1, relief="groove", anchor='center')
        self.upRateS.place(relx=.74, rely=.28, relh=.12, relw=.25)
        self.dnRateL = Label(self.network, background="green", foreground="white", font=font1, relief="groove", anchor='center', text='RX / DN')
        self.dnRateL.place(relx=.58, rely=.41, relh=.12, relw=.15)
        self.dnRateS = Label(self.network, background="green", foreground="white", font=font1, relief="groove", anchor='center')
        self.dnRateS.place(relx=.74, rely=.41, relh=.12, relw=.25)

        self.serverDetailL = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove", text='Server IP : Port')
        self.serverDetailL.place(relx=.01, rely=.87, relh=.12, relw=.313)
        self.serverDetailS = Label(self.network, background="#d9d9d9", foreground="#000000", font=font2, relief="groove")
        self.serverDetailS.place(relx=.33, rely=.87, relh=.12, relw=.42)
        
        self.setBtn = Button(self.network, activebackground="#ececec", activeforeground="#0000ff", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", relief='ridge',highlightcolor="black", pady="0", text='Set', command=self.setServerDetails)
        self.setBtn.place(relx=.51, rely=.7, relh=.12, relw=.18)
        
        self.serveBtn = Button(self.network, activebackground="#ececec", activeforeground="#0000ff", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", relief='ridge',highlightcolor="black", pady="0", text='Serve', command=self.serve)
        self.serveBtn.place(relx=.77, rely=.56, relh=.12, relw=.18)

        self.stopBtn = Button(self.network, activebackground="#ececec", activeforeground="#0000ff", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", relief='ridge',highlightcolor="black", pady="0", text='Stop', command=self.stop)
        self.stopBtn.place(relx=.77, rely=.7, relh=.12, relw=.18)
        
        self.connectBtn = Button(self.network, activebackground="#ececec", activeforeground="#0000ff", background="#d9d9d9", disabledforeground="#a3a3a3", font=font2, foreground="#000000", highlightbackground="#d9d9d9", relief='ridge',highlightcolor="black", pady="0", text='Connect', command=self.connect)
        self.connectBtn.place(relx=.77, rely=.87, relh=.12, relw=.18)



        self.sendDetails = Details(self.root,text='Send', main=self)
        self.sendDetails.place(relx=.01, rely=.358, relh=.33, relw=.98)
        
        if self._path: self.sendDetails.localLoad(self._path)

        self.isDirChk = Checkbutton(self.sendDetails, text=f'{compStr} Directory?', activebackground="#ececec", activeforeground="#000000", background="#d9d9d9", disabledforeground="#a3a3a3", font=font1, foreground="#000000", highlightbackground="#d9d9d9", highlightcolor="black", pady="0", relief="groove", variable=self.isDir)
        self.isDirChk.place(relx=.313, rely=0, relw=.255, relh=.082)

        self.receiveDetails = Details(self.root, text='Receive', main=self, which='r')
        self.receiveDetails.place(relx=.013, rely=.695, relh=.3, relw=.98)
        self.root.after(1000, self.loadNetworkInfo)
        self.root.after(10, self.update)
        self.root.mainloop()
        
    def update(self):
        super().update()
        self.setConnected()
        self.root.after(100, self.update)
    
    def mini(self): MiniFileTranxFer(self.root)
    
    def browse(self):
        super().browse()
        if self.path: self.sendDetails.localLoad(self.path)
    
    def setNetwork(self):
        super().setNetwork()
        if self.networkInfo: self.gatewayS.config(text=self.networkInfo.gateway)
        else:  self.gatewayS.config(text='No network.')
    
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
        if self.connected: show('Connected', 'Already Connected, Stop to continue', 'warn')
        else:
            self.serverSet = False
            self.isServer.set('0')
            if self.sameAsGateway.get() == '1':
                self.serverEnt.set(self.networkInfo.gateway if self.networkInfo else self.lh)
                self.serverS.config(state='disabled')
            else: self.serverS.config(state='normal')
    
    def toServe(self):
        if super().toServe(): self.sameAsGateway.set('0')
        
    def setServerDetails(self):
        if self.localhost.get() == '1' and 8: 0
            # if
        self.serverDetailS.config(text='')
        if super().setServerDetails():
            self.serverDetailS.config(text=f'{self.serverEnt.get()} : {self.getPort()}')
            return True
    
    def serve(self):
        if super().serve():
            if self.setServerDetails():
                self.server = Server(self.port, True if self.handShake.get() == '1' else False)
                self.setServing()
                return True
            else: show('Not Set', 'Server and Port not set.', 'warn')

class FileTranxFer:
    
    def __init__(self, full=True):
        TranxFerLogger.setLevel('critical')
        FullFileTranxFer() if full else MiniFileTranxFer()


