#coding:utf-8
import sys

import wx                  # This module uses the new wx namespace
import wx.html
import wx.lib.wxpTag

#---------------------------------------------------------------------------

class HtmlWin(wx.html.HtmlWindow):

    def __init__(self, parent, id=-1, size=(400, 220)):

        wx.html.HtmlWindow.__init__(self, parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()


    def OnLinkClicked(self, link):

        wx.LaunchDefaultBrowser(link.GetHref())

class MyAboutBox(wx.Dialog):
    text = u'''
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title></title>
</head>

<body bgcolor="#E8E8E8">
<table  width="100%", cellspacing="0"
cellpadding="0">
<tr>
    <td align="center" bgcolor="#B7CCBE">
    <h3>Web Publisher v1.1</h3><br>
    作者：赵子发<br>
    </td>
</tr>
</table>

<p>欢迎使用 <b>Web Publisher ！</b></p> <p>它是一个WEB发布工具，与SVN结合方便的将web文件更新或发布到正式网站上。</br>
  </p>
<p>同时可以实现网站文件自动备份，还原，SVN提交，SVN更新，文件更新与备份列表<br>
<p>的日志查看等功能。</p>
<br>
<p>当前版本：1.1 &nbsp;&nbsp;&nbsp;开发语言： python </p>
<p><font size="3">联系：avyou55@gmail.com</font></p>
<p>2014-2，广州</p>
</body>
</html>
'''
    def __init__(self, parent,size=(400,200)):
        wx.Dialog.__init__(self, parent, -1, u'关于 Web Publisher v1.1',size=size,
                           style=wx.DEFAULT_DIALOG_STYLE)
        html = HtmlWin(self)
        html.SetPage(self.text)
        ir = html.GetInternalRepresentation()
        html.SetSize( (ir.GetWidth()+20, ir.GetHeight()+5) )
        #html.SetSize( (400, 320) )
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)


if __name__ == '__main__':
    app = wx.App()
    dlg = MyAboutBox(None)
    dlg.ShowModal()
    dlg.Destroy()
    app.MainLoop()