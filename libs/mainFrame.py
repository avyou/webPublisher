#coding:utf-8
import globalDef as GL
import wx
import wx.aui
import wx.lib.agw.customtreectrl as CT
import os,time,subprocess
import cPickle as pickle
import sshHandle
import logHandler as LoadLog
from ui import CustomTree,MainWin,LogConsole,TaskBarIcon,CustomStatusBar
from registerUI import RegisterUI
from about import MyAboutBox
from loadConfig import UpdateSectionDict
from mainFun import MainFun,WorkerThread

wx.Log.SetLogLevel(0)



class MyFrame(wx.Frame):
    def __init__(self, parent, id, title,size, pos=wx.DefaultPosition,
                     style=wx.DEFAULT_FRAME_STYLE |wx.SUNKEN_BORDER |wx.CLIP_CHILDREN):
        wx.Frame.__init__(self, parent,id, title,size=size,pos=pos,style=style)
        self.SetIcon(wx.Icon('icons/logo.ico', wx.BITMAP_TYPE_ICO))
        #self.BackupDir = GL.BackupDir

        self.ConfFile = GL.ConfFile
        self.AuthFile = GL.AuthFile
        self.str_key = GL.str_key
        self.public_key = GL.public_key
        self.pass_private_key = GL.pass_private_key
        self.sections = GL.sections
        self.RegisterFile = GL.RegisterFile
        self.DefaultConfDict = GL.DefaultConfDict

        self.MenuBarUI()
        self.ToolBarUI()
        self.StatusBarUI()
        self._mgr = wx.aui.AuiManager(self)
        self.leftpanel = CustomTree(self,-1,GL.SvnWorkDir)
        self.leftpanel.SetBackgroundColour("white")
        self.rightpanel = MainWin(self, -1)
        self.bottompanel = LogConsole(self, -1)
        #leftpanel = self.CustomTree(leftpanel,"e:\\www\\usport")
        self.BackupDir = "/".join([GL.BackupDir,self.leftpanel.rootNote,""])
        self._mgr.AddPane(self.leftpanel,
                         wx.aui.AuiPaneInfo().
                         Left().Layer(1).BestSize((250, -1)).
                         MinSize((120, -1)).
                         #Floatable(self.allowAuiFloating).FloatingSize((240, 700)).
                         Caption(u"本地SVN目录树").
                         CloseButton(False).
                         Name(""))
        self._mgr.AddPane(self.rightpanel,
                          wx.aui.AuiPaneInfo().
                          CenterPane().
                          CloseButton(False).
                          Name("Notebook"))

        self._mgr.AddPane(self.bottompanel,
                         wx.aui.AuiPaneInfo().
                         Bottom().BestSize((-1, 250)).
                         MinSize((-1, -1)).
                         #Floatable(self.allowAuiFloating).FloatingSize((500, 160)).
                         Caption(u"日志").
                         CloseButton(False).
                         Name("LogWindow"))
        self._mgr.Update()
        #from taskbarIcon import TaskBarIcon
        self.taskBarIcon = TaskBarIcon(self)
        #self._runBackGround(GL.NtpServers)

        #self.leftpanel.Bind(CT.EVT_TREE_ITEM_CHECKED, self.ItemChecked,id=TREEID)
        #self.taskBarIcon = TaskBarIcon(self)
        self.leftpanel.Bind(CT.EVT_TREE_ITEM_CHECKED,self.ItemChecked,id=GL.TreeID)
        self.rightpanel.Bind(wx.EVT_BUTTON, self.OnPublishEntry, id=GL.PublishMenuID)
        self.rightpanel.Bind(wx.EVT_BUTTON, self.OnPublishText, id=GL.PublishTextMenuID)
        self.rightpanel.Bind(wx.EVT_BUTTON, self.OnClearEntry, id=GL.Clear_All_Entry_ID)
        self.rightpanel.Bind(wx.EVT_BUTTON, self.OnRemoveEntry, id=GL.Remove_Entry_ID)
        self.rightpanel.Bind(wx.EVT_BUTTON, self.OnClearText, id=GL.Clear_All_Text_ID)
        self.rightpanel.page1.ChoiceListBox.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)
        self.Bind(wx.EVT_CLOSE, self.OnHide)

        self.MainFun = MainFun(GL.LIPaddr,GL.GlogDir,GL.SvnUrl,GL.SvnWorkDir,GL.SvnUser,GL.SvnPass,GL.SvnLogUrl,GL.logger_sysLog)
        self.OnRegditThread(self.MainFun,"regedit",self.public_key,self.str_key,self.RegisterFile)
        #self.OnStartTimeSyncThread(self.MainFun,"timesync",GL.ntpServer)
        self.MonitorThread(self.MainFun,"monitornet")

        elapsed = (time.clock() - GL.start)
        print("Time used:",elapsed)


    def MenuBarUI(self):
        ## 菜单栏
        menuBar = wx.MenuBar()
        menu_file = wx.Menu()
        menu_view = wx.Menu()
        menu_operate = wx.Menu()
        menu_about = wx.Menu()
        menuBar.Append(menu_file,u"文件")
        menuBar.Append(menu_view,u"查看")
        menuBar.Append(menu_operate,u"操作")
        menuBar.Append(menu_about,u"帮助")
        menu_file.Append(GL.OpenDirID,u"打开目录",u"打开指定的SVN目录")
        menu_file.Append(GL.RefreshTreeDirID,u"刷新目录",u"刷新后将重新载入SVN目录")
        menu_file.AppendSeparator()
        menu_file.Append(GL.MenuSettingID,u"设置",u"程序的全局配置")
        menu_file.Append(GL.ExitID,u"退出",u"退出")
        menu_view.Append(GL.SvnDirViewID,u"查看本地SVN目录",u"查看SVN目录")
        menu_view.Append(GL.LogViewID,u"查看本地日志",u"查看本地日志")
        menu_view.Append(GL.GLogViewID,u"查看全局日志",u"查看全局日志")
        #log_view.Enable(False)
        menu_operate.Append(GL.PublishMenuID,u"默认发布",u"通过目录树将文件发布到正式网站")
        menu_operate.Append(GL.PublishTextMenuID,u"自定义发布",u"通过自定义输入将文件发布到正式网站")
        menu_operate.Append(GL.RollBackID,u"文件还原",u"将指定的备份文件还原到正式网站")
        menu_operate.AppendSeparator()
        menu_operate.Append(GL.SvnCommitID,u"SVN提交",u"SVN提交")
        menu_operate.Append(GL.SvnUpdateID,u"SVN更新",u"SVN更新")
        menu_about.Append(GL.MenuAboutID,u"关于",u"关于")
        menu_about.Append(GL.MenuRegisterID,u"注册",u"注册")
        self.MenuUpdate = menu_about.Append(GL.ProgramUpdateID,u"更新",u"程序更新")
        self.MenuUpdate.Enable(False)
        menu_about.AppendSeparator()
        self.MenuHelp = menu_about.Append(GL.HelpID,u"帮助",u"帮助")
        #self.MenuHelp.Enable(False)
        self.SetMenuBar(menuBar)
        self.Bind(wx.EVT_MENU,self.OnMenuRegister,id=GL.MenuRegisterID)
        self.Bind(wx.EVT_MENU,self.OnMenuAbout,id=GL.MenuAboutID)
        self.Bind(wx.EVT_MENU,self.OnMenuSetting,id=GL.MenuSettingID)
        self.Bind(wx.EVT_MENU,self.OnOpenDir,id=GL.OpenDirID)
        self.Bind(wx.EVT_MENU,self.OnClose,id=GL.ExitID)

    def ToolBarUI(self):
        self.toolbar = toolbar = self.CreateToolBar(style = wx.TB_HORIZONTAL|wx.TB_FLAT|wx.TB_TEXT)
        ## 定义一个工具栏的间隔距离
        tsize = (56,32)
        toolbar.SetToolBitmapSize(tsize)
        #####定义工具栏的位图

        # add_tmp = wx.Image('img/c1.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        # del_tmp = wx.Image('img/c2.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        # edit_tmp = wx.Image('img/c3.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        # start_tmp = wx.Image('img/c4.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        # restart_tmp = wx.Image('img/c8.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        file_publish = wx.Bitmap("icons/c1.png",wx.BITMAP_TYPE_ANY)
        file_rollback = wx.Bitmap("icons/c2.png",wx.BITMAP_TYPE_ANY)
        refresh_dir = wx.Bitmap("icons/c3.png",wx.BITMAP_TYPE_ANY)
        svn_commit = wx.Bitmap("icons/c4.png",wx.BITMAP_TYPE_ANY)
        svn_update = wx.Bitmap("icons/c5.png",wx.BITMAP_TYPE_ANY)
        refresh_log = wx.Bitmap("icons/c6.png",wx.BITMAP_TYPE_ANY)
        #stop_tmp = wx.Bitmap("img/prestart.png",wx.BITMAP_TYPE_ANY)
        ###添加工具栏标签
        toolbar.AddLabelTool(GL.PublishToolID,u"文件发布",file_publish,shortHelp=u"文件发布",longHelp=u"")
        toolbar.AddLabelTool(GL.RollBackID,u"文件还原",file_rollback,shortHelp=u"从备份列表中还原文件",longHelp=u"")
        toolbar.AddLabelTool(GL.RefreshTreeDirID,u"刷新目录",refresh_dir,shortHelp=u"刷新目录",longHelp=u"")
        toolbar.AddSeparator()
        self.SvnCommitBtn = toolbar.AddLabelTool(GL.SvnCommitID,u"SVN提交",svn_commit,shortHelp=u"SVN更新",longHelp=u"")
        self.SvnUpdateBtn = toolbar.AddLabelTool(GL.SvnUpdateID,u"SVN更新",svn_update,shortHelp=u"SVN提交",longHelp=u"")
        toolbar.AddSeparator()
        self.RefreshLogBtn = toolbar.AddLabelTool(GL.RefreshLogID,u"刷新日志",refresh_log,shortHelp=u"同步全局日志文件到本地",longHelp=u"更新全局日志文件到本地")
        #toolbar.AddLabelTool(wx.NewId(),u"重启进程",stop_tmp,shortHelp=u"重启进程",longHelp=u"")
        ##分隔线
        toolbar.AddSeparator()
        toolbar.AddStretchableSpace()

        toolbar.AddControl( wx.StaticText(toolbar, wx.NewId(), u"用户：" ))
        self.username_text = wx.TextCtrl(toolbar, GL.GetUserNameUID, "",size=(100,-1),style= wx.TE_PROCESS_ENTER )
        self.username_text.SetMaxLength(8)
        #authDict = self.ReadAuthFile()
        #print authDict
        #self.username_text.SetValue(authDict.get("username",""))
        self.username_text.SetValue(GL.SvnUser)

        toolbar.AddControl(self.username_text)
        toolbar.AddControl(wx.StaticText(toolbar, wx.NewId(), u" 密码："))
        self.password_text = wx.TextCtrl(toolbar, GL.GetPasswordID, "",size=(100,-1),style=wx.PASSWORD )
        #self.password_text.SetValue(authDict.get("password",""))
        self.password_text.SetValue(GL.SvnPass)
        toolbar.AddControl(self.password_text)
        toolbar.AddControl(wx.StaticText(toolbar, wx.NewId(), u" " ))
        self.remember_checkbox = wx.CheckBox(toolbar, GL.RememberCheckBoxID, u"记住")
        if self.username_text.IsEmpty() or self.password_text.IsEmpty():
            self.remember_checkbox.SetValue(False)
        else:
            self.remember_checkbox.SetValue(True)
        toolbar.AddControl(self.remember_checkbox)
        toolbar.Realize()
        self.Bind(wx.EVT_MENU, self.OnPublishEntry, id=GL.PublishMenuID)
        self.Bind(wx.EVT_MENU, self.OnPublishText, id=GL.PublishTextMenuID)
        self.Bind(wx.EVT_MENU, self.OnPublish,id=GL.PublishToolID)

        self.Bind(wx.EVT_MENU,self.OnRollBack,id=GL.RollBackID)
        self.Bind(wx.EVT_MENU,self.OnRefreshTreeDir,id=GL.RefreshTreeDirID)
        self.Bind(wx.EVT_MENU,self.OnSvnCommitThread,id=GL.SvnCommitID)
        self.Bind(wx.EVT_MENU,self.OnSvnUpdateThread,id=GL.SvnUpdateID)
        self.Bind(wx.EVT_MENU,self.OnMenuHelp,id=GL.HelpID)
        self.Bind(wx.EVT_MENU,self.OnMenuViewSvnDir, id=GL.SvnDirViewID)
        self.Bind(wx.EVT_MENU,self.OnMenuViewGLogDir, id=GL.GLogViewID)
        self.Bind(wx.EVT_MENU,self.OnMenuViewLogDir, id=GL.LogViewID)
        self.Bind(wx.EVT_TEXT,self.OnGetUserName,id=GL.GetUserNameUID)
        self.Bind(wx.EVT_TEXT,self.OnGetPassword, id=GL.GetPasswordID)
        self.Bind(wx.EVT_MENU,self.OnRefreshLogThread,id=GL.RefreshLogID)

        self.user_input_num = 0
        self.pass_input_num = 0
        self.Bind(wx.EVT_CHECKBOX,self.OnSaveSvnAuthToFile, id=GL.RememberCheckBoxID)
        #self.username_text.SetValue("avyou")

    def OnHide(self, event):
        self.Hide()

    def OnClose(self, event):
        self.taskBarIcon.Destroy()
        self.Destroy()
        self.Close()

    # def StatusBarUI(self):
    #     ####状态栏
    #     statusBar = self.CreateStatusBar()
    #     self.SetStatusBar(statusBar)
    def StatusBarUI(self):
        self.statusbar = CustomStatusBar(self)
        self.SetStatusBar(self.statusbar)

    def OnMenuHelp(self,event):
        import wx.lib
        import wx.lib.dialogs
        dialog_texts = u'''
        1. 程序需要注册才可以使用，一台机器对应一个注册码.

        2. 发布文件时,请确保文件已经上传到SVN服务器，也就是说在点击"文件发布"按\n
        钮前，请先进行SVN提交，可以使用 TortoiseSVN 提交，也可以使用本工具\n
        的"SVN提交".

        3. 用户和密码请填各自的SVN用户名和密码.

        4. "工作目录" 请"打开"系统上对应的SVN工作目录.

        5. "自定义发布" 只支持文件发布，为了安全起见，不支持目录发布.'''

        dialog = wx.lib.dialogs.ScrolledMessageDialog(None,dialog_texts, u"使用帮助",
                                                  pos=wx.DefaultPosition, size=(500,300))
        dialog.ShowModal()
        dialog.Destroy()

    def OnStartTimeSyncThread(self,windows,feature,ntpservers):
        thread = WorkerThread(windows,feature,ntpServers=ntpservers)#创建一个线程
        thread.start()#启动线程

    def OnRegditThread(self,windows,feature,public_key,str_key,RegisterFile):
        thread = WorkerThread(windows,feature,public_key=public_key,str_key=str_key,RegisterFile=RegisterFile)#创建一个线程
        thread.start()#启动线程

    def MonitorThread(self,windows,feature):
        thread = WorkerThread(windows,feature)#创建一个线程
        thread.start()#启动线程


    def OnRefreshLogThread(self,event):
        if GL.Active is False:
            wx.MessageBox(u"程序未注册!",u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
            return
        self.RefreshData()
        thread = WorkerThread(self.MainFun,"refreshlog")
        thread.start()

    def OnContextMenu(self, event):
        self.Bind(wx.EVT_MENU, self.OnCopy, id=GL.popupID_Copy)
        self.Bind(wx.EVT_MENU, self.OnRemoveEntry, id=GL.popupID_Remove)
        menu = wx.Menu()
        item = wx.MenuItem(menu, GL.popupID_Copy,u"复制")
        menu.AppendItem(item)
        menu.Append(GL.popupID_Remove, u"移除")
        self.PopupMenu(menu)
        menu.Destroy()

    def OnMenuViewSvnDir(self,event):
        try:
            subprocess.Popen(["explorer.exe",GL.SvnWorkDir], shell=True)
        except:
            msg = u"打开SVN目录 %s 发生错误." % GL.SvnWorkDir
            LoadLog.LogMsg(GL.logger_sysLog.warning,msg)
            wx.MessageBox(msg, u"错误",style=wx.OK|wx.ICON_ERROR)


    def OnMenuViewGLogDir(self,event):
        try:
            subprocess.Popen(["explorer.exe",GL.GlogDir], shell=True)
        except:
            msg = u"打开全局日志目录 %s 发生错误." % GL.GlogDir
            LoadLog.LogMsg(GL.logger_sysLog.warning,msg)
            wx.MessageBox(msg, u"错误",style=wx.OK|wx.ICON_ERROR)

    def OnMenuViewLogDir(self,event):
        try:
            subprocess.Popen(["explorer.exe",GL.LogDir], shell=True)
        except:
            msg = u"打开本地日志目录 %s 发生错误." % GL.LogDir
            LoadLog.LogMsg(GL.logger_sysLog.warning,msg)
            wx.MessageBox(msg, u"错误",style=wx.OK|wx.ICON_ERROR)

    def SelectEntryList(self):
        #select_file_list = []
        Sel = self.rightpanel.page1.ChoiceListBox.GetSelections()
        select_file_list = [ self.rightpanel.page1.ChoiceListBox.GetString(item) for item in Sel ]
        return select_file_list

    def OnCopy(self, event):
        sf = self.SelectEntryList()
        sfiles = ""
        for efile in sf:
            sfiles = "".join([sfiles,efile,"\n"])
        #print sfiles
        self.dataObj = wx.TextDataObject()
        self.dataObj.SetText(sfiles)
        try:
            with wx.Clipboard.Get() as clipboard:
                clipboard.SetData(self.dataObj)
        except TypeError:
            wx.MessageBox(u"无法打开粘贴板", u"错误",style=wx.OK|wx.ICON_ERROR)

    # def OnExit(self,event):
    #     #self.taskBarIcon.Destroy()
    #     self.Destroy()
    #     self.Close()

    def OnOpenDir(self,event):
        dlg = wx.DirDialog(None, u"选择文件夹:", style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            GL.SvnWorkDir = dlg.GetPath()
            print GL.SvnWorkDir
            self.OnRefreshTreeDir()

        dlg.Destroy()

    def OnMenuSetting(self,event):
        from SettingUI import settingDlg
        self.dlgSetting  = dlg = settingDlg(u"设置")
        SvnWorkDir = dlg.SetUI.svnWorkDir_t.GetValue()
        dlg.Center()
        if dlg.ShowModal() == wx.ID_OK:
            self.MainFun = MainFun(GL.LIPaddr,GL.GlogDir,GL.SvnUrl,GL.SvnWorkDir,GL.SvnUser,GL.SvnPass,GL.SvnLogUrl,GL.logger_sysLog)
            from loadConfig import SaveConf,SaveSSHAuthToFile
            GetSaveConfDict,GetSaveSSHAuthDict = dlg.SetUI.GetDataFromUIAndEncrypt()
            SaveConf(self.ConfFile,GetSaveConfDict)
            SaveSSHAuthToFile(GetSaveSSHAuthDict,self.AuthFile,self.str_key,self.pass_private_key)

            if not (dlg.SetUI.svnUser_t.IsEmpty() and dlg.SetUI.svnPass_t.IsEmpty()):
                SvnUser = dlg.SetUI.svnUser_t.GetValue()
                SvnPass = dlg.SetUI.svnPass_t.GetValue()
                self.username_text.SetValue(SvnUser)
                self.password_text.SetValue(SvnPass)
                self.remember_checkbox.SetValue(True)
        dlg.SetUI.GetDataFromUI()
        GL.LPort = int(GL.LPort)
        GL.RPort = int(GL.RPort)
        if SvnWorkDir != GL.SvnWorkDir:
            self.OnRefreshTreeDir()
        #print GL.SvnWorkDir
        dlg.Destroy()

    def OnMenuAbout(self,event):
        dlg = MyAboutBox(None,(300, 200))
        dlg.ShowModal()
        dlg.Destroy()

    def OnMenuRegister(self,event):
        import  readHardware
        try:
            with open(GL.RegisterFile,"rb",-1) as f:
                rCode = pickle.load(f)
        except:
            rCode = ""
        machineCode = str(readHardware.get_disk_info(self.str_key)).lstrip("-")
        if len(rCode) != 0:
            deMachineCode = str(readHardware.DencryptForRegCode(rCode,self.public_key))
            if deMachineCode == machineCode:
                GL.Active = True
            else:
                GL.Active = False
        dialog = RegisterUI((500,400),machineCode,rCode,self.public_key)
        dialog.ShowModal()

    def OnSvnCommitThread(self,evt):
        if GL.Active is False:
            wx.MessageBox(u"程序未注册!",u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
            return
        self.RefreshData()
        thread = WorkerThread(self.MainFun,"svncommit")
        thread.start()

    def OnSvnUpdateThread(self,evt):
        if GL.Active is False:
            wx.MessageBox(u"程序未注册!",u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
            return
        self.RefreshData()
        thread = WorkerThread(self.MainFun,"svnupdate")
        thread.start()

    def OnGetUserName(self,event):
        if self.username_text.IsModified():
            self.user_input_num += 1
            #print self.user_input_num
            self.remember_checkbox.SetValue(False)
            if self.user_input_num == 1:
                self.OnSaveSvnAuthToFile()
            if self.user_input_num > 50:
                self.user_input_num = 0
                return

    def OnGetPassword(self,event):
        if self.password_text.IsModified():
            self.pass_input_num += 1
            self.remember_checkbox.SetValue(False)
            if self.pass_input_num == 1:
                self.OnSaveSvnAuthToFile()
            if self.pass_input_num > 50:
                self.pass_input_num = 0
                return

    def OnSaveSvnAuthToFile(self,event=None):
        if self.remember_checkbox.IsChecked():
            self.user_input_num = 0
            self.pass_input_num = 0
            GL.SvnUser = SvnUser = self.username_text.GetValue()
            GL.SvnPass = SvnPass = self.password_text.GetValue()
            from passEncrypt import GetKey,EncodeAES
            cipher = GetKey(self.str_key)
            SvnPass =  EncodeAES(cipher, SvnPass,32)
            GL.isSave = True
        else:
            SvnUser = ""
            SvnPass = ""
            GL.isSave = False
            GL.SvnUser = self.username_text.GetValue()
            GL.SvnPass = self.password_text.GetValue()
        UpdateSectionDict(self.ConfFile,self.DefaultConfDict,self.sections,"SVNConfig","SvnUser",SvnUser)
        UpdateSectionDict(self.ConfFile,self.DefaultConfDict,self.sections,"SVNConfig","SvnPass",SvnPass)


    def OnRefreshTreeDir(self,event=None):
        if GL.Active is False:
            wx.MessageBox(u"程序未注册!",u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
            return
        self.OnClearEntry()
        self.OnClearText()
        self.leftpanel.Destroy()
        #self._mgr.Destroy()
        #print GL.SvnWorkDir
        self.leftpanel = CustomTree(self,-1,GL.SvnWorkDir)
        #self.leftpanel.Hide()
        #self.leftpanel.Layout(0)
        self._mgr.AddPane(self.leftpanel,
                         wx.aui.AuiPaneInfo().
                         Left().Layer(1).BestSize((250, -1)).
                         MinSize((120, -1)).
                         #Floatable(self.allowAuiFloating).FloatingSize((240, 700)).
                         Caption(u"本地SVN目录树").
                         CloseButton(False).
                         Name(""))
        self._mgr.Update()
        self.leftpanel.Refresh()
        self.leftpanel.Bind(CT.EVT_TREE_ITEM_CHECKED,self.ItemChecked,id=GL.TreeID)



    def OnPublish(self,event):
        print "on publish"
        #print self.rightpanel.nb.GetSelection()
        if self.rightpanel.nb.GetSelection() == 0:
            print "111"
            self.OnPublishEntry(event)
        elif self.rightpanel.nb.GetSelection() == 1:
            self.OnPublishText(event)
        else:
            msg = u'请切换到"发布"选项卡页面.'
            wx.MessageBox(msg,u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
            return

    # def OnPublishTextThread(self,event):
    #     if GL.Active is False:
    #         wx.MessageBox(u"程序未注册!",u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
    #         return
    #     thread = WorkerThread(self,"publishText")
    #     thread.start()

    def OnPublishText(self,event):
        if GL.Active is False:
            wx.MessageBox(u"程序未注册!",u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
            return
        publishList = []
        error_list = []
        if self.rightpanel.page2.customUpdateText.IsEmpty():
            msg = u"文本框为空，请输入文件后再发布！"
            wx.MessageBox(msg,u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
            return
        self.RefreshData()
        Login,loginMsg = self.MainFun.AuthUserPass(GL.SvnUrl,GL.SvnUser,GL.SvnPass)
        if Login is False:
            wx.MessageBox(loginMsg,u"错误提示", style=wx.OK|wx.ICON_ERROR)
            return
        ##光标插入文本框末尾
        self.rightpanel.page2.customUpdateText.SetInsertionPointEnd()
        ##光标插入末尾后，获取最后的point
        end_point_num = self.rightpanel.page2.customUpdateText.GetInsertionPoint()
        ##所有的行
        all_line = self.rightpanel.page2.customUpdateText.GetRange(0,end_point_num).strip()
        #print all_line
        ##行列表
        line_list = all_line.split("\n")
        #print line_list
        for each_file in line_list:
            if each_file == "":
                continue
            #full_path_file = "".join([self.leftpanel.rootPathPrefix[0],each_file.replace("/",os.sep)])
            full_path_file = "\\".join([GL.SvnWorkDir,each_file.replace("/",os.sep)])
            print each_file
            print full_path_file
            if os.path.exists(full_path_file) and not os.path.isdir(full_path_file):
                publishList.append(each_file)
            else:
                error_list.append(each_file)
        if len(error_list) != 0:
            msg = u"格式不正确或文件不存在，请查看日志。"
            wx.MessageBox(msg, u"错误", style=wx.OK|wx.ICON_ERROR)
            for i in error_list:
                msg = u"文件 %s 不存在." % i
                LoadLog.LogMsg(GL.logger_PubLog.warning,msg)
            return
        msg = u"您确定要将列表中的文件发布到正式服务器吗?"
        dlg = wx.MessageBox(msg, u"信息确认", style=wx.YES_NO|wx.YES_DEFAULT|wx.ICON_INFORMATION)

        if dlg == wx.YES:
            try:
                self.client = sshHandle.SSHConect(GL.LIPaddr, GL.LPort,GL.sshUser,GL.sshPass,timeout=GL.sshTimeout)
                #self.client = sshHandle.SSHConect("192.168.2.15", 2215,"root","svn229develop#",timeout=5)

            except Exception,e:
                msg = u"连接服务器出错! %s" %e
                wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
                LoadLog.LogMsg(GL.logger_sysLog.warning,msg)
            else:
                self.client.publish_cmd(publishList,GL.webDir,self.BackupDir,GL.RwebDir,GL.RIPaddr,GL.RPort)
                self.client.close()
                try:
                    checkGlog = self.MainFun.initSvnLogDir()
                    print "log bool",checkGlog
                    if checkGlog is True:
                        checkGlog = self.MainFun.initSvnLogDir()
                        if checkGlog is True:
                            #print "error 1"
                            wx.MessageBox(u"全局日志写入失败text-01.",u"错误提示", style=wx.OK|wx.ICON_ERROR)
                            return
                    else:
                        print "write log"
                        self.MainFun.writeGlobal_log(GL.PublishList,GL.chandlers,GL.logger_gPubLog,"publish")
                        if len(GL.backup_list) != 0:
                            self.MainFun.writeGlobal_log(GL.backup_list,GL.dhandlers,GL.logger_gBakLog,"backup")
                except:
                    print "error log"
                    wx.MessageBox(u"全局日志写入失败text-02.",u"错误提示", style=wx.OK|wx.ICON_ERROR)
                    return
                else:
                    self.rightpanel.page3.BakRollText.SetItems(GL.backup_list)
                    GL.loadGBackupLog = True
                    GL.loadGUpdateLog = True
        else:
            return

    def OnClearText(self,event=None):
        self.rightpanel.page2.customUpdateText.SetValue("")


    # def OnPublishEntryThread(self,event):
    #     if GL.Active is False:
    #         wx.MessageBox(u"程序未注册!",u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
    #         return
    #     thread = WorkerThread(self,"publishEntry")
    #     thread.start()
    def OnPublishEntry(self,event):
        if GL.Active is False:
            wx.MessageBox(u"程序未注册!",u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
            return

        self.PublishList = [self.rightpanel.page1.ChoiceListBox.GetString(i) for i in range(self.rightpanel.page1.ChoiceListBox.GetCount())]
        if len(self.PublishList) == 0:
            msg = u"列表为空，请选择文件后再发布！"
            wx.MessageBox(msg,u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
            return
        self.RefreshData()
        Login,loginMsg = self.MainFun.AuthUserPass(GL.SvnUrl,GL.SvnUser,GL.SvnPass)
        if Login is False:
            wx.MessageBox(loginMsg,u"错误提示", style=wx.OK|wx.ICON_ERROR)
            return
        msg = u"您确定要将列表中的文件发布到正式服务器吗?"
        dlg = wx.MessageBox(msg, u"信息确认", style=wx.YES_NO|wx.YES_DEFAULT|wx.ICON_INFORMATION)
        if dlg == wx.YES:
            try:
                #print type(GL.LPort)
                self.client = sshHandle.SSHConect(GL.LIPaddr, GL.LPort,GL.sshUser,GL.sshPass,timeout=GL.sshTimeout)
                #self.client = sshHandle.SSHConect("192.168.2.15", 2215,"root","svn229develop#",timeout=5)
            except Exception,e:
                #print GL.LIPaddr, type(GL.LPort),GL.sshUser,GL.sshPass
                msg = u"连接服务器出错,error: %s" %e
                wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
                LoadLog.LogMsg(GL.logger_sysLog.warning,msg)
            else:
                #print "/".join([self.BackupDir,self.leftpanel.custom_tree.GetRootItem()])
                self.client.publish_cmd(self.PublishList,GL.webDir,self.BackupDir,GL.RwebDir,GL.RIPaddr,GL.RPort)
                #dlg = MyProgressDialog(client,PublishList)
                #dlg.ShowModal()
                self.client.close()
                #self.rightpanel.page3.BakRollText.SetItems([])
                self.rightpanel.page3.BakRollText.SetItems(GL.backup_list)
                #print self.PublishList
                checkGlog = self.MainFun.initSvnLogDir()
                #print checkGlog
                if checkGlog is True:
                    checkGlog = self.MainFun.initSvnLogDir()
                    if checkGlog is True:
                        wx.MessageBox(u"发布信息写入全局日志失败entry-01.",u"错误提示", style=wx.OK|wx.ICON_ERROR)
                        return
                else:
                    try:
                        self.MainFun.writeGlobal_log(GL.PublishList,GL.chandlers,GL.logger_gPubLog,"publish")
                        if len(GL.backup_list) != 0:
                            self.MainFun.writeGlobal_log(GL.backup_list,GL.dhandlers,GL.logger_gBakLog,"backup")
                    except:
                        wx.MessageBox(u"发布信息写入全局日志失败entry-02.",u"错误提示", style=wx.OK|wx.ICON_ERROR)
                        return
                GL.loadGBackupLog = True
                GL.loadGUpdateLog = True
        #dlg.Destroy()

    def OnRollBack(self,event):
        if GL.Active is False:
            wx.MessageBox(u"程序未注册!",u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
            return
        self.RefreshData()
        Login,loginMsg = self.MainFun.AuthUserPass(GL.SvnUrl,GL.SvnUser,GL.SvnPass)
        if Login is False:
            wx.MessageBox(loginMsg,u"错误提示", style=wx.OK|wx.ICON_ERROR)
            return
        if self.rightpanel.nb.GetSelection() != 2:
            msg = u'请切换到"备份还原"选项卡页面.'
            wx.MessageBox(msg,u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
            return
        self.RollBackList = self.rightpanel.page3.BakRollText._dest.GetItems()
        if len(self.RollBackList) == 0:
            msg = u"还原列表为空，请选择备份文件后再还原！"
            wx.MessageBox(msg,u"信息提示", style=wx.OK|wx.ICON_INFORMATION)
            return
        else:
            msg = u"您确定要将这些备份文件还原到正式服务器吗?"
            dlg = wx.MessageBox(msg, u"信息确认", style=wx.YES_NO|wx.YES_DEFAULT|wx.ICON_INFORMATION)
            if dlg == wx.YES:
                try:
                    self.client = sshHandle.SSHConect(GL.LIPaddr, GL.LPort,GL.sshUser,GL.sshPass,timeout=GL.sshTimeout)
                except:
                    msg = u"连接服务器出错!"
                    wx.MessageBox(msg, style=wx.OK|wx.ICON_ERROR)
                    LoadLog.LogMsg(GL.logger_sysLog.error,msg)
                else:
                    print self.BackupDir
                    self.client.rollback_cmd(self.RollBackList,GL.RwebDir,self.BackupDir,GL.RIPaddr, GL.RPort)
                    self.rightpanel.page3.BakRollText._source.SetItems(GL.backup_list)
                    self.rightpanel.page3.BakRollText._dest.SetItems([])
                    self.client.close()
                    checkGlog = self.MainFun.initSvnLogDir()
                    if checkGlog is True:
                        checkGlog = self.MainFun.initSvnLogDir()
                        if checkGlog is True:
                            wx.MessageBox(u"备份信息写入全局日志失败bak-01.",u"错误提示", style=wx.OK|wx.ICON_ERROR)
                            return
                    else:
                        try:
                            self.MainFun.writeGlobal_log(GL.rollbacked_list,GL.chandlers,GL.logger_gPubLog,"rollback")
                        except:
                            wx.MessageBox(u"备份信息写入全局日志失败bak-02.",u"错误提示", style=wx.OK|wx.ICON_ERROR)
                            return

    def RefreshData(self):
        GL.SvnUser = self.username_text.GetValue()
        #print "refresh data:",GL.SvnUser
        GL.SvnPass = self.password_text.GetValue()
        self.MainFun = MainFun(GL.LIPaddr,GL.GlogDir,GL.SvnUrl,GL.SvnWorkDir,GL.SvnUser,GL.SvnPass,GL.SvnLogUrl,GL.logger_sysLog)

    def RemoveEntry(self):
        #Sel = self.ChoiceListBox.GetCursor()
        Sel = self.rightpanel.page1.ChoiceListBox.GetSelections()
        pos = 0
        #print Sel
        for i in Sel:
            idx = i - pos
            #DelFile = "/".join([self.leftpanel.rootNote, self.rightpanel.page1.ChoiceListBox.GetString(idx)])
            DelFile = self.rightpanel.page1.ChoiceListBox.GetString(idx)
            #print self.leftpanel.rootPathPrefix[0]
            #FullPath = "\\".join([self.leftpanel.rootPathPrefix[0],DelFile.replace("/",os.sep)])
            FullPath = "\\".join([GL.SvnWorkDir,DelFile.replace("/",os.sep)])
            print FullPath
            FullPathItem = self.leftpanel.AllFileDiect[FullPath]
            #print DelFile
            self.rightpanel.page1.ChoiceListBox.Delete(idx)
            self.leftpanel.custom_tree.CheckItem(FullPathItem,checked=False)
            #print idx
            pos = pos + 1
    def OnRemoveEntry(self,event):
        #Sel = self.ChoiceListBox.GetCursor()
        self.RemoveEntry()
    def OnClearEntry(self,event=None):
        self.rightpanel.page1.ChoiceListBox.Clear()
        print self.leftpanel.root
        self.leftpanel.custom_tree.CheckChilds(self.leftpanel.root,checked=False)

    def SetCheckBox(self):
        self.leftpanel.custom_tree.GetSelection()

    def GetPath(self,alist,evtGetItem):
        #path_list.append(evtGetItem)
        pItem = self.leftpanel.custom_tree.GetItemParent(evtGetItem)
        if pItem is not None:
            pfile = self.leftpanel.custom_tree.GetItemText(pItem)
            #print pfile
            if pfile == self.leftpanel.rootShow:
                pfile = self.leftpanel.rootNote
            alist.append(pfile)
            self.GetPath(alist,pItem)
        select_file = self.leftpanel.custom_tree.GetItemText(evtGetItem)
        #fullPath = "/" + "/".join(reversed(alist)) + "/" + str(select_file)
        fullPath = "/" + "/".join(reversed(alist)) + "/" + str(select_file)
        return fullPath

    ##选择文件，添加到列表
    def ItemChecked(self, event):
        #print("Somebody checked something")
        item = event.GetItem()
        alist = []
        spath = self.GetPath(alist,item)
        spath = "/".join(spath.split("/")[2:])
        if item.IsChecked():
            #print spath
            self.rightpanel.page1.ChoiceListBox.Append(spath)
        else:
            findex = self.rightpanel.page1.ChoiceListBox.FindString(spath)
            try:
                self.rightpanel.page1.ChoiceListBox.Delete(findex)
            except:
                pass


if __name__ == "__main__":

    start = time.clock()
    #LoadLog.LogMain()
    ListDir = GL.SvnWorkDir

    app = wx.App()
    frame = MyFrame(None,-1,"WEBPer",(800,600))
    app.SetTopWindow(frame)
    frame.Center()
    frame.Show()
    app.MainLoop()

