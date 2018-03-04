#coding:utf-8
version = 1.0
import wx
import logging,os
import logging.handlers
from loadConfig import ReadAllConf,ReadSSHAuthFile
from passEncrypt import GetKey,DecodeAES
from mainFun import MainFun

OpenDirID = wx.NewId()
MenuSettingID = wx.NewId()
ExitID = wx.NewId()
TreeID = wx.NewId()
LogViewID = wx.NewId()
ProgramUpdateID = wx.NewId()
SvnUpdateID = wx.NewId()
HelpID = wx.NewId()
Add_Entry_ID = wx.NewId()
Clear_All_Entry_ID = wx.NewId()
Clear_All_Text_ID = wx.NewId()
Remove_Entry_ID = wx.NewId()
PublishToolID = wx.NewId()
PublishID = wx.NewId()
PublishMenuID = wx.NewId()
PublishTextMenuID = wx.NewId()
RollBackID = wx.NewId()
RegisterID = wx.NewId()
Register_Cancel_ID = wx.NewId()
RegCodeTextID = wx.NewId()
MenuRegisterID = wx.NewId()
RefreshTreeDirID = wx.NewId()
GetUserNameUID = wx.NewId()
GetPasswordID = wx.NewId()
RememberCheckBoxID = wx.NewId()
MenuAboutID = wx.NewId()
Commit_OK_ID = wx.NewId()
Commit_Cancel_ID = wx.NewId()
SvnCommitID = wx.NewId()
SvnUpdateID = wx.NewId()
Update_OK_ID = wx.NewId()
SettingOK = wx.NewId()
GlobalLogID = wx.NewId()
popupID_Copy = wx.NewId()
popupID_Remove = wx.NewId()
ShowWinID = wx.NewId()
SetUIOpenDirID = wx.NewId()
DefaultDataID = wx.NewId()
SvnDirViewID = wx.NewId()
GLogViewID = wx.NewId()
RefreshLogID = wx.NewId()
CommitSvnOK = wx.NewId()

public_key = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCaGOAQ+XdZhbpOot5KAGS4Hfms
/ELpv8kgNazBEADUT/65Xq3BH4c9XwFnDnfLSiGf1Nbiw8V406OYzvugCmYdcs8T
qEpkquGdfT0QgTKf5SLtyOLI1bq2rkZmn1Vqs0MKes884RUy5eCZDH0WN2QY3fEM
oiiJVPhiKSnIgpnCRQIDAQAB
-----END PUBLIC KEY-----
"""
pass_private_key = """
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCrE1yvqcwvqL1hWPHzA6PnMBvqKvUXuzw6LyHrYRT7A7+Y4fft
ef5Q+F0sRQZ2p2Q2q76IhdxL6zGx0crLPyAseNsd/KuKR+AlYaE9nBUHGCnT7BPs
wk0yMFAlY4iGf9rH+rB+lNI0qDyY5gVJRs/qDJBP3UodY0FR3XsqmZPkGwIDAQAB
AoGADnt5ITXSn0Y9ofwRn2zzdyLPeidg0D19f791s6NoT0el9J9MicIGEXy1BoZh
YbIR/b7URmJun86tSkxkSohxhK7XzAZ5HszOODN3AA3Jp1nFbwSQfH6RO1igBfHc
rD0FU9m5oFpqimwv8nekVXwkuaIqP0lhugcx4AszcspzykECQQDRSItNh103BZkq
hU683ZkBKIeknvTBhhqozkn7RNp9SEh2Kj705iOQxVItmDZfHP5DSkMdRhsoy7UC
YJQ//loZAkEA0UNxucsncJlZAumRQhFbGweJduofXD7KSv8/LFexeBJdma6S3UAx
RAXTwGr914oMgapjszvGwQQi/UXenTPeUwJAEfdCTiOCswh9/5J2EeyMB/dsvYsP
w9U5UKh03WcpwnuEDPDPesKO5wypY1SfxkZ85VXosQilqDjkjxGvaFbzcQJAEjkI
T0CUp6aC7NEAGDvArkLiwpsyreq93PgLPUZJqwYWZoqgOWocoCrNvMTUZA+edTAs
THBZJ3e/wER0VUYuBwJBANANUT2wRCEOlyCIiFxigU1DrWOW68+y2q7iJ1QJS9nf
xMSFMucvpKk3I+rsP+DhVtV3Iqqyi3XZgqH2diFhg7A=
-----END RSA PRIVATE KEY-----
"""

pass_public_key = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCrE1yvqcwvqL1hWPHzA6PnMBvq
KvUXuzw6LyHrYRT7A7+Y4fftef5Q+F0sRQZ2p2Q2q76IhdxL6zGx0crLPyAseNsd
/KuKR+AlYaE9nBUHGCnT7BPswk0yMFAlY4iGf9rH+rB+lNI0qDyY5gVJRs/qDJBP
3UodY0FR3XsqmZPkGwIDAQAB
-----END PUBLIC KEY-----
"""

