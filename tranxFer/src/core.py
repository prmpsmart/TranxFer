import logging, datetime, json, os, threading, zipfile, subprocess, time
from .prmp_miscs import PRMP_Mixins

# platform
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


# zipping
def zipPath(resource, destination='', latest=False):
    # Create name of new zip file, based on original folder or file name
    resource = resource.rstrip('\\').rstrip('/')
    # if resource in destination: TranxFerLogger.warning('Loop: Save somewhere else!')
    
    if not os.path.exists(resource):
        TranxFerLogger.error(resource, 'does not exist')
        return
    
    if destination:
        if os.path.isdir(destination):
            baseFileName = os.path.basename(resource) + '.zip'
            zipFileName = os.path.join(destination, baseFileName)
        else: zipFileName = destination

    else: zipFileName = resource + '.zip'
    
    if os.path.isdir(resource): zipRootDir = os.path.basename(resource)
    
    if (os.path.isfile(zipFileName) == True) and (latest == False):
        TranxFerLogger.debug('ZipFileName %s Already exist'%zipFileName)
        return zipFileName
    
    # Create zip file
    with zipfile.ZipFile(zipFileName, "w", compression=zipfile.ZIP_DEFLATED) as zipFile:
        if os.path.isdir(resource):
            for root, dirs, files in os.walk(resource):
               for file in files:
                   filename = os.path.join(root, file)
                   arc = root.replace(resource, zipRootDir)
                   arcname = os.path.join(arc, file)
                   zipFile.write(filename, arcname, zipfile.ZIP_DEFLATED)
        else: zipFile.write(resource, zipFileName, zipfile.ZIP_DEFLATED)
    return zipFileName

# logger
class TranxFerLogger:
    
    _logLevel = ''
    _only = False
    _logToFile = False
    _log = {'i':'info', 'e':'error', 'd':'debug', 'c':'critical', 'w':'warning'}
    _logLevels = {'info': 20, 'error': 40, 'debug': 10, 'critical': 50, 'warning': 30}
    _levels = list(_logLevels.keys())
    _levelsShort = list(_log.keys())
    
    logFile = 'tranxFerLog.log'
    logFormat = 'TranxFerLogger | %(dt)s | %(lvl)s | %(msg)s. ' # %()
    # logFormat = 'TranxFerLogger | {dt} | : {lvl} | {msg} | {f} ' # .format()
    
    @classmethod
    def logToFile(cls, lvl=0): cls._logToFile = lvl
    
    @classmethod
    def getLevel(cls):
        if cls._logLevel: return (cls._logLevel, cls._only)
    
    @classmethod
    def setLevel(cls, lvl='info', only=False):
        if not lvl: return cls.setLevel('info')
        levels = cls._levelsShort + cls._levels
        assert lvl.lower() in levels, 'Level must be in {} .'.format(levels)
        if lvl == None: return
        if lvl in levels:
            if lvl in cls._levelsShort: lvl = cls._log.get(lvl)
            cls._logLevel = lvl.lower()
            if only: cls._only = True
    
    @classmethod
    def loggable(cls, level):
        classLevel, testLevel = cls._logLevels.get(cls._logLevel), cls._logLevels.get(level)
        if cls._only:
            return level == cls._logLevel
        if classLevel and testLevel:
            if classLevel >= testLevel: return True
        return False
        
    @classmethod
    def writeLog(cls, lvl, msg):
        dt = datetime.datetime.now()
        dicts = {'dt': dt, 'lvl': lvl.upper(), 'msg': msg}
        log = cls.logFormat%dicts + '\n'
        if cls.loggable(lvl): print(log)
        if cls._logToFile: open(cls.logFile, 'a').write(log)
    
    @classmethod
    def info(cls, msg): cls.writeLog('info', msg)
    @classmethod
    def error(cls, msg): cls.writeLog('error', msg)
    @classmethod
    def debug(cls, msg): cls.writeLog('debug', msg)
    @classmethod
    def critical(cls, msg): cls.writeLog('critical', msg)
    @classmethod
    def warning(cls, msg): cls.writeLog('warning', msg)

