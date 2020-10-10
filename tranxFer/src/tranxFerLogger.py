import logging, traceback
from datetime import datetime

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
        # baks = traceback.format_stack()
        # for a in baks[-5:-3]: print(a)
        dt = datetime.now()
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