str_key = "www.usportnews.com+publish45"
dataDir = "data"
AuthFile = "%s/AuthFile.db" %dataDir
BackupDir = "/backup/www"
ConfFile = "setting.ini"
RegisterFile = "%s/Register.db" %dataDir
Active = False

LOG_MAX_BYTES = 1 * 1024 * 1024
FILE_LOG_LEVEL = "info"
CONSOLE_LOG_LEVEL = "info"
BACKUP_COUNT = 5
loadGUpdateLog = True
loadGBackupLog = True
SPLASH_TIME = 2000
#formatter = logging.Formatter('%(asctime)s [ %(levelname) ][%(lineno)]   %(message)s')
#formatter = logging.Formatter('%(asctime)s - %(levelname) - %(message)s')
formatter = logging.Formatter('%(asctime)s  - %(levelname)s - %(message)s')
start = 0
NetStatus = u"正常"

LogDir = "logs"
GlogDir = "Glogs"
MonitorDir = "/data/www/monitor"
Monitor_Upload_File = "%s/uploadBlock.conf" % MonitorDir
publish_logfile = "%s/publish.log" % LogDir
backup_logfile = "%s/backup.log" % LogDir
gloabl_publish_logfile = "%s/global_publish.log" % GlogDir
global_backup_logfile = "%s/global_backup.log" % GlogDir
system_logfile = "%s/system.log" % LogDir

backup_list = []
PublishList = []
rollbacked_list = []

sections = ['BaseConfig','SVNConfig',"LocalServer","RemoteServer"]

DefaultConfDict = {
                   "BaseConfig":
                       {"authstart":"True","update":"True"},
                   "SVNConfig":
                       {"SvnUrl":"http://192.168.2.15:8080/svn/usport","SvnWorkDir":"D:\\usport","SvnUser":"username","SvnPass":"12345678","isSave":"True"},
                   "LocalServer":
                       {"LocalWebDir":"/data/www/usport/","IPaddr":"192.168.2.15","Port":"2215","username":"","timeout":"5"},
                   "RemoteServer":
                       {"RemoteWebDir":"/opt/phproot/wwwroot/www/","IPaddr":"192.168.11.4","Port":"7991","timeout":"5"},
                   "LogConfig":
                       {"SvnLogUrl": "http://192.168.2.15:8080/svn/Glogs","GlogDir":"Glogs","ntpServer":"pool.ntp.org,time.windows.com"}
                   }

EncryptConfDict = ReadAllConf(ConfFile,sections,DefaultConfDict)
#print EncryptConfDict
sshAuthDict = ReadSSHAuthFile(AuthFile,str_key,pass_public_key,"password")
sshPass = sshAuthDict["password"]

cipher = GetKey(str_key)

try:
    SvnUrl = EncryptConfDict["SVNConfig"]["SvnUrl"]
except:
    SvnUrl = DefaultConfDict["SVNConfig"]["SvnUrl"]

try:
    SvnWorkDir = EncryptConfDict["SVNConfig"]["SvnWorkDir"]
except:
    SvnWorkDir = DefaultConfDict["SVNConfig"]["SvnWorkDir"]

try:
    SvnUser = EncryptConfDict["SVNConfig"]["SvnUser"]
except:
    SvnUser = DefaultConfDict["SVNConfig"]["SvnUser"]
try:
    enSvnPass = EncryptConfDict["SVNConfig"]["SvnPass"]
    SvnPass = DecodeAES(cipher,enSvnPass,32)
except:
    SvnPass = DefaultConfDict["SVNConfig"]["SvnPass"]

isSave = True

try:
    webDir = EncryptConfDict["LocalServer"]["LocalWebDir"]
except:
    webDir = DefaultConfDict["LocalServer"]["LocalWebDir"]