try: from pathlib import Path
except ImportError: TranxFerLogger.debug('pathlib is not installed.')

# paths
class PathStat(PRMP_Mixins):
    isFolder = 'folder'
    
    def __init__(self, pathFromRoot=None):

        self.path = None
        self.givenPath = None
        self.__pathFromRoot = pathFromRoot
        self.name = None
        self.stat = None
        self.isFile = None
        self.isDir = None
        self.isRemote = False
        self.dest = ''
        self._dict = None
        
        self.ctime = None
        self.atime = None
        self.mtime = None
        
        self.innerSize = 0
        
        self.filesCount = 0
        self.dirsCount = 0
        
        self.openFile = None
        self.zipped = False
    
    def __str__(self): return self.fullName
    
    def normalizePath(self, path_):
        if which_platform() == 'nt': return str(path_).replace('/', '\\')
        else: return str(path_).replace('\\', '/')
    @property
    def size(self):
        if self.exists:
            if self.zipped: return os.path.getsize(self.zipName)
            elif self.isDir: return self.innerSize
            elif self.isFile: return os.path.getsize(self.fullName)
        # else: return self.dicts['size']

    @property
    def zipName(self):
        if self.fullName.endswith('.zip'): return self.fullName
        return self.fullName + '.zip'
    
    @property
    def pathFromRoot(self): 
        if self.__pathFromRoot:
            try: return str(self.__pathFromRoot.pathFromRoot)
            except: return str(self.__pathFromRoot)
        return str(self.name)
    @property
    def exists(self): return os.path.exists(self.fullName)
    
    @property
    def fSize(self): return self.formatSize(self.size)
    @property
    def fullSize(self): return self.formatSize(self.size, 1)
    @property
    def fInnerSize(self): return self.formatSize(self.innerSize)
    @property
    def fullInnerSize(self): return self.formatSize(self.innerSize, 1)
    @property
    def aTime(self): return self.formatTime('a')
    @property
    def cTime(self): return self.formatTime('c')
    @property
    def mTime(self): return self.formatTime('m')
    @property
    def fullATime(self): return self.formatTime('a', 1)
    @property
    def fullCTime(self): return self.formatTime('c', 1)
    @property
    def fullMTime(self): return self.formatTime('m', 1)
    @property
    def dicts(self):
        if self._dict: return self._dict
        
        isFile, isDir = self.isFile, self.isDir
        if self.compress and not isFile:
            isFile, isDir = True, False
            pathFromRoot = name = os.path.basename(self.zipName)
        else:
            name = self.name
            pathFromRoot = self.pathFromRoot
        # print(self.compress)
        return {'name': name, 'isFile': isFile, 'isDir': isDir, 'ctime': self.ctime, 'atime': self.atime, 'mtime': self.mtime, 'size': self.size, 'innerSize': self.innerSize, 'filesCount': self.filesCount, 'dirsCount': self.dirsCount, 'pathFromRoot': pathFromRoot, 'compress': self.compress, 'foldersStrings': self.foldersStrings}
    
    @dicts.setter
    def dicts(self, dict_): self._dict = dict_
    
    @property
    def fullName(self):
        if python_version() == 2:
            if os.path.isabs(self.path): fn = os.path.abspath(self.path)
            else: fn = os.path.join(os.getcwd(), self.givenPath)
        
        else:
            if self.path.is_absolute(): fn = self.path.resolve()
            else: fn = os.path.join(self.path.cwd(), self.givenPath)
        return str(fn)
        
    @property
    def bytesDicts(self):
        dump = json.dumps(self.dicts).encode()
        return dump
    
    @property
    def type(self):
        if self.isFile: return os.path.splitext(self.fullName)[-1]
        elif self.isDir: return self.isFolder
    @property
    def fullType(self):
        fileTypes = {'.aif' : 'AIF audio file', '.cda' : 'CD audio track file', '.mid' : 'MIDI audio file.', '.midi' : 'MIDI audio file.', '.mp3' : 'MP3 audio file', '.mpa' : 'MPEG-2 audio file', '.ogg' : 'Ogg Vorbis audio file', '.wav' : 'WAV file', '.wma' : 'WMA audio file', '.wpl' : 'Windows Media Player playlist', '.7z' : '7-Zip compressed file', '.arj' : 'ARJ compressed file', '.deb' : 'Debian software package file', '.pkg' : 'Package file', '.rar' : 'RAR file', '.rpm' : 'Red Hat Package Manager', '.tar' : 'Tarball compressed file', '.gz': 'Tarball compressed file', '.z' : 'Z compressed file', '.zip' : 'Zip compressed file', '.bin' : 'Binary disc image', '.dmg' : 'macOS X disk image', '.iso' : 'ISO disc image', '.toast' : 'Toast disc image', '.vcd' : 'Virtual CD', '.csv' : 'Comma separated value file', '.dat' : 'Data file', '.db' : 'Database file', '.dbf' : 'Database file', '.log' : 'Log file', '.mdb' : 'Microsoft Access database file', '.sav' : 'Save file (e.g., game save file)', '.sql' : 'SQL database file', '.tar' : 'Linux / Unix tarball file archive', '.xml' : 'XML file', '.email' : 'Outlook Express e-mail message file.', '.eml' : 'E-mail message file from multiple e-mail clients, including Gmail.', '.emlx' : 'Apple Mail e-mail file.', '.msg' : 'Microsoft Outlook e-mail message file.', '.oft' : 'Microsoft Outlook e-mail template file.', '.ost' : 'Microsoft Outlook offline e-mail storage file.', '.pst' : 'Microsoft Outlook e-mail storage file.', '.vcf' : 'E-mail contact file.', '.apk' : 'Android package file', '.bat' : 'Batch file', '.bin' : 'Binary file', '.cgi' : 'Perl script file', '.pl' : 'Perl script file', '.com' : 'MS-DOS command file', '.exe' : 'Executable file', '.gadget' : 'Windows gadget', '.jar' : 'Java Archive file', '.msi' : 'Windows installer package', '.py' : 'Python file', '.wsf' : 'Windows Script File', '.fnt' : 'Windows font file', '.fon' : 'Generic font file', '.otf' : 'Open type font file', '.ttf' : 'TrueType font file', '.ai' : 'Adobe Illustrator file', '.bmp' : 'Bitmap image', '.gif' : 'GIF image', '.ico' : 'Icon file', '.jpeg' : 'JPEG image', '.jpg' : 'JPEG image', '.png' : 'PNG image', '.PNG' : 'PNG image', '.ps' : 'PostScript file', '.psd' : 'PSD image', '.svg' : 'Scalable Vector Graphics file', '.tif' : 'TIFF image', '.tiff' : 'TIFF image', '.asp' : 'Active Server Page file', '.aspx' : 'Active Server Page file', '.cer' : 'Internet security certificate', '.cfm' : 'ColdFusion Markup file', '.cgi' : 'Perl script file', '.pl' : 'Perl script file', '.css' : 'Cascading Style Sheet file', '.htm' : 'HTML file', '.html' : 'HTML file', '.js' : 'JavaScript file', '.jsp' : 'Java Server Page file', '.part' : 'Partially downloaded file', '.php' : 'PHP file', '.py' : 'Python file', '.rss' : 'RSS file', '.xhtml' : 'XHTML file', '.key' : 'Keynote presentation', '.odp' : 'OpenOffice Impress presentation file', '.pps' : 'PowerPoint slide show', '.ppt' : 'PowerPoint presentation', '.pptx' : 'PowerPoint Open XML presentation', '.c' : 'C and C++ source code file', '.class' : 'Java class file', '.cpp' : 'C++ source code file', '.cs' : 'Visual C# source code file', '.h' : 'C, C++, and Objective-C header file', '.hpp' : 'C, C++, and Objective-C header file', '.java' : 'Java Source code file', '.pl' : 'Perl script file.', '.sh' : 'Bash shell script', '.swift' : 'Swift source code file', '.vb' : 'Visual Basic file', '.ods' : 'OpenOffice Calc spreadsheet file', '.xls' : 'Microsoft Excel file', '.xlsm' : 'Microsoft Excel file with macros', '.xlsx' : 'Microsoft Excel Open XML spreadsheet file', '.bak' : 'Backup file', '.cab' : 'Windows Cabinet file', '.cfg' : 'Configuration file', '.cpl' : 'Windows Control panel file', '.cur' : 'Windows cursor file', '.dll' : 'DLL file', '.dmp' : 'Dump file', '.drv' : 'Device driver file', '.icns' : 'macOS X icon resource file', '.ico' : 'Icon file', '.ini' : 'Initialization file', '.lnk' : 'Windows shortcut file', '.msi' : 'Windows installer package', '.sys' : 'Windows system file', '.tmp' : 'Temporary file', '.3g2' : '3GPP2 multimedia file', '.3gp' : '3GPP multimedia file', '.avi' : 'AVI file', '.flv' : 'Adobe Flash file', '.h264' : 'H.264 video file', '.m4v' : 'Apple MP4 video file', '.mkv' : 'Matroska Multimedia Container', '.mov' : 'Apple QuickTime movie file', '.mp4' : 'MPEG4 video file', '.mpg' : 'MPEG video file', '.mpeg' : 'MPEG video file', '.rm' : 'RealMedia file', '.swf' : 'Shockwave flash file', '.vob' : 'DVD Video Object', '.wmv' : 'Windows Media Video file', '.doc' : 'Microsoft Word file', '.docx' : 'Microsoft Word file', '.odt' : 'OpenOffice Writer document file', '.pdf' : 'PDF file', '.rtf' : 'Rich Text Format', '.tex' : 'A LaTeX document file', '.txt' : 'Plain text file', '.wpd' : 'WordPerfect document', self.isFolder : 'Directory'}
        return fileTypes.get(self.type.lower(), 'unknown')
    
    def open(self, pr='rb'):
        if (self.openFile == None):
            # if self.isRemote:

            if self.isFile:
                self.openFile = open(self.fullName, pr)
                self.opened = True
                
            elif self.isDir:
                if self.isRemote:
                    m = 'A Directory %s can not be opened.'%self.name
                    TranxFerLogger.error(m)
                    raise OSError(m)
                p = self.turnToZip()
                self.openFile = open(p, pr)
            return self.openFile
        
        else: TranxFerLogger.error('Path is currently opened.')
    
    def close(self):
        if self.openFile != None:
            self.openFile.close()
            self.openFile = None
        else: TranxFerLogger.error('Path is not currently opened.')
    
    def delete(self):
        if self.zipped: os.remove(self.zipName)
    
    def write(self, byts=b''):
        if (self.openFile != None):
            self.openFile.write(byts)
            return len(byts)
        else: TranxFerLogger.error('Path is not currently opened.')
    
    def read(self, byts=1024):
        if (self.openFile != None): return self.openFile.read(byts)
        else: TranxFerLogger.error('Path is not currently opened.')
    
    def walk(self):
        if self.isFile: self.filesCount, self.dirsCount, self.innerSize = 1, 0, self.size
        
        elif self.isDir:
            for r, ds, fs in os.walk(self.fullName):
                for f in fs:
                    self.filesCount += 1
                    self.innerSize += os.path.getsize(os.path.join(r, f))
                for d in ds: self.dirsCount += 1
    
    def formatTime(self, time='c', full=0):
        strT = '%A, %B %d, %Y, %I:%M:%S %p' if full else '%d/%m/%Y, %H:%M:%S'
        if time in ['a', 'c', 'm']:
            if time == 'a': tm = self.atime
            elif time == 'c': tm = self.ctime
            elif time == 'm': tm = self.mtime
            return datetime.datetime.fromtimestamp(tm).strftime(strT)
        
        # Monday, March 9, 2020, 3:16:43 PM
    
    def formatSize(self, size=0, full=0):
        kb = 1024
        mb = kb ** 2
        gb = kb ** 3
        tb = kb ** 4
        
        strSize = ''
        if full:
            while size >= 0:
                if size >= tb:
                    trby, size = divmod(size, tb)
                    strSize += '%d TB '%trby
                elif size >= gb:
                    giby, size = divmod(size, gb)
                    strSize += '%d GB '%giby
                elif size >= mb:
                    meby, size = divmod(size, mb)
                    strSize += '%d MB '%meby
                elif size >= kb:
                    kbby, size = divmod(size, kb)
                    strSize += '%d KB %d B'%(kbby, size)
                else:  break
        else:
            if size >= tb:
                trby, size = divmod(size, tb)
                strSize = '%d.%s TB '%(trby, self.stripZeros(size, 2))
            elif size >= gb:
                giby, size = divmod(size, gb)
                strSize = '%d.%s GB '%(giby, self.stripZeros(size, 2))
            elif size >= mb:
                meby, size = divmod(size, mb)
                strSize = '%d.%s MB '%(meby, self.stripZeros(size, 2))
            elif size >= kb:
                kbby, size = divmod(size, kb)
                strSize = '%d.%s KB '%(kbby, self.stripZeros(size, 2))
            else: strSize = '%s B '%(self.stripZeros(size, 2))
        return strSize

    def turnToZip(self, u=0):
        if self.compress or u:
            if self.zipped == False and self.isRemote == False:
                TranxFerLogger.info('Started Zipping %s.'%self.fullName)
                z = zipPath(str(self.fullName), self.zipName, latest=self.latest)
                self.compress = True
                self.zipped = True
                assert z == self.zipName
                TranxFerLogger.info('Ended Zipping %s.'%self.fullName)
            return self.zipName
        return self.fullName

