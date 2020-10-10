from datetime import datetime, timedelta
from .tranxFerLogger import TranxFerLogger
from json import dumps, loads
from os import path, walk, stat, getcwd, remove, makedirs
import threading
try: from pathlib import Path
except ImportError: TranxFerLogger.debug('pathlib is not installed.')
from zipfile import ZipFile, ZIP_DEFLATED
from .platforms import python_version, which_platform

def zipPath(resource, destination='', latest=False):
    # Create name of new zip file, based on original folder or file name
    resource = resource.rstrip('\\').rstrip('/')
    # if resource in destination: TranxFerLogger.warning('Loop: Save somewhere else!')
    
    if not path.exists(resource):
        TranxFerLogger.error(resource, 'does not exist')
        return
    
    if destination:
        if path.isdir(destination):
            baseFileName = path.basename(resource) + '.zip'
            zipFileName = path.join(destination, baseFileName)
        else: zipFileName = destination

    else: zipFileName = resource + '.zip'
    
    if path.isdir(resource): zipRootDir = path.basename(resource)
    
    if (path.isfile(zipFileName) == True) and (latest == False):
        TranxFerLogger.debug('ZipFileName %s Already exist'%zipFileName)
        return zipFileName
    
    # Create zip file
    with ZipFile(zipFileName, "w", compression=ZIP_DEFLATED) as zipFile:
        if path.isdir(resource):
            for root, dirs, files in walk(resource):
               for file in files:
                   filename = path.join(root, file)
                   arc = root.replace(resource, zipRootDir)
                   arcname = path.join(arc, file)
                   zipFile.write(filename, arcname, ZIP_DEFLATED)
        else: zipFile.write(resource, zipFileName, ZIP_DEFLATED)
    return zipFileName

class Mixin:
    
    def __repr__(self): return str(self)
    
    def decimalPlace(self, num, place=1):
        num = float(num)
        numStr = str(num) + '0'
        endIndex = numStr.index('.') + place + 1
        return numStr[:endIndex]

    def approximate(self, num, size=1):
        assert size > 0
        strNum = str(num)
        listNum = list(strNum)
        if len(listNum) <= 3: return num
        app = listNum[size]
        
        listNum[size:] = ['0' for _ in range(size, len(listNum))]
        add = 0 if int(app) < 5 else 1
        adx = int(listNum[size - 1]) + add
        listNum[size - 1] = str(adx)
        retur = ''.join(listNum)
        return int(retur)
    
    def stripZeros(self, num, app=1):
        num = self.approximate(num, app)
        strNum = str(num)
        listNum = list(strNum)
        return strNum.strip('0')

