#coding:utf-8
import wx
class TaskBarIcon(wx.TaskBarIcon):

    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon(name='icons/logo.ico', type=wx.BITMAP_TYPE_ICO), u'进程监控管理器 v1.0')
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)
        self.Bind(wx.EVT_MENU, self.OnShow, id=1990)
        #self.Bind(wx.EVT_MENU, self.frame.OnAbout, id=wx.ID_ABOUT)
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
        menu.Append(1990, u'显示主窗口')
        menu.AppendSeparator()
        menu.Append(wx.ID_ABOUT, u'关于')
        menu.AppendSeparator()
        menu.Append(wx.ID_EXIT, u'退出')
        return menu