class LocalPathStat(PathStat):
    
    def __init__(self, path_, pathFromRoot=None, compress=False, latest=True):
        # super().__init__(pathFromRoot)
        PathStat.__init__(self, pathFromRoot)
        path_ = self.normalizePath(str(path_))
        
        self.givenPath = self.normalizePath(path_)
        
        self.compress = compress
        
        self.latest = latest
        
        if path_ == '.': path_ = os.getcwd()
        
        if python_version() == 2:
            self.path = path_
            self.name = os.path.basename(self.path)
        else:
            self.path = Path(path_)
            self.name = self.path.name
        
        if self.exists:
            if python_version() == 2:
                self.stat = os.stat(self.path)
                self.isFile = os.path.isfile(self.path)
                self.isDir = os.path.isdir(self.path)
            else:
                self.stat = self.path.stat()
                self.isFile = self.path.is_file()
                self.isDir = self.path.is_dir()
        
            self.ctime = self.stat.st_ctime
            self.atime = self.stat.st_atime
            self.mtime = self.stat.st_mtime
            
            threading.Thread(target=self.walk).start()
    
        
    def asRoot(self, path_, obj=False):
        s, p = self.normalizePath(self), self.normalizePath(path_)
        assert (s != p) and (s in p), 'Path must be descendant of {} not {}.'.format(self, path_)
        np = p.replace(os.path.dirname(s),'').strip('\\').strip('/')
        if obj: return LocalPathStat(path_, np)
        return np

    def folders(self):
        if self.compress: yield None
        for r, ds, fs in os.walk(self.fullName):
            for d in ds:
                dd = os.path.join(r, d)
                yield LocalPathStat(dd, self.asRoot(dd))
    
    def files(self):
        if self.compress: yield None
        for r, ds, fs in os.walk(self.fullName):
            for f in fs:
                fd = os.path.join(r, f)
                yield LocalPathStat(fd, self.asRoot(fd))
    
    @property
    def totalFiles(self): return self.filesCount
    
    def testGenerator(self, gen):
        for l in gen:
            if l == None: return False
            return True
        
    @property
    def foldersStrings(self):
        if self.isDir and self.testGenerator(self.folders()):
            dirs = [str(d.pathFromRoot) for d in self.folders()]
            return ';'.join(dirs)
    @property
    def foldersList(self): return list(self.folders())
    @property
    def filesList(self): return list(self.files())
    @property
    def filesList(self): return list(self.files())
    @property
    def totalFolders(self): return len(self.foldersList)

