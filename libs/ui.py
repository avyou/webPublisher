#coding:utf-8
import wx
import wx.aui
import wx.lib.agw.customtreectrl as CT
import os
import globalDef as GL
import logHandler as LoadLog
from wx.lib.itemspicker import ItemsPicker, \
                               EVT_IP_SELECTION_CHANGED, \
                               IP_SORT_CHOICES, IP_SORT_SELECTED,\
                               IP_REMOVE_FROM_CHOICES
class DefaultPublishUI(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.sampleList = []
        #
        select_file_text = wx.StaticText(self,label=u"已选择的文件:")
        select_file_blank = wx.StaticText(self,label="")
        self.ChoiceListBox = ChoiceListBox = wx.ListBox(self,-1, (-1, 1), (-1, -1), self.sampleList, wx.LB_EXTENDED|
                                                                                                wx.LB_NEEDED_SB|
                                                                                                wx.HSCROLL)#wx.LB_SORT|)

        BtnClean = wx.Button(self,label=u"清空",size=(100,30),id=GL.Clear_All_Entry_ID)
        BtnDelte = wx.Button(self,label=u"移除",size=(100,30),id=GL.Remove_Entry_ID)
        BtnUpdate = wx.Button(self,label=u"发布",size=(100,60),id=GL.PublishMenuID)
        self.ChoiceListBox.SetItemBackgroundColour(0,"green")

        hsizer =wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(select_file_blank,0,wx.LEFT,30)
        vsizer.Add(select_file_text,0,wx.LEFT,30)
        vsizer.Add(ChoiceListBox,1, wx.LEFT|wx.EXPAND,30)
        vsizer2 = wx.BoxSizer(wx.VERTICAL)
        #vsizer2.Add(BtnAdd,0,wx.BOTTOM,10)
        vsizer2.Add(BtnClean,0,wx.BOTTOM,10)
        vsizer2.Add(BtnDelte,0,wx.BOTTOM,10)
        vsizer2.Add(BtnUpdate,0)
        hsizer.Add(vsizer,1,wx.BOTTOM|wx.RIGHT|wx.EXPAND,25)
        hsizer.Add(vsizer2,0,wx.ALIGN_BOTTOM|wx.RIGHT|wx.BOTTOM,25)
        self.SetSizerAndFit(hsizer)
class BackupRollBackUI(wx.Panel):
    def __init__(self, parent,style=IP_REMOVE_FROM_CHOICES):
        wx.Panel.__init__(self, parent,style=style)
        self.backupList = GL.backup_list
        self.radioList = [u'当前用户最近备份列表', u'载入当前用户备份列表', u'载入全局备份列表']
        self.backupRadio = wx.RadioBox(self, -1, "", (-1,-1), wx.DefaultSize, self.radioList, 3, wx.RA_SPECIFY_COLS | wx.NO_BORDER)
        #BtnRollBack = wx.Button(self,label=u"锟斤拷原",size=(80,50),id=GL.Publishing)
        self.BakRollText = ItemsPicker(self,-1,self.backupList,u"备份列表", u'确认还原文件:',ipStyle = style)
        self.BakRollText.add_button_label =  u'添加=》'
        self.BakRollText.remove_button_label =  u'《=移除'
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer =wx.BoxSizer(wx.VERTICAL)
        self.BakRollText._source.SetMinSize((-1,150))

        self.BakRollText._dest.SetMinSize((-1,150))
        vsizer.Add(self.backupRadio, 0, wx.ALL, 0)
        vsizer.Add(self.BakRollText, 1, wx.ALL|wx.EXPAND, 0)
        hsizer.Add(vsizer,1,wx.ALL|wx.EXPAND,10)
        self.SetSizerAndFit(hsizer)
        self.itemCount = 3
        self.Bind(wx.EVT_RADIOBOX, self.OnLoadBackupList, self.backupRadio)
        self.BakRollText.Bind(EVT_IP_SELECTION_CHANGED, self.OnSelectionChange)
    def OnLoadBackupList(self,event):
        if event.GetInt() == 0:
            self.BakRollText._source.SetItems([])
            self.BakRollText._source.SetItems(GL.backup_list)
            #self.BakRollText._dest.SetItems(GL.backup_list)
            #print self.BakRollText._dest.GetItems()
        elif event.GetInt() == 1:
            self.BakRollText._source.SetItems([])
            import codecs


            #data = self.GetUserLogList('f:\\backup\\Glogs\\global_backup.log')
            #print data
            #self.FileContentList = []
            self.FileContentList = self.GetUserLogList(GL.global_backup_logfile,isFilter=True)
            #with codecs.open('f:\\backup\\Glogs\\global_backup.log','r',"utf8") as FileObj:
            #    [self.FileContentList.append(line) for line in FileObj]
            #print self.FileContentList

            self.BakRollText._source.SetItems(self.FileContentList)
            #self.BakRollText._source.SetBackgroundColour('#FF0000')
            #print "load log2"
        elif event.GetInt() == 2:
            self.BakRollText._source.SetItems([])
            self.FileContentList = self.GetUserLogList(GL.global_backup_logfile,isFilter=False)
            self.BakRollText._source.SetItems(self.FileContentList)
        else:
            self.BakRollText._source.SetItems([])


    def GetUserLogList(self,filelog,isFilter):
        if not os.path.exists(filelog):
            msg = u"读取全局日志文件出错."
            LoadLog.LogMsg(GL.logger_sysLog.error,msg)
            wx.MessageBox(msg,u"错误", style=wx.OK|wx.ICON_ERROR)
            FileContentList = []
            return FileContentList
        FileContentList = []
        with open(filelog,'r') as f:
            if isFilter is True:
                bad = 0
                import codecs,re
                goodline = re.compile(ur'#+?.*\[%s\].*#$' % GL.SvnUser)
                badline =  re.compile(ur'#+?.*\[((?!%s).)*#$' % GL.SvnUser)
                for line in f:
                    line = unicode(line,"utf8")
                    if goodline.search(line) is not None:
                        #print line
                        bad = 1
                        FileContentList.append(line.strip())
                        continue
                    if bad and badline.search(line) is  None:
                        #print line
                        FileContentList.append(line.strip())
                        continue
                    else:
                        bad = 0
            else:
                [ FileContentList.append(unicode(line,"utf8")) for line in f]
        return FileContentList

    def OnAdd(self,e):
        items = self.BakRollText.GetItems()
        self.itemCount += 1
        newItem = "item%d" % self.itemCount
        self.BakRollText.SetItems(items + [newItem])
    #def OnSelectionChange(self, e):
    # self.log.write("EVT_IP_SELECTION_CHANGED %s\n" % \
    # ",".join(e.GetItems()))
    def OnSelectionChange(self, e):
        #self.log.write("EVT_IP_SELECTION_CHANGED %s\n" % ",".join(e.GetItems()))
        pass
class CustomPublishUI(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.sampleList = []
        #
        select_file_text = wx.StaticText(self,label=u"手工输入文件：(文件样例参照\"默认发布\")")
        select_file_blank = wx.StaticText(self,label="")
        self.customUpdateText = customUpdateText = wx.TextCtrl(self, -1, u"", size=(-1,-1),style=wx.TE_MULTILINE)

        BtnClean = wx.Button(self,label=u"清空",size=(100,30),id=GL.Clear_All_Text_ID)
        BtnUpdate = wx.Button(self,label=u"发布",size=(100,60),id=GL.PublishTextMenuID)
        hsizer =wx.BoxSizer(wx.HORIZONTAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(select_file_blank,0,wx.LEFT,30)
        vsizer.Add(select_file_text,0,wx.LEFT,30)
        vsizer.Add(customUpdateText,1, wx.LEFT|wx.EXPAND,30)
        vsizer2 = wx.BoxSizer(wx.VERTICAL)
        #vsizer2.Add(BtnAdd,0,wx.BOTTOM,10)
        vsizer2.Add(BtnClean,0,wx.BOTTOM,10)
        vsizer2.Add(BtnUpdate,0)
        hsizer.Add(vsizer,1,wx.BOTTOM|wx.RIGHT|wx.EXPAND,25)
        hsizer.Add(vsizer2,0,wx.ALIGN_BOTTOM|wx.RIGHT|wx.BOTTOM,25)
        self.SetSizerAndFit(hsizer)
# class PageFour(wx.Panel):
# def __init__(self, parent):
# wx.Panel.__init__(self, parent)
# t = wx.StaticText(self, -1, "This is a PageOne object", (20,20))
# class PageFive(wx.Panel):
# def __init__(self, parent):
# wx.Panel.__init__(self, parent)
# t = wx.StaticText(self, -1, "This is a PageThree object", (100,100))
class MainWin(wx.Panel):
    def __init__(self,parent,id):
        wx.Panel.__init__(self,parent,id)
        self.nb = wx.aui.AuiNotebook(self,style=wx.aui.AUI_NB_TOP)
        # create the page windows as children of the notebook
        self.page1 = DefaultPublishUI(self.nb)
        self.page2 = CustomPublishUI(self.nb)
        self.page3 = BackupRollBackUI(self.nb)
        #self.page3.
        # self.page4 = PageFour(nb)
        # self.page5 = PageFive(nb)
        # add the pages to the notebook with the label to show on the tab
        self.nb.AddPage(self.page1,u"默认发布")
        #nb.AddPage(self.page2, u"鎸塖VN搴撳彂甯�)
        #nb.AddPage(self.page3, u"鎸夋椂闂存棩鏈熷彂甯�)
        self.nb.AddPage(self.page2, u"自定文件发布")
        self.nb.AddPage(self.page3, u"备份还原")
        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)
class LogConsole(wx.Panel):
    def __init__(self,parent,id):
        wx.Panel.__init__(self,parent,id)
        self.nb = wx.Notebook(self)
        self.UpdateLogName = UpdateLogPage(self.nb)
        self.BackupLogName = BackupLogPage(self.nb)
        self.GLobalUpdateLog = GLobalUpdateLogPage(self.nb)
        self.GlobalBackupLog = GLobalBackupLogPage(self.nb)
        self.SysinfoLog = SysinfoLogPage(self.nb)
        self.nb.AddPage(self.UpdateLogName, u"发布日志")
        self.nb.AddPage(self.BackupLogName, u"备份日志")
        self.nb.AddPage(self.GLobalUpdateLog, u"全局更新日志")
        self.nb.AddPage(self.GlobalBackupLog, u"全局备份日志")
        self.nb.AddPage(self.SysinfoLog, u"系统日志")
        sizer = wx.BoxSizer()
        sizer.Add(self.nb, 1, wx.EXPAND)
        self.SetSizer(sizer)

        self.nb.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED,self.OnChangeLogPanel)

    def OnChangeLogPanel(self,evnt):

        if self.nb.GetSelection() == 2 and GL.loadGUpdateLog == True:
            logcontent = self.FileContents(GL.gloabl_publish_logfile,"utf8")
            self.GLobalUpdateLog.GupdateText.SetValue(logcontent)
            self.FileContentList = []
            #GL.loadGUpdateLog = False

        if self.nb.GetSelection() == 3 and GL.loadGBackupLog == True:
            logcontent = self.FileContents(GL.global_backup_logfile,"utf8")
            self.GlobalBackupLog.GbackupText.SetValue(logcontent)
            self.FileContentList = []
            #GL.loadGBackupLog = False

    def FileContents(self,filePath,fileCode):
        if not os.path.exists(filePath):
            msg = u"全局日志文件不存在."
            wx.MessageBox(msg,u"错误", style=wx.OK|wx.ICON_ERROR)
            LoadLog.LogMsg(GL.logger_sysLog.error,msg)
            return ""
        self.FileContentList = []
        try:
            import codecs
            with codecs.open(filePath,'r',fileCode) as FileObj:
                [self.FileContentList.append(line) for line in FileObj]
        except UnicodeDecodeError,errorMsg:
            msg = u"读取全局日志文件出错." + errorMsg
            LoadLog.LogMsg(GL.logger_sysLog.error,msg)
            wx.MessageBox(msg,u"错误", style=wx.OK|wx.ICON_ERROR)
            return "codeError"
        else:
            self.FileContent = "".join(self.FileContentList)
            return self.FileContent

class UpdateLogPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        boxsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ConsoleText = ConsoleText = wx.TextCtrl(self,-1, "", size=(-1,-1),style=wx.TE_MULTILINE|wx.TE_READONLY)#|wx.TE_RICH2)
        ConsoleText.SetBackgroundColour("light blue")
        boxsizer.Add(ConsoleText,1,flag=wx.EXPAND)
        self.SetSizerAndFit(boxsizer)
        #LoadLog.LogMsg(GL.loggera.warning,u"aaaaaaaaaaaaa")
        txtHandler = LoadLog.LogConsoleHandler(self.ConsoleText)
        GL.logger_PubLog.addHandler(txtHandler)

class BackupLogPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        boxsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.BackupText = BackupText = wx.TextCtrl(self,-1, "", size=(-1,-1),style=wx.TE_MULTILINE|wx.TE_READONLY)#|wx.TE_RICH2)
        BackupText.SetBackgroundColour("light blue")
        boxsizer.Add(BackupText,1,flag=wx.EXPAND)
        self.SetSizerAndFit(boxsizer)
        #LoadLog.LogMsg(GL.logger.warning,u"aaaaaaaaaaaaa")
        btxtHandler = LoadLog.LogConsoleHandler(self.BackupText)
        GL.logger_BakLog.addHandler(btxtHandler)
class GLobalUpdateLogPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        boxsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.GupdateText = GupdateText = wx.TextCtrl(self,-1, "", size=(-1,-1),style=wx.TE_MULTILINE|wx.TE_READONLY)#|wx.TE_RICH2)
        GupdateText.SetBackgroundColour("light blue")
        boxsizer.Add(GupdateText,1,flag=wx.EXPAND)
        self.SetSizerAndFit(boxsizer)
        #LoadLog.LogMsg(GL.logger.warning,u"aaaaaaaaaaaaa")
        #ctxtHandler = LoadLog.LogConsoleHandler(self.GupdateText)
        #GL.logger_gPubLog.addHandler(ctxtHandler)
class GLobalBackupLogPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        boxsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.GbackupText = GbackupText = wx.TextCtrl(self,-1, "", size=(-1,-1),style=wx.TE_MULTILINE|wx.TE_READONLY)#|wx.TE_RICH2)
        GbackupText.SetBackgroundColour("light blue")
        boxsizer.Add(GbackupText,1,flag=wx.EXPAND)
        self.SetSizerAndFit(boxsizer)
        #LoadLog.LogMsg(GL.logger.warning,u"aaaaaaaaaaaaa")
        dtxtHandler = LoadLog.LogConsoleHandler(self.GbackupText)
        GL.logger_gBakLog.addHandler(dtxtHandler)
class SysinfoLogPage(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        boxsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SysText = SysText = wx.TextCtrl(self,-1, "", size=(-1,-1),style=wx.TE_MULTILINE|wx.TE_READONLY)#|wx.TE_RICH2)
        SysText.SetBackgroundColour("light blue")
        boxsizer.Add(SysText,1,flag=wx.EXPAND)
        self.SetSizerAndFit(boxsizer)
        #LoadLog.LogMsg(GL.logger.warning,u"aaaaaaaaaaaaa")
        etxtHandler = LoadLog.LogConsoleHandler(self.SysText)
        GL.logger_sysLog.addHandler(etxtHandler)
class CustomTree(wx.Panel):
    def __init__(self,parent,id,rootDir):
        wx.Panel.__init__(self,parent,id)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.ListDir = rootDir

        self.rootNote = os.path.split(self.ListDir)[-1]
        self.rootPathPrefix = os.path.split(self.ListDir)[:-1]
        #print self.rootPathPrefix
        self.custom_tree = custom_tree = CT.CustomTreeCtrl(self,id=GL.TreeID,size=(-1,-1), agwStyle=wx.TR_DEFAULT_STYLE)

        self.custom_tree.SetBackgroundColour("white")

        self.rootShow = self.rootNote+" ("+self.ListDir+") "
        self.root = custom_tree.AddRoot(self.rootShow)
        sizer.Add(custom_tree,1,flag=wx.EXPAND)
        #self.ListDir = ListDir
        il = wx.ImageList(16, 16)
        self.fldridx = fldridx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        self.fldropenidx = fldropenidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16, 16)))
        self.fileidx = il.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))
        custom_tree.SetImageList(il)
        custom_tree.SetItemImage(self.root, fldridx, wx.TreeItemIcon_Normal)
        custom_tree.SetItemImage(self.root, fldropenidx, wx.TreeItemIcon_Expanded)
        self.AllFileDiect = {}
        #appenDir(custom_tree,root,"d:\\all_source\\usport")

        #self.AppenDir(custom_tree,self.root,self.ListDir)
        self.AppenDirThread(custom_tree,self.root,self.ListDir)

        #custom_tree.Expand(self.root)
        self.SetSizerAndFit(sizer)
        #custom_tree.SendSizeEvent()


    def AppenDirThread(self,tree,treeid,rootdir):
        from mainFun import  WorkerThread,MainFun
        thread = WorkerThread(self,"appendir",tree,treeid,rootdir)#创建一个线程
        thread.start()#启动线程



    def AppenDir(self,tree,treeid,rootdir):
        self.custom_tree.Expand(self.root)
        try:
            # try:
            # ListFristDir = self.ReadPickle()
            # if len(ListFristDir) == 0:
            # print "read file"
            # ListFristDir = os.listdir(rootdir)
            # ListFristDir.sort(key=lambda f: os.path.splitext(f)[1])
            # except:
            # print "read dir"
            # ListFristDir = self.SaveAsPickle(rootdir)
            ListFristDir = os.listdir(rootdir)
            ListFristDir.sort(key=lambda f: os.path.splitext(f)[1])
            for i in ListFristDir:
                if i == r'.svn':
                    continue
                sAllDir = os.path.join(rootdir,i)#.replace(os.sep,'/')
                try:
                    if os.path.isdir(sAllDir):
                        childID = tree.AppendItem(treeid,i)
                        self.custom_tree.SetItemImage(childID, self.fldropenidx, wx.TreeItemIcon_Expanded)
                        self.custom_tree.SetItemImage(childID, self.fldridx, wx.TreeItemIcon_Normal)
                        self.AppenDir(tree,childID,sAllDir)
                    else:
                        childID = tree.AppendItem(treeid,i,ct_type=1)
                        self.AllFileDiect[sAllDir] = childID
                        self.custom_tree.SetItemImage(childID, self.fileidx, wx.TreeItemIcon_Normal)
                except:
                    tree.AppendItem(treeid,u"非法名称")
        except:
            pass

        #for key in self.AllFileDiect:
        # print key, self.AllFileDiect[key]

