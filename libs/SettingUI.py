#coding:utf-8
import  wx
import globalDef as GL
from passEncrypt import GetKey,EncodeAES
#from libs.useValidator import InputValidator

class SettingPanel(wx.Listbook):
    def __init__(self,parent):
        wx.Listbook.__init__(self, parent, wx.ID_ANY, style=wx.BK_DEFAULT)
        self.LogLevelList = ['debug','info','warning','error','critical']
        #self.confdict = confdict
        #self.sshAuthDict = sshAuthDict
        self.enkey = GL.str_key
        self.public_key = GL.pass_public_key
        self.private_key = GL.pass_private_key

        pages = [  (self.BaseSettingUI(), u" 基本设置  "),
                   (self.SvnUI(),      u" SVN配置  "),
                   (self.LocalUI(),     u" 本地服务  "),
                   (self.RemoteUI(),  u" 远程服务  "),
                   (self.LogSettingUI(),  u" 日志配置  "),
                 ]
        imID = 0
        for page, label in pages:
            self.AddPage(page, label, imageId=imID)
            imID += 1

        self.SetConfigDictOnUI()

    def BaseSettingUI(self):
        p = wx.Panel(self, -1)#子窗体的容器
        win=wx.Panel(p,-1)

        about_s = wx.StaticText(win,-1,u"基本设置")
        line = wx.StaticLine(win)
        self.startup_c = wx.CheckBox(win, label=u"随系统启动",id = wx.NewId())
        self.startup_c.Disable()
        #print "bool self.startup: ",self.startup
        self.minicon_c = wx.CheckBox(win, label=u"最小化系统托盘",id = wx.NewId())
        self.minicon_c.Disable()
        self.checkupdate_c = wx.CheckBox(win, label=u"自动检测更新",id = wx.NewId())
        self.checkupdate_c.Disable()
        self.defaultbtn = wx.Button(win,label=u"还原默认设置",size=(100,25),id=GL.DefaultDataID)

        sizer = wx.GridBagSizer(5,5)
        sizer.Add(about_s,pos=(0,0),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)
        sizer.Add(line,pos=(1,0),span=(1,3),flag=wx.EXPAND|wx.RIGHT|wx.LEFT|wx.TOP,border=5)
        sizer.Add(self.startup_c,pos=(2,0),span=(1,1),flag=wx.TOP|wx.LEFT|wx.EXPAND, border=10)
        sizer.Add(self.minicon_c,pos=(3,0),span=(1,1),flag=wx.TOP|wx.LEFT|wx.EXPAND, border=10)
        sizer.Add(self.checkupdate_c,pos=(4,0),span=(1,1),flag=wx.TOP|wx.LEFT|wx.EXPAND, border=10)
        sizer.Add(self.defaultbtn,pos=(5,0),span=(1,1),flag=wx.TOP|wx.LEFT|wx.EXPAND, border=10)
        sizer.AddGrowableCol(1,1)
        win.SetSizerAndFit(sizer)
        sizer.SetSizeHints(self)

        def OnCPSize(evt, win=win):
            win.SetPosition((0,0))
            win.SetSize(evt.GetSize())

        p.Bind(wx.EVT_SIZE, OnCPSize)
        # p.Bind(wx.EVT_CHECKBOX, self.OnBaseConfig, id=gen.ID_STARTUP)
        # p.Bind(wx.EVT_CHECKBOX, self.OnBaseConfig, id=gen.ID_MINICON)
        p.Bind(wx.EVT_BUTTON, self.OnDefaultData, id=GL.DefaultDataID)
        return p

    def OnDefaultData(self,event):
        defaultDlog = wx.MessageDialog(self,u"您确定要还原默认值吗？", u'确认提示',
                                            wx.YES_NO|wx.YES_NO|wx.ICON_INFORMATION)
        if defaultDlog.ShowModal() == wx.ID_YES:
            self.LoadDefault()
            self.SetConfigDictOnUI()
            wx.MessageBox(u"已还默认配置", u"提示", style=wx.ICON_INFORMATION)
            defaultDlog.Destroy()

    def SvnUI(self):
        p = wx.Panel(self, -1)#子窗体的容器
        win=wx.Panel(p,-1)
        ##控件
        about_s = wx.StaticText(win,-1,u"SVN设置")
        url_s = wx.StaticText(win,-1,u"URL 地址：")
        self.url_t  = wx.TextCtrl(win,size=(150,20),value="http://")
        self.url_t.SetMaxLength(50)

        svnWorkDir_s = wx.StaticText(win,-1,u"工作目录：")
        self.svnWorkDir_t = wx.TextCtrl(win,size=(150,20),style=wx.TE_READONLY)
        self.svnWorkDir_b = wx.Button(win,label=u"打开",size=(50,20),id=GL.SetUIOpenDirID)

        svnUser_s = wx.StaticText(win,-1,u"用户：")
        self.svnUser_t = wx.TextCtrl(win,size=(150,20))
        self.svnUser_t.SetMaxLength(10)

        svnPass_s = wx.StaticText(win,-1,u"密码：")
        self.svnPass_t = wx.TextCtrl(win,size=(150,20),style=wx.TE_PASSWORD)
        self.svnPass_t.SetMaxLength(15)

        line = wx.StaticLine(win)
        ##布局
        sizer = wx.GridBagSizer(4,5)
        sizer.Add(about_s,pos=(0,0),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)
        sizer.Add(line,pos=(1,0),span=(1,3),flag=wx.EXPAND|wx.RIGHT|wx.LEFT|wx.TOP,border=5)
        sizer.Add(url_s,pos=(2,0),span=(1,1),flag=wx.TOP|wx.LEFT|wx.EXPAND, border=10)
        sizer.Add(self.url_t,pos=(2,1),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT|wx.EXPAND, border=10)

        sizer.Add(svnWorkDir_s,pos=(3,0),span=(1,1),flag=wx.TOP|wx.LEFT|wx.EXPAND, border=10)
        sizer.Add(self.svnWorkDir_t,pos=(3,1),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT|wx.EXPAND, border=10)
        sizer.Add(self.svnWorkDir_b,pos=(3,2),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT, border=10)

        sizer.Add(svnUser_s,pos=(4,0),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)
        sizer.Add(self.svnUser_t,pos=(4,1),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT, border=10)

        sizer.Add(svnPass_s,pos=(5,0),span=(1,1),flag=wx.TOP|wx.LEFT|wx.EXPAND, border=10)
        sizer.Add(self.svnPass_t,pos=(5,1),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT, border=10)

        sizer.AddGrowableCol(1,1)
        win.SetSizerAndFit(sizer)
        sizer.SetSizeHints(self)


        def OnCPSize(evt, win=win):
            win.SetPosition((0,0))
            win.SetSize(evt.GetSize())
        p.Bind(wx.EVT_SIZE, OnCPSize)
        p.Bind(wx.EVT_BUTTON, self.OnSetUIOpenDir,id=GL.SetUIOpenDirID)
        return p

    def OnSetUIOpenDir(self,event):
        dlg = wx.DirDialog(None, u"选择文件夹:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            SvnWorkDir = dlg.GetPath()
            self.svnWorkDir_t.SetValue(SvnWorkDir)
        dlg.Destroy()


    def LocalUI(self):
        p = wx.Panel(self, -1)#子窗体的容器
        win=wx.Panel(p,-1)

        about_s = wx.StaticText(win,-1,u"本地服务器配置",)
        line = wx.StaticLine(win)
        webDir_s = wx.StaticText(win,-1,u"web根目录：")
        self.webDir_t  = wx.TextCtrl(win,size=(250,20))
        self.webDir_t.SetMaxLength(40)

        #self.webDir_b = wx.Button(win,label=u"打开",size=(50,20),id=wx.NewId())
        ipaddr_s = wx.StaticText(win,-1,u"IP地址：")
        self.ipaddr_t  = wx.TextCtrl(win,size=(250,20))
        self.ipaddr_t.SetMaxLength(15)

        sshPort_s = wx.StaticText(win,-1,u"SSH端口：")
        self.sshPort_t  = wx.TextCtrl(win,size=(250,20))
        self.sshPort_t.SetMaxLength(5)

        sshUser_s = wx.StaticText(win,-1,u"用户：")
        self.sshUser_t = wx.TextCtrl(win,size=(250,20),style=wx.TE_PASSWORD)
        self.sshUser_t.SetMaxLength(10)

        #sshPass_s = wx.StaticText(win,-1,u"密码：")
        #self.sshPass_t = wx.TextCtrl(win,size=(250,20),style=wx.TE_PASSWORD)
        #self.sshPass_t.SetMaxLength(15)


        sshTimeout_s = wx.StaticText(win,-1,u"连接超时：")
        self.sshTimeout_t  = wx.TextCtrl(win,size=(150,20))
        self.sshTimeout_t.SetMaxLength(2)
        sshTimeout_s2  = wx.StaticText(win,-1,u"秒")

        sizer = wx.GridBagSizer(7,3)
        sizer.Add(about_s,pos=(0,0),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)
        sizer.Add(line,pos=(1,0),span=(1,3),flag=wx.EXPAND|wx.RIGHT|wx.LEFT|wx.TOP,border=5)


        sizer.Add(webDir_s,pos=(2,0),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT|wx.EXPAND, border=10)
        sizer.Add(self.webDir_t,pos=(2,1),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT, border=10)
        #sizer.Add(self.webDir_b,pos=(2,4),span=(1,1),flag=wx.TOP|wx.ALIGN_RIGHT|wx.LEFT, border=10)

        sizer.Add(ipaddr_s,pos=(3,0),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT|wx.EXPAND, border=10)
        sizer.Add(self.ipaddr_t,pos=(3,1),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT, border=10)
        sizer.Add(sshPort_s,pos=(4,0),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT|wx.EXPAND, border=10)
        sizer.Add(self.sshPort_t,pos=(4,1),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT, border=10)

        sizer.Add(sshUser_s,pos=(5,0),span=(1,1),flag=wx.TOP|wx.LEFT|wx.ALIGN_LEFT|wx.EXPAND, border=10)
        sizer.Add(self.sshUser_t,pos=(5,1),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT, border=10)

        #sizer.Add(sshPass_s,pos=(6,0),span=(1,1),flag=wx.TOP|wx.LEFT|wx.ALIGN_LEFT|wx.EXPAND, border=10)
        #sizer.Add(self.sshPass_t,pos=(6,1),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT, border=10)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(sshTimeout_s,0,wx.ALL,0)
        hsizer.Add(self.sshTimeout_t,0,wx.LEFT,37)
        hsizer.Add(sshTimeout_s2,0,wx.LEFT,10)
        sizer.Add(hsizer,pos=(7,0),span=(1,4),flag=wx.TOP|wx.LEFT|wx.ALIGN_LEFT|wx.EXPAND, border=10)

        sizer.AddGrowableCol(1,1)
        win.SetSizerAndFit(sizer)
        sizer.SetSizeHints(self)


        def OnCPSize(evt, win=win):
            win.SetPosition((0,0))
            win.SetSize(evt.GetSize())
        p.Bind(wx.EVT_SIZE, OnCPSize)
        return p

    def RemoteUI(self):
        p = wx.Panel(self, -1)#子窗体的容器
        win=wx.Panel(p,-1)

        about_s = wx.StaticText(win,-1,u"远程服务器配置")
        line = wx.StaticLine(win)
        RwebDir_s = wx.StaticText(win,-1,u"正式web目录：")
        self.RwebDir_t  = wx.TextCtrl(win,size=(250,20))
        #self.webDir_b = wx.Button(win,label=u"打开",size=(50,20),id=wx.NewId())
        self.RwebDir_t.SetMaxLength(40)

        Ripaddr_s = wx.StaticText(win,-1,u"IP地址：")
        self.Ripaddr_t  = wx.TextCtrl(win,size=(250,20))#,style=wx.TE_PASSWORD)
        self.Ripaddr_t.SetMaxLength(15)

        RsshPort_s = wx.StaticText(win,-1,u"SSH端口：")
        self.RsshPort_t  = wx.TextCtrl(win,size=(250,20),style=wx.TE_PASSWORD)
        self.RsshPort_t.SetMaxLength(5)

        RsshTimeout_s = wx.StaticText(win,-1,u"连接超时：")
        self.RsshTimeout_t  = wx.TextCtrl(win,size=(150,20))
        self.RsshTimeout_t.SetMaxLength(2)
        RsshTimeout_s2  = wx.StaticText(win,-1,u"秒")

        sizer = wx.GridBagSizer(5,3)
        sizer.Add(about_s,pos=(0,0),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)
        sizer.Add(line,pos=(1,0),span=(1,3),flag=wx.EXPAND|wx.RIGHT|wx.LEFT|wx.TOP,border=5)

        sizer.Add(RwebDir_s,pos=(2,0),span=(1,1),flag=wx.TOP|wx.LEFT|wx.EXPAND, border=10)
        sizer.Add(self.RwebDir_t,pos=(2,1),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT, border=10)
        #sizer.Add(self.webDir_b,pos=(2,2),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT|wx.EXPAND, border=10)

        sizer.Add(Ripaddr_s,pos=(3,0),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)
        sizer.Add(self.Ripaddr_t,pos=(3,1),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)

        sizer.Add(RsshPort_s,pos=(4,0),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)
        sizer.Add(self.RsshPort_t,pos=(4,1),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(RsshTimeout_s,0,wx.ALL,0)
        hsizer.Add(self.RsshTimeout_t,0,wx.LEFT,37)
        hsizer.Add(RsshTimeout_s2,0,wx.LEFT,10)
        sizer.Add(hsizer,pos=(5,0),span=(1,3),flag=wx.TOP|wx.LEFT|wx.ALIGN_LEFT|wx.EXPAND, border=10)

        sizer.AddGrowableCol(1,1)
        win.SetSizerAndFit(sizer)
        sizer.SetSizeHints(self)


        def OnCPSize(evt, win=win):
            win.SetPosition((0,0))
            win.SetSize(evt.GetSize())
        p.Bind(wx.EVT_SIZE, OnCPSize)
        return p

    def LogSettingUI(self):
        p = wx.Panel(self, -1)#子窗体的容器
        win=wx.Panel(p,-1)

        about_s = wx.StaticText(win,-1,u"日志配置")
        line = wx.StaticLine(win)
        RlogUrl_s = wx.StaticText(win,-1,u"SVN日志URL：")
        self.RlogUrl_t  = wx.TextCtrl(win,size=(250,20))
        self.RlogUrl_t.SetMaxLength(50)
        #self.webDir_b = wx.Button(win,label=u"打开",size=(50,20),id=wx.NewId())

        GlogDir_s = wx.StaticText(win,-1,u"全局日志目录：")
        self.GlogDir_t  = wx.TextCtrl(win,size=(250,20))
        self.GlogDir_t.SetMaxLength(50)
        time_s = wx.StaticText(win,-1,u"时间同步：")
        self.time_t  = wx.TextCtrl(win,size=(250,20))
        self.time_t.SetMaxLength(32)


        sizer = wx.GridBagSizer(5,4)
        sizer.Add(about_s,pos=(0,0),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)
        sizer.Add(line,pos=(1,0),span=(1,3),flag=wx.EXPAND|wx.RIGHT|wx.LEFT|wx.TOP,border=5)

        sizer.Add(RlogUrl_s,pos=(2,0),span=(1,1),flag=wx.TOP|wx.LEFT|wx.EXPAND, border=10)
        sizer.Add(self.RlogUrl_t,pos=(2,1),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT, border=10)
        #sizer.Add(self.webDir_b,pos=(2,2),span=(1,1),flag=wx.TOP|wx.ALIGN_LEFT|wx.LEFT|wx.EXPAND, border=10)

        sizer.Add(GlogDir_s,pos=(3,0),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)
        sizer.Add(self.GlogDir_t,pos=(3,1),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)

        sizer.Add(time_s,pos=(4,0),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)
        sizer.Add(self.time_t,pos=(4,1),span=(1,1),flag=wx.TOP|wx.LEFT, border=10)

        sizer.AddGrowableCol(1,1)
        win.SetSizerAndFit(sizer)
        sizer.SetSizeHints(self)



        def OnCPSize(evt, win=win):
            win.SetPosition((0,0))
            win.SetSize(evt.GetSize())
        p.Bind(wx.EVT_SIZE, OnCPSize)
        return p

    def GetDataFromUI(self):
        GL.SvnUrl = self.url_t.GetValue()
        GL.SvnWorkDir = self.svnWorkDir_t.GetValue()
        GL.SvnUser = self.svnUser_t.GetValue()
        GL.SvnPass = self.svnPass_t.GetValue()
        GL.isSave = "True"

        GL.webDir = self.webDir_t.GetValue()
        if not GL.webDir.endswith("/"):
            GL.webDir = "".join([GL.webDir,"/"])
        GL.LIPaddr = self.ipaddr_t.GetValue()
        GL.LPort = self.sshPort_t.GetValue()
        GL.sshUser = self.sshUser_t.GetValue()
        #GL.sshPass = self.sshPass_t.GetValue()
        GL.sshTimeout = self.sshTimeout_t.GetValue()

        GL.RwebDir = self.RwebDir_t.GetValue()
        if not GL.RwebDir.endswith("/"):
            GL.RwebDir = "".join([GL.RwebDir,"/"])
        GL.RIPaddr = self.Ripaddr_t.GetValue()
        GL.RPort = self.RsshPort_t.GetValue()
        GL.RsshTimeout = self.RsshTimeout_t.GetValue()

        GL.SvnLogUrl = self.RlogUrl_t.GetValue()
        GL.GlogDir = self.GlogDir_t.GetValue()
        GL.ntpServer = self.time_t.GetValue()


    def GetDataFromUIAndEncrypt(self):
        self.GetDataFromUI()
        cipher = GetKey(self.enkey)
        ConfigDict = {}
        sshAuthDict = {}
        GL.SvnPass = EncodeAES(cipher,GL.SvnPass,32)
        GL.sshUser = EncodeAES(cipher,self.sshUser_t.GetValue(),32)
        GL.RIPaddr = EncodeAES(cipher,self.Ripaddr_t.GetValue(),32)
        GL.RPort = EncodeAES(cipher,self.RsshPort_t.GetValue(),32)

        ConfigDict["SVNConfig"] = {"SvnUrl":GL.SvnUrl,"SvnWorkDir":GL.SvnWorkDir,"SvnUser":GL.SvnUser,"SvnPass":GL.SvnPass,"isSave":GL.isSave}
        ConfigDict["LocalServer"] = {"LocalWebDir":GL.webDir,"IPaddr":GL.LIPaddr,"Port":GL.LPort,"username":GL.sshUser,"timeout":GL.sshTimeout}
        ConfigDict["RemoteServer"] = {"RemoteWebDir":GL.RwebDir,"IPaddr":GL.RIPaddr,"Port":GL.RPort,"timeout":GL.RsshTimeout}
        ConfigDict["LogConfig"] = {"SvnLogUrl":GL.SvnLogUrl,"GlogDir":GL.GlogDir,"ntpServer": GL.ntpServer}
        sshAuthDict["password"] = GL.sshPass
        return ConfigDict,sshAuthDict


    def SetConfigDictOnUI(self):
        self.url_t.SetValue(GL.SvnUrl)
        self.svnWorkDir_t.SetValue(GL.SvnWorkDir)
        if GL.isSave == False:
            self.svnUser_t.SetValue("")
            self.svnPass_t.SetValue("")
        else:
            self.svnUser_t.SetValue(GL.SvnUser)
            self.svnPass_t.SetValue(GL.SvnPass)
        self.webDir_t.SetValue(GL.webDir)
        self.ipaddr_t.SetValue(GL.LIPaddr)
        self.sshPort_t.SetValue(str(GL.LPort))
        self.sshUser_t.SetValue(GL.sshUser)
        #self.sshPass_t.SetValue(GL.sshPass)
        self.sshTimeout_t.SetValue(GL.sshTimeout)
        self.RwebDir_t.SetValue(GL.RwebDir)
        self.Ripaddr_t.SetValue(GL.RIPaddr)
        self.RsshPort_t.SetValue(str(GL.RPort))
        self.RsshTimeout_t.SetValue(GL.RsshTimeout)
        self.RlogUrl_t.SetValue(GL.SvnLogUrl)
        self.GlogDir_t.SetValue(GL.GlogDir)
        self.time_t.SetValue(GL.ntpServer)

    def LoadDefault(self):
        GL.SvnUrl = GL.DefaultConfDict["SVNConfig"]["SvnUrl"]
        GL.SvnWorkDir = GL.DefaultConfDict["SVNConfig"]["SvnWorkDir"]
        GL.SvnUser = GL.DefaultConfDict["SVNConfig"]["SvnUser"]
        GL.SvnPass = GL.DefaultConfDict["SVNConfig"]["SvnPass"]
        GL.webDir = GL.DefaultConfDict["LocalServer"]["LocalWebDir"]
        GL.LIPaddr = GL.DefaultConfDict["LocalServer"]["IPaddr"]
        GL.LPort = int(GL.DefaultConfDict["LocalServer"]["Port"])
        GL.sshUser = GL.DefaultConfDict["LocalServer"]["username"]
        GL.sshTimeout = GL.DefaultConfDict["LocalServer"]["timeout"]
        GL.RwebDir = GL.DefaultConfDict["RemoteServer"]["RemoteWebDir"]
        GL.RIPaddr = GL.DefaultConfDict["RemoteServer"]["IPaddr"]
        GL.RPort = int(GL.DefaultConfDict["RemoteServer"]["Port"])
        GL.RsshTimeout = GL.DefaultConfDict["RemoteServer"]["timeout"]
        GL.SvnLogUrl = GL.DefaultConfDict["LogConfig"]["SvnLogUrl"]
        GL.GlogDir = GL.DefaultConfDict["LogConfig"]["GlogDir"]
        GL.ntpServer = GL.DefaultConfDict["LogConfig"]["ntpServer"]

class settingDlg(wx.Dialog):
    def __init__(self,title):
        wx.Dialog.__init__(self, None, -1,title=title,size=(600,410),style=wx.DEFAULT_DIALOG_STYLE)#|wx.RESIZE_BORDER)

        self.panel = wx.Panel(self)
        #self.panel.SetBackgroundColour("white")
        self.SetUI = SettingPanel(self.panel)
        self.OKBtn = wx.Button(self.panel, label=u"确定",size=(80, 22),id=wx.ID_OK)
        self.CancelBtn = wx.Button(self.panel, label=u"取消",size=(80, 22),id=wx.ID_CANCEL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(self.SetUI,1,wx.EXPAND)
        vsizer.Add(hsizer,1,wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.Add(self.OKBtn,0,wx.RIGHT|wx.ALIGN_RIGHT|wx.BOTTOM,border=10)
        hsizer2.Add(self.CancelBtn,0,wx.RIGHT|wx.ALIGN_RIGHT|wx.BOTTOM,border=10)
        vsizer.Add(hsizer2,0,wx.ALIGN_RIGHT|wx.RIGHT|wx.TOP, border=10)
        self.panel.SetSizerAndFit(vsizer)

        #self.Bind(wx.EVT_BUTTON,self.OnSettingOK,id= GL.SettingOK)

if __name__ == "__main__":
    #EnConfigDataDict = loadConfig.ReadAllConf(GL.ConfFile,GL.sections)
    #configDataDict = loadConfig.ReadConfigDictValue()
    #sshAuthDict = loadConfig.ReadSSHAuthFile(GL.AuthFile,GL.str_key,GL.pass_public_key,"password")
    app = wx.App()
    dlg = settingDlg(u"设置")
    dlg.Center()
    if dlg.ShowModal() == wx.ID_OK:
        from loadConfig import SaveConf,SaveSSHAuthToFile
        GetSaveConfDict,GetSaveSSHAuthDict = dlg.SetUI.GetDataFromUIAndEncrypt()
        SaveConf(GL.ConfFile,GetSaveConfDict)
        SaveSSHAuthToFile(GetSaveSSHAuthDict,GL.AuthFile,GL.str_key,GL.pass_private_key)


    dlg.SetUI.GetDataFromUI()
    print GL.RIPaddr
    dlg.Destroy()
    app.MainLoop()