class RemotePathStat(PathStat):
    
    def __init__(self, details, dest=''):
        # super().__init__()
        
        dicts = json.loads(details)
        
        self.dicts = dicts
        
        PathStat.__init__(self, self.normalizePath(dicts['pathFromRoot']))
        
        self.dest = dest
        self.isRemote = True
        
        self.name = dicts['name']
        self.isFile = dicts['isFile']
        self.isDir = dicts['isDir']
        self.ctime = dicts['ctime']
        self.atime = dicts['atime']
        self.mtime = dicts['mtime'] 
        
        self.compress = dicts['compress']

        self.innerSize = dicts['innerSize']
        
        self.filesCount = dicts['filesCount']
        self.dirsCount = dicts['dirsCount']
        self.foldersStrings = self.normalizePath(dicts['foldersStrings'])
        
        if self.foldersStrings:
            folders = self.foldersStrings.split(';')
            for folder in folders[:-1]:
                pth = os.path.join(self.dest, folder)
                
                try: os.makedirs(pth)
                except Exception as error: TranxFerLogger.critical(error)
        else:
            dirs = os.path.dirname(self.pathFromRoot)
            if dirs:
                try: os.makedirs(os.path.join(self.dest, dirs))
                except: pass
    
    @property
    def fullName(self): return os.path.join(self.dest, self.pathFromRoot)

