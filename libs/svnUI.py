#coding:utf-8
import wx
import time
import pysvn
import urllib2
import base64
from ObjectListView import ObjectListView, ColumnDefn
import wx.dataview as dv
import globalDef as GL

class Results(object):
    def __init__(self,filename, filestatus):
        """Constructor"""
        #self.uid = uid
        self.filename = filename
        self.filestatus = filestatus


class SvnCommitUI(wx.Dialog):

    def __init__(self,username,password,url,svnDir,title,size):
        wx.Dialog.__init__(self, None, -1,title=title, size=size)
        self.username = username
        self.password = password
        self.svnDir = svnDir
        self.url = url
        self.client = pysvn.Client()
        self.UI()


    def UI(self):
        entry = self.client.info(self.svnDir)
        self.rev_num = entry.revision.number
        version_info = u'现版本库为： %s' % self.rev_num
        self.text_head  = wx.StaticText(self,label=version_info)

        mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.resultsOlv = ObjectListView(self, style=wx.LC_REPORT|wx.SUNKEN_BORDER)
        self.resultsOlv.SetEmptyListMsg(u"没有更改的内容")
        self.filenameColumn = ColumnDefn(u"文件", "left", 350, "filename")
        self.statusColumn = ColumnDefn(u"状态", "left", 100, "filestatus")

        AllSvnList = self.setResults()

        checkBtn = wx.Button(self, label=u"全选")
        uncheckBtn = wx.Button(self, label=u"清空")

        self.button_save = wx.Button(self,label=u"提交",id=GL.CommitSvnOK)
        if len(AllSvnList) == 0:
            self.button_save.Disable()
        button_cancel = wx.Button(self,label=u"取消",id=wx.ID_CANCEL)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        btnSizer.Add(checkBtn, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        btnSizer.Add(uncheckBtn, 0, wx.ALL|wx.ALIGN_LEFT, 5)
        btnSizer.Add(self.button_save, 0, wx.ALL|wx.ALIGN_RIGHT, 5)
        btnSizer.Add(button_cancel, 0, wx.ALL|wx.ALIGN_RIGHT, 5)

        mainSizer.Add(self.text_head, 0, wx.ALL, 5)
        mainSizer.Add(self.resultsOlv, 1, wx.EXPAND|wx.ALL, 5)
        mainSizer.Add(btnSizer, 0, wx.CENTER|wx.ALL, 5)
        self.SetSizer(mainSizer)

        checkBtn.Bind(wx.EVT_BUTTON, self.onCheck)
        uncheckBtn.Bind(wx.EVT_BUTTON, self.onUncheck)
        self.Bind(wx.EVT_BUTTON,self.OnCommitToSvn,id=GL.CommitSvnOK)
        button_cancel.Bind(wx.EVT_BUTTON,self.OnCancel)

    def GetSvnObjList(self,alist):
        data = []
        for each in alist:
            x,y = each
            i = Results(x,y)
            data.append(i)
        return data

    def onCheck(self, event):
        objects = self.resultsOlv.GetObjects()
        for obj in objects:
            self.resultsOlv.SetCheckState(obj, True)
        self.resultsOlv.RefreshObjects(objects)

    def onUncheck(self, event):
        objects = self.resultsOlv.GetObjects()

        for obj in objects:
            self.resultsOlv.SetCheckState(obj, False)
        self.resultsOlv.RefreshObjects(objects)

    def OnCommitToSvn(self,event):
        self.SelectFileList = []
        allobj = self.resultsOlv.GetObjects()
        for obj in allobj:
            if self.resultsOlv.IsChecked(obj) == True:
                self.SelectFileList.append([obj.filename,obj.filestatus])
        #print self.SelectFileList

        self.client.callback_get_login = self.get_login
        Login,msg = self.AuthUserPass()
        if Login is True:
            commitFileList = []
            for itemvalues in self.SelectFileList:
                if itemvalues[1] == u"conflicted":
                    msg = u"提交列表中有冲突文件,提交失败，请到指定SVN目录进行操作."
                    wx.MessageBox(msg,style=wx.ICON_ERROR)
                    return
                if itemvalues[1] == u"unversioned":
                    self.client.add(itemvalues[0])
                if itemvalues[1] == u"missing":
                    self.client.remove(itemvalues[0])
                commitFileList.append(itemvalues[0])
                #self.svnCommitFun.client.checkin(itemvalues[0]," ")
            self.client.checkin(commitFileList," ")
            wx.MessageBox(u"文件提交完成.", u"完成确认", style=wx.OK|wx.ICON_INFORMATION)
            revs = self.client.update(self.svnDir, depth=pysvn.depth.infinity, depth_is_sticky=True)
            self.rev_num = revs[-1].number
            #print self.rev_num
            self.Destroy()
            dialog = SvnCommitUI(self.username,self.password,self.url,self.svnDir,u"SVN文件提交",(500, 350))
            dialog.Center()
            dialog.ShowModal()
            #self.Destroy()

    def AuthUserPass(self):
        base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
        authheader =  "Basic %s" % base64string
        req = urllib2.Request(self.url,data=None,headers={"Authorization": authheader})
        try:
            #handle = urllib2.urlopen(req)
            urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            if e.code == 401:
                self.msg = "认证失败,错误信息: %s" %e
                self.Login = False
            else:
                self.msg = "其它错误,错误信息: %s" %e
                self.Login = False
        except:
            self.msg = u"错误"
            self.Login = False
        else:
            self.msg = u"认证通过"
            self.Login = True
        return self.Login,self.msg

    def get_login(self, realm, username, may_save):
        data = (True, self.username, self.password, False)
        return data

    def CheckSvnFile(self):
        allCommitList = []
        changes = self.client.status(self.svnDir)
        list_added =  [f.path for f in changes if f.text_status == pysvn.wc_status_kind.added]
        list_missing =  [f.path for f in changes if f.text_status == pysvn.wc_status_kind.missing]
        list_removed =  [f.path for f in changes if f.text_status == pysvn.wc_status_kind.deleted]
        list_modified =  [f.path for f in changes if f.text_status == pysvn.wc_status_kind.modified]
        list_conflicted = [f.path for f in changes if f.text_status == pysvn.wc_status_kind.conflicted]
        list_unversioned =  [f.path for f in changes if f.text_status == pysvn.wc_status_kind.unversioned]

        [ allCommitList.append([efile,u"unversioned"]) for efile in list_unversioned if len(list_unversioned) != 0 ]
        [ allCommitList.append([efile,u"added"]) for efile in list_added if len(list_added) != 0 ]
        [ allCommitList.append([efile,u"missing"]) for efile in list_missing if len(list_missing) != 0 ]
        [ allCommitList.append([efile,u"modified"]) for efile in list_modified if len(list_modified) != 0 ]
        [allCommitList.append([efile,u"deleted"]) for efile in list_removed if len(list_removed) != 0 ]
        [ allCommitList.append([efile,u"conflicted"]) for efile in list_conflicted  if len(list_conflicted) != 0 ]

        return allCommitList


    def OnCancel(self,event):
        self.Destroy()

    def setResults(self):
        self.resultsOlv.SetColumns([self.filenameColumn,self.statusColumn,])
        self.resultsOlv.CreateCheckStateColumn()


        AllSvnList = self.CheckSvnFile()
        self.SvnObjData = self.GetSvnObjList(AllSvnList)
        self.resultsOlv.SetObjects(self.SvnObjData)
        return AllSvnList


class SvnUpdateUI(SvnCommitUI):

    def __init__(self,username,password,url,svnDir,title,size):
        #SvnCommitUI.__init__(self,username=username,password=password,url=url,svnDir=svnDir,title=title,size=size)
        wx.Dialog.__init__(self, None, -1,title=title, size=size)
        self.username = username
        self.password = password
        self.svnDir = svnDir
        self.url = url
        self.client = pysvn.Client()
        self.UI()

    def UI(self):
        old_rev,new_rev,msg,update = self.svnUpdate()

        version_info = u'%s，现版本库为： %s' % (msg,new_rev)

        svnUpdateAllList = self.SvnUpdateList(old_rev,new_rev)
        self.text_head = text_head = wx.StaticText(self,label=version_info)
        self.dvlc = dvlc = dv.DataViewListCtrl(self,size=(400,250))

        self.commitBtn = regBtn = wx.Button(self,label=u"确定",id=GL.Update_OK_ID)
        #self.cancelBtn = cancelBtn = wx.Button(self,label=u"取消",id = GL.Update_Cancel_ID)

        dvlc.AppendTextColumn(u'已操作', width=100)
        dvlc.AppendTextColumn(u'文件', width=300)

        [self.dvlc.AppendItem(itemvalues) for itemvalues in  svnUpdateAllList]

        self.DvlcSizer = wx.BoxSizer()
        self.DvlcSizer.Add(dvlc, 1,wx.ALL,5)
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.vsizer.Add(self.text_head,0,wx.TOP|wx.LEFT,10)
        self.vsizer.Add(self.DvlcSizer,0,wx.EXPAND|wx.ALL,5)
        self.vsizer.Add(self.commitBtn,0,wx.ALIGN_CENTER_HORIZONTAL)
        self.SetSizer(self.vsizer)

        self.Bind(wx.EVT_BUTTON,self.OnOKUpdate,id = GL.Update_OK_ID)
        #self.Bind(wx.EVT_BUTTON,self.OnCancel,id = GL.Commit_Cancel_ID)

    def OnCancel(self,event):
        self.Destroy()

    def SvnUpdateList(self,old_rev,new_rev):
        head = pysvn.Revision(pysvn.opt_revision_kind.number, old_rev)
        end = pysvn.Revision(pysvn.opt_revision_kind.number, new_rev)

        FILE_CHANGE_INFO = {    pysvn.diff_summarize_kind.normal: ' ',
                                pysvn.diff_summarize_kind.modified: u'修改',
                                pysvn.diff_summarize_kind.delete: u'删除',
                                pysvn.diff_summarize_kind.added: u'添加',
                            }

        summary = self.client.diff_summarize(self.svnDir, head, self.svnDir, end)
        UpdateAllList = []
        for info in summary:
            path = info.path
            if info.node_kind == pysvn.node_kind.dir:
                path += '/'
            file_changed = FILE_CHANGE_INFO[info.summarize_kind]
            prop_changed = ' '
            if info.prop_changed:
                prop_changed = 'M'
            UpdateAllList.append([file_changed + prop_changed, path])
        #print UpdateAllList
        return  UpdateAllList

    def svnUpdate(self):
        entry = self.client.info(self.svnDir)
        old_rev = entry.revision.number
        self.client.callback_get_login = self.get_login
        Login,LoginMsg = self.AuthUserPass()
        if Login is True:
            try:
                revs = self.client.update(self.svnDir, depth=pysvn.depth.infinity, depth_is_sticky=True)
            except pysvn.ClientError:
                msg =  u"认证失败，无法更新"
                new_rev = old_rev
                update = False
                #wx.MessageBox(msg, u"信息", style=wx.OK|wx.ICON_ERROR)
            except:
                msg = u"SVN 更新失败，请到 SVN 目录操作"
                new_rev = old_rev
                update = False
                #wx.MessageBox(msg, u"信息", style=wx.OK|wx.ICON_ERROR)
            else:
                msg = u"完成更新"
                new_rev = revs[-1].number
                update = True
        else:
            msg =  u"认证失败，无法更新"
            new_rev = old_rev
            update = False

        return old_rev,new_rev,msg,update

    def OnOKUpdate(self,event):
        self.Destroy()



if __name__ == '__main__':
    svnDir = "d:\\demo3"
    svnUrl = "http://192.168.2.15:8080/svn/demo"
    svnUser = "avyou"
    svnPass = "123456"
    app = wx.App()
    app.MainLoop()
    dialog = SvnUpdateUI(svnUser,svnPass,svnUrl,svnDir,u"SVN更新",(450,380))
    dialog.Center()
    dialog.ShowModal()

    #dialog.Destroy()