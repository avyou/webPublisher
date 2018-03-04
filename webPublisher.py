#coding:utf-8
import wx
import time
from libs.mainFrame import MyFrame
import libs.globalDef as GL

class MySplashScreen(wx.SplashScreen):

    def __init__(self, parent=None):
        aBitmap = wx.Image(name = "icons/startup.jpg").ConvertToBitmap()
        splashStyle = wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT
        splashDuration = GL.SPLASH_TIME
        wx.SplashScreen.__init__(self, aBitmap, splashStyle,splashDuration, parent)
        self.Bind(wx.EVT_CLOSE, self.OnExit)
        wx.Yield()

    def OnExit(self, evt):
        self.Hide()
        # from mainFun import MainFun
        # self.MainFun = MainFun(GL.GlogDir,GL.SvnUrl,GL.SvnWorkDir,GL.SvnUser,GL.SvnPass,GL.SvnLogUrl,GL.logger_sysLog)
        # self.MainFun.initSvnLogDir()
        # LoadLog.DefineLog(self)
        frame = MyFrame(None,-1,"Web Publisher",(800,600))
        app.SetTopWindow(frame)
        frame.Center()
        frame.Show(True)
        evt.Skip()

class MyApp(wx.App):
    def OnInit(self):
        ##获取实例名称
        self.name = "%s-%s" % (self.GetAppName(), wx.GetUserId())
        ##要检测的实例
        self.instance = wx.SingleInstanceChecker(self.name)
        ##查看实例是否已经运行，如果已经运行则初始化失败退出
        if self.instance.IsAnotherRunning():
            wx.MessageBox(u"Web Publisher，已经在运行了！",u"提示")
            return False
        MySplash = MySplashScreen()
        MySplash.Show()
        return True

if __name__ == '__main__':
    GL.start = time.clock()
    app = MyApp()
    app.MainLoop()