# networks
class NetworkMixin(PRMP_Mixins):
    yes = b'yes'
    conned = b'connected?'
    error = None
    connected = False
    lh = 'localhost'
    
    @property
    def ip(self):
        os = get_os_name()
        if os == 'Android': return self.ipaddress
        elif os == 'Windows': return self.ip4
    
    @classmethod
    def getNetwork(cls):
        os = get_os_name()
        if os == 'Android': return AndroidNetworkInfo()
        elif os == 'Windows': return WindowsNetworkInfo()
    
    @classmethod
    def checkIp(cls, ip):
        if ip == 'localhost': return True
        ips = ip.split('.')
        if len(ips) == 4:
            for i in ips:
                try: int(i)
                except: return False
            return True
        return False
    
    @classmethod
    def getConfig(cls):
        os_ = get_os_name()
        if os_ == 'Windows': prog = 'ipconfig'
        else: prog = 'ifconfig'
        # config = subprocess.check_output([prog]).decode()
        config = os.popen(prog).read()
        
        return config

class Transmission(NetworkMixin):
    def __init__(self): self.restart()
        
    def __repr__(self): return str(self)
        
    def __str__(self): return "%s(packets=%d, errors=%d, dropped=%d, overruns=%d, %s=%d, bytes=%d)"%(self.which, self.packets, self.errors, self.dropped, self.overruns, 'frame' if self.carrier == 0 else 'carrier', self.frame if self.carrier == 0 else self.carrier, self.bytes)
    
    def restart(self):
        self.which = None
        self.packets = 0
        self.errors = 0
        self.dropped = 0
        self.overruns = 0
        self.frame = 0
        self.carrier = 0
        self.bytes = 0

    @property
    def fBytes(self):
        kb = 1024
        mb = kb ** 2
        gb = kb ** 3
        tb = kb ** 4
        
        strBytes = ''
        if self.bytes >= tb:
            trby, self.bytes = divmod(self.bytes, tb)
            strBytes = '%d.%s Tbps '%(trby, self.stripZeros(self.bytes, 2))
        elif self.bytes >= gb:
            giby, self.bytes = divmod(self.bytes, gb)
            strBytes = '%d.%s Gbps '%(giby, self.stripZeros(self.bytes, 2))
        elif self.bytes >= mb:
            meby, self.bytes = divmod(self.bytes, mb)
            strBytes = '%d.%s Mbps '%(meby, self.stripZeros(self.bytes, 2))
        elif self.bytes >= kb:
            kbby, self.bytes = divmod(self.bytes, kb)
            strBytes = '%d.%s Kbps '%(kbby, self.stripZeros(self.bytes, 2))
        else: strBytes = '%s Bps '%self.stripZeros(self.bytes, 2)
        return strBytes

    def parse(self, text):
        lines = text.split()
        if not self.which: self.which = lines[0].strip()
        else:
            if lines[0].strip() != self.which: raise ValueError
        results = lines[1:]
        for result in results:
            prop, val = result.split(':')
            if prop == 'packets': self.packets = int(val)
            if prop == 'errors': self.errors = int(val)
            if prop == 'dropped': self.dropped = int(val)
            if prop == 'overruns': self.overruns = int(val)
            if prop == 'frame': self.frame = int(val)
            if prop == 'carrier': self.carrier = int(val)
            if prop == 'bytes': self.bytes = int(val)

