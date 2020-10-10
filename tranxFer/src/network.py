import subprocess, multiprocessing
from .pathstats import Mixin
from .platforms import get_os_name, python_version, os

class NetworkMixin(Mixin):
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
