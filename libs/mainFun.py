#coding:utf-8
import wx
import threading
import subprocess,re
import shutil,os,time
import pysvn
import logging
import cPickle as pickle
import logHandler as LoadLog
import globalDef as GL

class MainFun(object):
    def __init__(self,LIPaddr,GlogDir,SvnUrl,SvnWorkDir,SvnUser,SvnPass,SvnLogUrl,sysLogName,
                 num=1,netLoopTime=30000,syncLoopTime=1800000):
        self.client = pysvn.Client()
        self.LIPaddr = LIPaddr
        self.GlogDir = GlogDir
        self.SvnUrl =SvnUrl
        self.SvnWorkDir = SvnWorkDir
        self.SvnUser = SvnUser
        self.SvnPass = SvnPass
        self.SvnLogUrl = SvnLogUrl
        self.sysLogName = sysLogName
        self.num = num
        self.netLoopTime = netLoopTime
        self.syncLoopTime = syncLoopTime
        self.checkDir()

        #print self.SvnUser
        #print self.SvnPass

    def checkDir(self):
        if not os.path.exists(GL.LogDir):
            try:
                os.mkdir(GL.LogDir)
            except:
                pass
        if not os.path.exists(GL.dataDir):
            try:
                os.mkdir(GL.dataDir)
            except:
                pass

        if not os.path.exists(self.GlogDir):
            LoadLog.LogMsg(self.sysLogName.info,u"全局日志目录不存在")
            netcheck = self.ping(self.num)
            if netcheck is True:
                #print "netcheck",netcheck
                try:
                    self.client.callback_get_login = self.get_login
                    LoadLog.LogMsg(self.sysLogName.info,u"Checkout 全局日志 %s " % self.GlogDir)
                    self.client.checkout(self.SvnLogUrl,self.GlogDir)
                    #self.client.checkout("http://192.168.2.16/svn",self.GlogDir)
                except:
                    LoadLog.LogMsg(self.sysLogName.error,u"全局日志 %s 文件夹checkout出错" % self.GlogDir)
                    return True
            else:
                LoadLog.LogMsg(self.sysLogName.warning,u"无法 ping 通 IP %s" % self.LIPaddr)

    def initSvnLogDir(self):
        self.checkDir()
        try:
            entry = self.client.info(self.GlogDir)
            #print "entry:",entry.url
            #print "SvnLogUrl:",self.SvnLogUrl
            if entry.url != self.SvnLogUrl:
                LoadLog.LogMsg(self.sysLogName.info,u"检测到全局日志%s有问题" % self.GlogDir)
                LoadLog.LogMsg(self.sysLogName.info,u"删除全局日志 %s " % self.GlogDir)
                self.CleanDir(self.GlogDir)
                try:
                    netheck = self.ping(self.num)
                    if netheck is True:
                        LoadLog.LogMsg(self.sysLogName.info,u"重新Checkout 全局日志 %s " % self.GlogDir)
                        self.client.checkout(self.SvnLogUrl,self.GlogDir)
                except:
                    LoadLog.LogMsg(self.sysLogName.error,u"网络不正常，checkout全局日志出错" % self.GlogDir)
                    GL.NetStatus = u"断开"
                    return True
            else:
                return False
        except:
            return False


    def ping(self,num):
        ping = subprocess.Popen(["ping", "-n", str(num), self.LIPaddr], shell=True, stdout = subprocess.PIPE)
        out, error = ping.communicate()
        try:
            m = re.search(r".*TTL=\d+",out.decode("GB2312"))
        except:
            #print "ping error"
            pass
        else:
            if m is not None:
                #print "正常"
                GL.NetStatus = u"正常"
                return True
            else:
                GL.NetStatus = u"断开"
                return False

    def LoopDoMonitor(self):
        self.ping(self.num)
        wx.CallLater(self.netLoopTime,self.LoopDoMonitor)

    def writeGlobal_log(self,logdataList,handle,logName,logPanel):
        #print "write user:",self.SvnUser
        self.client.callback_get_login = self.get_login
        Login,loginMsg = self.AuthUserPass(self.SvnLogUrl,self.SvnUser,self.SvnPass)
        if Login is False:
            #wx.MessageBox(loginMsg,u"错误提示", style=wx.OK|wx.ICON_ERROR)
            LoadLog.LogMsg(self.sysLogName.error,loginMsg)
            raise  ValueError,loginMsg
        try:
            self.client.update(self.GlogDir)
        except:
            try:
                self.client.cleanup(self.GlogDir)
                self.client.update(self.GlogDir)
            except:
                LoadLog.LogMsg(self.sysLogName.error,u"全局日志更新出错")
                return
        tstr = time.strftime('%Y-%m-%d %H:%M:%S')
        msg = "\n".join(logdataList)
        if logPanel == "publish":
            msg2 = u"更新了如下文件："
        elif logPanel == "backup":
            msg2 = u"备份了如下文件："
        else:
            msg2 = u"还原了如下文件："

        myformat = u"######## %s [%s] %s ########\n%s\n" %(tstr,self.SvnUser,msg2,msg)
        handle.setFormatter(logging.Formatter(myformat))
        LoadLog.LogMsg(logName.info,msg)
        self.CommitToSvn(GL.GlogDir)

    def CleanDir(self,delDir):
        if os.path.isdir(delDir):
            paths = os.listdir(delDir)
            for path in paths:
                filePath = os.path.join(delDir, path )
                if os.path.isfile( filePath ):
                    try:
                        os.remove(filePath)
                    except os.error:
                        pass
                elif os.path.isdir( filePath ):
                    if filePath[-4:].lower() == ".svn".lower():
                        continue
                    shutil.rmtree(filePath,True)
        return True

    def CheckSvnFile(self,svnDir):
        allCommitList = []
        changes = self.client.status(svnDir)

        list_added =  [f.path for f in changes if f.text_status == pysvn.wc_status_kind.added]
        list_missing =  [f.path for f in changes if f.text_status == pysvn.wc_status_kind.missing]
        list_removed =  [f.path for f in changes if f.text_status == pysvn.wc_status_kind.deleted]
        list_modified =  [f.path for f in changes if f.text_status == pysvn.wc_status_kind.modified]
        list_conflicted = [f.path for f in changes if f.text_status == pysvn.wc_status_kind.conflicted]
        list_unversioned =  [f.path for f in changes if f.text_status == pysvn.wc_status_kind.unversioned]


        [ allCommitList.append([efile,"non-versioned"]) for efile in list_unversioned if len(list_unversioned) != 0 ]
        [ allCommitList.append([efile,"added"]) for efile in list_added if len(list_added) != 0 ]
        [ allCommitList.append([efile,"missing"]) for efile in list_missing if len(list_missing) != 0 ]
        [ allCommitList.append([efile,"modified"]) for efile in list_modified if len(list_modified) != 0 ]
        [ allCommitList.append([efile,"removed"]) for efile in list_removed if len(list_removed) != 0 ]
        [ allCommitList.append([efile,"conflicted"]) for efile in list_conflicted  if len(list_conflicted) != 0 ]
        #print allCommitList

        return allCommitList

    def AuthUserPass(self,url,username,password):
        import urllib2,base64
        base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
        authheader =  "Basic %s" % base64string
        req = urllib2.Request(url,data=None,headers={"Authorization": authheader})
        try:
            urllib2.urlopen(req,timeout=2)
        except urllib2.HTTPError, e:
            if e.code == 401:
                msg = u"SVN认证失败,错误信息 %s" %e
                Login = False
            else:
                msg = u"SVN其它错误,%s" %e
                Login = False
        except:
            msg = u"SVN验证失败."
            Login = False
        else:
            msg = u"SVN认证通过"
            Login = True
        return Login,msg

    def get_login(self, realm, username,may_save):
        data = (True,self.SvnUser,self.SvnPass, False)
        return data

    def CommitToSvn(self,svnDir):
        try:
            f = open(GL.global_backup_logfile,"r")
            f.close()
            f = open(GL.gloabl_publish_logfile,"r")
            f.close()
        except:
            pass
        #time.sleep(1)
        #self.allCommitList = []
        #self.client.update(svnDir)
        #Login,loginMsg = self.AuthUserPass(self.SvnLogUrl,self.SvnUser,self.SvnPass)
        self.allCommitList = self.CheckSvnFile(svnDir)
        #print self.allCommitList

        for itemvalues in self.allCommitList:
        #for itemvalues in allCommitList:
            if itemvalues[1] == "conflicted":
                LoadLog.LogMsg(self.sysLogName.warning,u"有svn冲突文件,请用TortoiseSVN操作")
                return
            if itemvalues[1] == "non-versioned":
                self.client.add(itemvalues[0])
            if itemvalues[1] == "missing":
                self.client.remove(itemvalues[0])

            self.client.checkin(itemvalues[0]," ")

        #self.client.checkin(svnDir," ")

    def TimeSync(self,ntpServers):
        import ntplib
        c = ntplib.NTPClient()
        if len(ntpServers) == 0:
            return
        ntpServers = ntpServers.split(",")
        for ntpServer in ntpServers:
            try:
                response = c.request(ntpServer)
            except ntplib.NTPException,e:
                if  ntpServer == ntpServers[-1]:
                    msg = u"无法同步时间，请检测本地时间是否正确."
                    LoadLog.LogMsg(self.sysLogName.warning,msg)
                    break
                else:
                    continue
            except:
                pass
            else:
                ts = response.tx_time
                _date = time.strftime('%Y-%m-%d',time.localtime(ts))
                _time = time.strftime('%X',time.localtime(ts))
                #os.system('date {} && time {}'.format(_date,_time))
                subprocess.Popen(['date {} && time {}'.format(_date,_time)], shell=True, stdout = subprocess.PIPE)
                #return ts,_date,_time

    def TimeSyncLoop(self,ntpServer):
        self.TimeSync(ntpServer)
        wx.CallLater(self.syncLoopTime,self.TimeSyncLoop,ntpServer)

    def isRegedit(self,public_key,str_key,RegisterFile):
        import readHardware
        try:
            with open(RegisterFile,"rb",-1) as f:
                rCode = pickle.load(f)
        except:
            rCode = ""
        machineCode = str(readHardware.get_disk_info(str_key)).lstrip("-")
        if len(rCode) != 0:
            deMachineCode = str(readHardware.DencryptForRegCode(rCode,public_key))
            if deMachineCode == machineCode:
                GL.Active = True
            else:
                GL.Active = False
    def OnSvnCommit(self):
        from svnUI import SvnCommitUI
        dialog = SvnCommitUI(self.SvnUser,self.SvnPass,self.SvnUrl,self.SvnWorkDir,u"SVN文件提交",(500, 350))
        dialog.Center()
        dialog.ShowModal()
        #self.SvnCommitBtn.Enable(True)
        #dialog.Destroy()

    def OnSvnUpdate(self):
        dlgPrompt = wx.MessageBox(u"你确定要更新SVN操作吗?", u"确认提示", style=wx.YES_NO|wx.YES_DEFAULT|wx.ICON_INFORMATION)
        if dlgPrompt == wx.YES:
            from svnUI import SvnUpdateUI
            dialog = SvnUpdateUI(self.SvnUser,self.SvnPass,self.SvnUrl,self.SvnWorkDir,u"SVN更新",(450,380))
            dialog.Center()
            dialog.ShowModal()
            dialog.Destroy()

    def RefreshLog(self):
        self.client.callback_get_login = self.get_login
        Login,loginMsg = self.AuthUserPass(self.SvnLogUrl,self.SvnUser,self.SvnPass)
        if Login is False:
            wx.MessageBox(loginMsg,u"错误提示", style=wx.OK|wx.ICON_ERROR)
            LoadLog.LogMsg(self.sysLogName.error,loginMsg)
            return
        try:
            self.client.update(self.GlogDir)
            wx.MessageBox(u"完成全局日志同步到本地",u"提示", style=wx.OK|wx.ICON_INFORMATION)
            LoadLog.LogMsg(self.sysLogName.info,u"完成全局日志同步到本地")
            time.sleep(2)
        except:
            try:
                self.client.cleanup(self.GlogDir)
                self.client.update(self.GlogDir)
                wx.MessageBox(u"完成全局日志更新到本地",u"提示", style=wx.OK|wx.ICON_INFORMATION)
                LoadLog.LogMsg(self.sysLogName.info,u"完成全局日志同步到本地")
                time.sleep(2)
            except:
                msg = u"全局日志更新出错"
                wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
                LoadLog.LogMsg(self.sysLogName.error,msg)