class AndroidInterfaceInfo(NetworkMixin):
    __names = ['ap0', 'wlan0', 'p2p0', 'lo']
    __repls = {'inet': 'inet addr', 'linkEncap': 'Link encap', 'mask': 'Mask', 'scope':'Scope', 'inet6': 'inet6 addr', ':': ': ', 'bCast': 'Bcast'}
    @classmethod
    def names(cls): return cls.__names
    
    def __init__(self, name):
        assert name in self.__names, 'Interface name must be in %r' % self.__names
        self.name = name
        self.rx = Transmission()
        self.tx = Transmission()
    
    def restart(self):
        self.linkEncap = None
        self.inet = None
        self.inet6 = None
        self.bCast = None
        self.mask = None
        self.scope = None
        self.collisions = 0
        self.txqueuelen = 0
        self.on = False
        self.rx.restart()
        self.tx.restart()
    
    def __str__(self): return 'AndriodInterfaceInfo(name=%s, Link_encap=%s, inet addr=%s, Bcast=%s, Mask=%s, inet6 addr=%s, Scope=%s, RX=%s, TX=%s, collisions=%s, txqueuelen=%s)' % (self.name, self.linkEncap, self.inet, self.bCast, self.mask,  self.inet6, self.scope, self.rx, self.tx, self.collisions, self.txqueuelen)
    
    @property
    def ip(self): return self.inet
    
    def generateInfo(self, output=None):
        self.restart()
        if output == None: output = subprocess.check_output(['ifconfig']).decode()
        
        if self.name not in output:
            self.on = False
            return
        
        # Splitting output into lines
        output = [out.strip() for out in output.split('\n')]
        startIndex = endIndex = 0
        
        #Getting InterfaceInfo from the output with name
        start = False
        for line in output:
            if line.startswith(self.name):
                startIndex = output.index(line)
                start = True
            if start:
                if line.startswith('RX bytes'):
                    endIndex = output.index(line)
                    break
        
        # Creating the lines of the Interface infomation
        realOutlines = output[startIndex:endIndex+1]
        
        # Getting the transmission information
        # Removing the transmission infos and needless infos
        if python_version() == 2:outlines = [a for a in realOutlines]
        elif python_version() == 3: outlines = realOutlines.copy()
        
        for line in outlines:
            if line.startswith('RX'):
                if 'TX' in line:
                    subLine = line.split()
                    line1 = ' '.join(subLine[:2])
                    line2 = ' '.join(subLine[2:])
                    self.rx.parse(line1)
                    self.tx.parse(line2)
                else: self.rx.parse(line)
                realOutlines.remove(line)
            elif line.startswith('TX'):
                self.tx.parse(line)
                realOutlines.remove(line)
            
            if 'Metric' in line: realOutlines.remove(line)
        
        # Creating rawStr
        rawStr = ''
        for line in realOutlines: rawStr += ' ' + line
        
        formattedStr = rawStr
        for key in self.__repls:
            val = self.__repls[key]
            formattedStr = formattedStr.replace(val, key)
        
        formattedLines = formattedStr.split()
        
        assert formattedLines[0] == self.name
        
        for line in formattedLines[1:]:
            splitted = line.split(':')
            key = splitted[0]
            if len(splitted) == 2: self.__dict__[key] = splitted[1]
            else: self.__dict__[key] = ':'.join(splitted[1:])

        self.on = True