try:
    LIPaddr = EncryptConfDict["LocalServer"]["IPaddr"]
except:
    LIPaddr = DefaultConfDict["LocalServer"]["IPaddr"]

try:
    LPort = int(EncryptConfDict["LocalServer"]["Port"])
except:
    LPort = int(DefaultConfDict["LocalServer"]["Port"])
try:
    sshUser = EncryptConfDict["LocalServer"]["username"]
    sshUser = DecodeAES(cipher,sshUser,32)
except:
    sshUser = DefaultConfDict["LocalServer"]["username"]

try:
    sshTimeout = EncryptConfDict["LocalServer"]["timeout"]
except:
    sshTimeout = DefaultConfDict["LocalServer"]["timeout"]

try:
    RwebDir = EncryptConfDict["RemoteServer"]["RemoteWebDir"]
except:
    RwebDir = DefaultConfDict["RemoteServer"]["RemoteWebDir"]

try:
    RIPaddr = EncryptConfDict["RemoteServer"]["IPaddr"]
    RIPaddr = DecodeAES(cipher,RIPaddr,32)
except:
    RIPaddr = DefaultConfDict["RemoteServer"]["IPaddr"]

try:
    RPort = EncryptConfDict["RemoteServer"]["Port"]
    RPort = int(DecodeAES(cipher,RPort,32))
except:
    RPort = DefaultConfDict["RemoteServer"]["Port"]

try:
    RsshTimeout = EncryptConfDict["RemoteServer"]["timeout"]
except:
    RsshTimeout = DefaultConfDict["RemoteServer"]["timeout"]

try:
    SvnLogUrl = EncryptConfDict["LogConfig"]["SvnLogUrl"]
except:
    SvnLogUrl = DefaultConfDict["LogConfig"]["SvnLogUrl"]

try:
    GlogDir = EncryptConfDict["LogConfig"]["GlogDir"]
except:
    GlogDir = DefaultConfDict["LogConfig"]["GlogDir"]

try:
    ntpServer = EncryptConfDict["LogConfig"]["ntpServer"]
except:
    ntpServer = DefaultConfDict["LogConfig"]["ntpServer"]

logger_PubLog = logging.getLogger("publish_log")
logger_BakLog = logging.getLogger("backup_log")
logger_gPubLog = logging.getLogger("gpublish_log")
logger_gBakLog = logging.getLogger("gbackup_log")
logger_sysLog = logging.getLogger("system_log")

GlogDirError = MainFun(LIPaddr,GlogDir,SvnUrl,SvnWorkDir,SvnUser,SvnPass,SvnLogUrl,logger_sysLog).initSvnLogDir()

ehandlers = logging.handlers.RotatingFileHandler(system_logfile,maxBytes=LOG_MAX_BYTES,backupCount=BACKUP_COUNT,)
ehandlers.setFormatter(formatter)

ahandlers = logging.handlers.RotatingFileHandler(publish_logfile,maxBytes=LOG_MAX_BYTES,backupCount=BACKUP_COUNT,)
ahandlers.setFormatter(formatter)
bhandlers = logging.handlers.RotatingFileHandler(backup_logfile,maxBytes=LOG_MAX_BYTES,backupCount=BACKUP_COUNT,)
bhandlers.setFormatter(formatter)
logger_PubLog.addHandler(ahandlers)
logger_PubLog.setLevel(logging.INFO)

logger_BakLog.addHandler(bhandlers)
logger_BakLog.setLevel(logging.INFO)

logger_sysLog.addHandler(ehandlers)
logger_sysLog.setLevel(logging.INFO)

#print LIPaddr,GlogDir,SvnUrl,SvnWorkDir,SvnUser,SvnPass,SvnLogUrl,logger_sysLog


if GlogDirError is not True:
    chandlers = logging.handlers.RotatingFileHandler(gloabl_publish_logfile,maxBytes=LOG_MAX_BYTES,backupCount=BACKUP_COUNT,)
    logger_gPubLog.addHandler(chandlers)
    logger_gPubLog.setLevel(logging.INFO)
    dhandlers = logging.handlers.RotatingFileHandler(global_backup_logfile,maxBytes=LOG_MAX_BYTES,backupCount=BACKUP_COUNT,)
    logger_gBakLog.addHandler(dhandlers)
    logger_gBakLog.setLevel(logging.INFO)