class PathStat(Mixin):
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
            if self.zipped: return path.getsize(self.zipName)
            elif self.isDir: return self.innerSize
            elif self.isFile: return path.getsize(self.fullName)
        # else: return self.dicts['size']

    @property
    def zipName(self): return self.fullName + '.zip'
    
    @property
    def pathFromRoot(self): 
        if self.__pathFromRoot:
            try: return str(self.__pathFromRoot.pathFromRoot)
            except: return str(self.__pathFromRoot)
        return str(self.name)
    @property
    def exists(self): return path.exists(self.fullName)
    
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
        if self.compress:
            isFile, isDir = True, False
            pathFromRoot = name = path.basename(self.zipName)
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
            if path.isabs(self.path): fn = path.abspath(self.path)
            else: fn = path.join(getcwd(), self.givenPath)
        
        else:
            if self.path.is_absolute(): fn = self.path.resolve()
            else: fn = path.join(self.path.cwd(), self.givenPath)
        return str(fn)
        
    @property
    def bytesDicts(self):
        dump = dumps(self.dicts).encode()
        return dump
    
    @property
    def type(self):
        if self.isFile: return path.splitext(self.fullName)[-1]
        elif self.isDir: return self.isFolder
    @property
    def fullType(self):
        fileTypes = {'.aif' : 'AIF audio file', '.cda' : 'CD audio track file', '.mid' : 'MIDI audio file.', '.midi' : 'MIDI audio file.', '.mp3' : 'MP3 audio file', '.mpa' : 'MPEG-2 audio file', '.ogg' : 'Ogg Vorbis audio file', '.wav' : 'WAV file', '.wma' : 'WMA audio file', '.wpl' : 'Windows Media Player playlist', '.7z' : '7-Zip compressed file', '.arj' : 'ARJ compressed file', '.deb' : 'Debian software package file', '.pkg' : 'Package file', '.rar' : 'RAR file', '.rpm' : 'Red Hat Package Manager', '.tar' : 'Tarball compressed file', '.gz': 'Tarball compressed file', '.z' : 'Z compressed file', '.zip' : 'Zip compressed file', '.bin' : 'Binary disc image', '.dmg' : 'macOS X disk image', '.iso' : 'ISO disc image', '.toast' : 'Toast disc image', '.vcd' : 'Virtual CD', '.csv' : 'Comma separated value file', '.dat' : 'Data file', '.db' : 'Database file', '.dbf' : 'Database file', '.log' : 'Log file', '.mdb' : 'Microsoft Access database file', '.sav' : 'Save file (e.g., game save file)', '.sql' : 'SQL database file', '.tar' : 'Linux / Unix tarball file archive', '.xml' : 'XML file', '.email' : 'Outlook Express e-mail message file.', '.eml' : 'E-mail message file from multiple e-mail clients, including Gmail.', '.emlx' : 'Apple Mail e-mail file.', '.msg' : 'Microsoft Outlook e-mail message file.', '.oft' : 'Microsoft Outlook e-mail template file.', '.ost' : 'Microsoft Outlook offline e-mail storage file.', '.pst' : 'Microsoft Outlook e-mail storage file.', '.vcf' : 'E-mail contact file.', '.apk' : 'Android package file', '.bat' : 'Batch file', '.bin' : 'Binary file', '.cgi' : 'Perl script file', '.pl' : 'Perl script file', '.com' : 'MS-DOS command file', '.exe' : 'Executable file', '.gadget' : 'Windows gadget', '.jar' : 'Java Archive file', '.msi' : 'Windows installer package', '.py' : 'Python file', '.wsf' : 'Windows Script File', '.fnt' : 'Windows font file', '.fon' : 'Generic font file', '.otf' : 'Open type font file', '.ttf' : 'TrueType font file', '.ai' : 'Adobe Illustrator file', '.bmp' : 'Bitmap image', '.gif' : 'GIF image', '.ico' : 'Icon file', '.jpeg' : 'JPEG image', '.jpg' : 'JPEG image', '.png' : 'PNG image', '.PNG' : 'PNG image', '.ps' : 'PostScript file', '.psd' : 'PSD image', '.svg' : 'Scalable Vector Graphics file', '.tif' : 'TIFF image', '.tiff' : 'TIFF image', '.asp' : 'Active Server Page file', '.aspx' : 'Active Server Page file', '.cer' : 'Internet security certificate', '.cfm' : 'ColdFusion Markup file', '.cgi' : 'Perl script file', '.pl' : 'Perl script file', '.css' : 'Cascading Style Sheet file', '.htm' : 'HTML file', '.html' : 'HTML file', '.js' : 'JavaScript file', '.jsp' : 'Java Server Page file', '.part' : 'Partially downloaded file', '.php' : 'PHP file', '.py' : 'Python file', '.rss' : 'RSS file', '.xhtml' : 'XHTML file', '.key' : 'Keynote presentation', '.odp' : 'OpenOffice Impress presentation file', '.pps' : 'PowerPoint slide show', '.ppt' : 'PowerPoint presentation', '.pptx' : 'PowerPoint Open XML presentation', '.c' : 'C and C++ source code file', '.class' : 'Java class file', '.cpp' : 'C++ source code file', '.cs' : 'Visual C# source code file', '.h' : 'C, C++, and Objective-C header file', '.hpp' : 'C, C++, and Objective-C header file', '.java' : 'Java Source code file', '.pl' : 'Perl script file.', '.sh' : 'Bash shell script', '.swift' : 'Swift source code file', '.vb' : 'Visual Basic file', '.ods' : 'OpenOffice Calc spreadsheet file', '.xls' : 'Microsoft Excel file', '.xlsm' : 'Microsoft Excel file with macros', '.xlsx' : 'Microsoft Excel Open XML spreadsheet file', '.bak' : 'Backup file', '.cab' : 'Windows Cabinet file', '.cfg' : 'Configuration file', '.cpl' : 'Windows Control panel file', '.cur' : 'Windows cursor file', '.dll' : 'DLL file', '.dmp' : 'Dump file', '.drv' : 'Device driver file', '.icns' : 'macOS X icon resource file', '.ico' : 'Icon file', '.ini' : 'Initialization file', '.lnk' : 'Windows shortcut file', '.msi' : 'Windows installer package', '.sys' : 'Windows system file', '.tmp' : 'Temporary file', '.3g2' : '3GPP2 multimedia file', '.3gp' : '3GPP multimedia file', '.avi' : 'AVI file', '.flv' : 'Adobe Flash file', '.h264' : 'H.264 video file', '.m4v' : 'Apple MP4 video file', '.mkv' : 'Matroska Multimedia Container', '.mov' : 'Apple QuickTime movie file', '.mp4' : 'MPEG4 video file', '.mpg' : 'MPEG video file', '.mpeg' : 'MPEG video file', '.rm' : 'RealMedia file', '.swf' : 'Shockwave flash file', '.vob' : 'DVD Video Object', '.wmv' : 'Windows Media Video file', '.doc' : 'Microsoft Word file', '.docx' : 'Microsoft Word file', '.odt' : 'OpenOffice Writer document file', '.pdf' : 'PDF file', '.rtf' : 'Rich Text Format', '.tex' : 'A LaTeX document file', '.txt' : 'Plain text file', '.wpd' : 'WordPerfect document', self.isFolder : 'Directory'}
        return fileTypes[self.type.lower()]
    
    def open(self, pr='rb'):
        if (self.openFile == None):
            # if self.isRemote:

            p = self.turnToZip()
            if self.isFile:
                self.openFile = open(p, pr)
                self.opened = True
                
            elif self.isDir:
                if self.isRemote:
                    m = 'A Directory %s can not be opened.'%self.name
                    TranxFerLogger.error(m)
                    raise OSError(m)
                self.openFile = open(p, pr)
            return self.openFile
        
        else: TranxFerLogger.error('Path is currently opened.')
    
    def close(self):
        if self.openFile != None:
            self.openFile.close()
            self.openFile = None
        else: TranxFerLogger.error('Path is not currently opened.')
    
    def delete(self):
        if self.zipped: remove(self.zipName)
    
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
            for r, ds, fs in walk(self.fullName):
                for f in fs:
                    self.filesCount += 1
                    self.innerSize += path.getsize(path.join(r, f))
                for d in ds: self.dirsCount += 1
    
    def formatTime(self, time='c', full=0):
        strT = '%A, %B %d, %Y, %I:%M:%S %p' if full else '%d/%m/%Y, %H:%M:%S'
        if time in ['a', 'c', 'm']:
            if time == 'a': tm = self.atime
            elif time == 'c': tm = self.ctime
            elif time == 'm': tm = self.mtime
            return datetime.fromtimestamp(tm).strftime(strT)
        
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
            TranxFerLogger.info('Started Zipping %s.'%self.fullName)
            if self.zipped == False and self.isRemote == False:
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
        
        if path_ == '.': path_ = getcwd()
        
        if python_version() == 2:
            self.path = path_
            self.name = path.basename(self.path)
        else:
            self.path = Path(path_)
            self.name = self.path.name
        
        if self.exists:
            if python_version() == 2:
                self.stat = stat(self.path)
                self.isFile = path.isfile(self.path)
                self.isDir = path.isdir(self.path)
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
        np = p.replace(path.dirname(s),'').strip('\\').strip('/')
        if obj: return LocalPathStat(path_, np)
        return np

    def folders(self):
        if self.compress: yield None
        for r, ds, fs in walk(self.fullName):
            for d in ds:
                dd = path.join(r, d)
                yield LocalPathStat(dd, self.asRoot(dd))
    
    def files(self):
        if self.compress: yield None
        for r, ds, fs in walk(self.fullName):
            for f in fs:
                fd = path.join(r, f)
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
        
        dicts = loads(details)
        
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
                pth = path.join(self.dest, folder)
                
                try: makedirs(pth)
                except Exception as error: TranxFerLogger.critical(error)
        else:
            dirs = path.dirname(self.pathFromRoot)
            if dirs:
                try: makedirs(path.join(self.dest, dirs))
                except: pass
    
    @property
    def fullName(self): return path.join(self.dest, self.pathFromRoot)