class AndroidNetworkInfo(NetworkMixin):
    wifi = 'Wifi'
    hotspot = 'Hotspot'
    
    def __init__(self, re=0):
        self.wlan0 = AndroidInterfaceInfo('wlan0')
        self.ap0 = AndroidInterfaceInfo('ap0')
        self.p2p0 = AndroidInterfaceInfo('p2p0')
        self.lo = AndroidInterfaceInfo('lo')
        
        self.interfaces = [self.wlan0, self.ap0, self.p2p0, self.lo]
        
        if re == 0: self.reload()
    
    def __str__(self): return 'AndroidNetworkInfo({}, {}, {}, {})'.format(self.wlan0, self.ap0, self.p2p0, self.lo)
    
    @property
    def status(self):
        st = {}
        for inter in self.interfaces: st[inter.name] = inter.on
        return st
    
    def reload(self):
        self.generateInfo()
        if self.ip: self.on = True
        else: self.on = False
    
    def generateInfo(self, output=''):
        if output: pass
        else: output = self.getConfig()
        [inter.generateInfo(output) for inter in self.interfaces]
    
    @property
    def ipaddress(self):
        if self.wlan0.ip: return self.wlan0.ip or self.lh
        elif self.ap0.on and self.ap0.ip: return self.ap0.ip or self.lh
        return self.lh
    
    ip = ipaddress
    
    @property
    def interface(self):
        if self.wlan0.inet: return self.wifi
        elif self.ap0.on and self.ap0.inet: return self.hotspot