class TaskBarIcon(wx.TaskBarIcon):
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon(name='icons/logo.ico', type=wx.BITMAP_TYPE_ICO), 'Web Publisher v1.0')
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
        self.Bind(wx.EVT_MENU, self.OnShow, id=GL.ShowWinID)
        self.Bind(wx.EVT_MENU, self.frame.OnMenuAbout, id=GL.MenuAboutID)
        self.Bind(wx.EVT_MENU, self.frame.OnMenuRegister, id=GL.RegisterID)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        self.font_bold = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        self.font_bold.SetWeight(wx.BOLD)

    def OnTaskBarLeftDClick(self, event):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
        if not self.frame.IsShown():
            self.frame.Show(True)
            self.frame.Raise()

    def OnShow(self, event):
        if not self.frame.IsShown():
            self.frame.Show(True)
        self.frame.Raise()

    def OnExit(self, event):
        self.frame.OnClose(event)

    def CreatePopupMenu(self):
        menu = wx.Menu()
        menu.Append(GL.ShowWinID, u'显示主窗口')
        menu.AppendSeparator()
        menu.Append(GL.RegisterID, u'注册')
        menu.AppendSeparator()
        menu.Append(GL.MenuAboutID, u'关于')
        menu.AppendSeparator()
        menu.Append(wx.ID_EXIT, u'退出')
        return menu

class CustomStatusBar(wx.StatusBar):
    def __init__(self,parent):
        wx.StatusBar.__init__(self, parent, -1)
        self.SetFieldsCount(4)
        self.SetStatusWidths([-2,-2,-1,-1])
        self.sizeChanged=True
        #self.Bind(wx.EVT_SIZE,self.OnSize)
        #self.SetStatusText(u"状态栏测试",0)
        #self.SetStatusText("aaa",1)
        # self.SetStatusText(gen.monProNum,1)
        #self.SetStatusText(gen.runProNum,2)
        self.timer=wx.PyTimer(self.Notify)
        self.timer.Start(1000)
        self.Notify()
    def Notify(self):
        import time
        t=time.localtime(time.time())
        st=time.strftime("%Y-%m-%d %H:%M:%S",t)

        #self.SetStatusText("",0)
        self.SetStatusText(u"网络状态:   " + GL.NetStatus,2)
        self.SetStatusText(st,3)