class WorkerThread(threading.Thread):
    """
    This just simulates some long-running task that periodically sends
    a message to the GUI thread.
    """
    def __init__(self,window,threadName,tree=None,treeid=None,rootdir=None,
                 ntpServers=None,
                 public_key=None,str_key=None,RegisterFile=None):
        threading.Thread.__init__(self)
        self.window = window
        self.threadName = threadName
        self.tree = tree
        self.treeid = treeid
        self.rootdir = rootdir
        self.ntpServers = ntpServers
        self.public_key= public_key
        self.str_key = str_key
        self.RegisterFile = RegisterFile

    def run(self):#运行一个线程

        if self.threadName == "timesync":
            time.sleep(1)
            wx.CallAfter(self.window.TimeSyncLoop,self.ntpServers)
        elif self.threadName == "appendir":
            time.sleep(0.5) # 休眠0.1秒
            wx.CallAfter(self.window.AppenDir,self.tree,self.treeid,self.rootdir)
        elif self.threadName == "regedit":
            time.sleep(1)
            wx.CallAfter(self.window.isRegedit,self.public_key,self.str_key,self.RegisterFile)
        elif self.threadName == "svncommit":
            #time.sleep(0.1)
            wx.CallAfter(self.window.OnSvnCommit)
        elif self.threadName == "svnupdate":
            #time.sleep(0.1)
            wx.CallAfter(self.window.OnSvnUpdate)
        # elif self.threadName == "publishEntry":
        #     wx.CallAfter(self.window.OnPublishEntry)
        # elif self.threadName == "publishText":
        #     wx.CallAfter(self.window.OnPublishEntry)
        elif self.threadName == "initsvnlogdir":
            time.sleep(1)
            wx.CallAfter(self.window.initSvnLogDir)
        elif self.threadName == "monitornet":
            time.sleep(1)
            wx.CallAfter(self.window.LoopDoMonitor)
        elif self.threadName == "refreshlog":
            time.sleep(1)
            wx.CallAfter(self.window.RefreshLog)
        else:
            pass