class WindowsNetworkInfo(NetworkMixin):
    
    def __init__(self): self.generateInfo()

    def restart(self):
        self.ip4 = None
        self.ip6 = None
        self.gateway = None
        self.mask = None
        self.on = False

    def __str__(self): return 'WindowsNetworkInfo(Link-local IPv6 Address=%s, IPv4 Address=%s, Subnet Mask=%s, Default Gateway=%s)' % (self.ip6, self.ip4, self.mask, self.gateway)
    
    @property
    def ip(self): return self.ip4 or self.lh

    def generateInfo(self):
        self.restart()
        output = self.getConfig()
        outlines =  output.split('\n')
        stripped_outlines = []
        for line in outlines:
            stli = line.strip()
            stripped_outlines.append(stli)
        
        start = False

        for line in stripped_outlines:
            index = stripped_outlines.index(line)
            if 'Wireless LAN' in line: start = True
            
            if start:
                one = (line.split('.')[0].strip() == 'IPv4 Address')
                two = (stripped_outlines[index + 1].split('.')[0].strip() == 'Subnet Mask')
                three = (stripped_outlines[index + 2].split('.')[0].strip() == 'Default Gateway')
                if one and two and three:
                    self.ip6 = ':'.join(stripped_outlines[index - 1].split(':')[1:]).strip()
                    self.ip4 = line.split(':')[-1].strip()
                    self.mask = stripped_outlines[index + 1].split(':')[-1].strip()
                    self.gateway = stripped_outlines[index + 2].split(':')[-1].strip()
                    self.on = True
                    return

# tranxFer
try: from socketserver import BaseRequestHandler, TCPServer
except ImportError:
    TranxFerLogger.debug('socketserver not installed, I percieve you\'re using python2')
    from SocketServer import BaseRequestHandler, TCPServer
import socket

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
        assert os.path.exists(path_)
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
        self.tranxFer = None
        assert self.path != ''
        compress = os.path.isdir(self.path)
        path = LocalPathStat(self.path, latest=True, compress=compress)
        self.tranxfer = TranxFer(self.request, path=path)
        self.tranxfer.startTranxFer()
        
        self.finish()

class AutoUploadServer(TCPServer, NetworkMixin):
    allow_reuse_address = True
    
    def __init__(self, port=7767, handler=None, start=False):
        Handler = handler or AutoUploadHandler
        TCPServer.__init__(self, ('', port), Handler)
        
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

def autoUpload(path, port=7767, compress=True):
    AutoUploadHandler.setPath(path)
    AutoUploadHandler.setCompress(compress)
    
    AutoUploadServer(port=port, start=True)

def autoDownload(dest='', ip='localhost', port=7767): connectedTranxFer(dest=dest, ip=ip, port=port, goOn=True, which='download').startTranxFer()

def continuousDownload(dest='', ip='localhost', port=7767):
    while True: autoDownload(dest=dest, ip=ip, port=port)











