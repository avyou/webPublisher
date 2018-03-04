#coding:utf-8
import wx
import time
import pysvn
import urllib2
import base64
import wx.dataview as dv
import globalDef as GL

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
        self.text_head = text_head = wx.StaticText(self,label=u"更改的文件：")
        self.dvlc = dvlc = dv.DataViewListCtrl(self,size=(400,250))

        self.commitBtn = regBtn = wx.Button(self,label=u"提交",id=GL.Commit_OK_ID)
        self.cancelBtn = cancelBtn = wx.Button(self,label=u"取消",id = GL.Commit_Cancel_ID)

        dvlc.AppendTextColumn(u'文件', width=300)
        dvlc.AppendTextColumn(u'状态', width=100)
        #dvlc.AppendTextColumn(u'状态', width=80)

        self.allCommitList = self.CheckSvnFile()
        for itemvalues in self.allCommitList:
            print itemvalues
            self.dvlc.AppendItem(itemvalues)

        if len(self.allCommitList) == 0:
            self.commitBtn.Disable()
        self.DvlcSizer = wx.BoxSizer()
        self.DvlcSizer.Add(dvlc, 1,wx.ALL,5)
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.vsizer.Add(self.text_head,0,wx.TOP|wx.LEFT,10)
        self.vsizer.Add(self.DvlcSizer,0,wx.EXPAND|wx.ALL,5)
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer.Add(self.commitBtn,0,wx.EXPAND|wx.ALL,5)
        self.hsizer.Add(cancelBtn,0,wx.EXPAND|wx.ALL,5)
        self.vsizer.Add(self.hsizer,0,wx.ALIGN_RIGHT|wx.ALL,5)
        self.SetSizer(self.vsizer)

        self.Bind(wx.EVT_BUTTON,self.OnOKCommit,id = GL.Commit_OK_ID)
        self.Bind(wx.EVT_BUTTON,self.OnCancel,id = GL.Commit_Cancel_ID)

    def AuthUserPass(self):
        base64string = base64.encodestring('%s:%s' % (self.username, self.password))[:-1]
        authheader =  "Basic %s" % base64string
        req = urllib2.Request(self.url,data=None,headers={"Authorization": authheader})
        try:
            handle = urllib2.urlopen(req)
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

        # if len(list_unversioned) != 0:
        #     #print list_unversioned
        #     for efile in list_unversioned:
        #         allCommitList.append([efile,"non-versioned"])
        #         #self.client.add(efile)
        #         #self.client.checkin(efile, " ")
        [ allCommitList.append([efile,"non-versioned"]) for efile in list_unversioned if len(list_unversioned) != 0 ]

        # if len(list_added) != 0:
        #     #print list_added
        #     for efile in list_added:
        #         #self.client.checkin(efile," ")
        #         allCommitList.append([efile,"added"])

        [ allCommitList.append([efile,"added"]) for efile in list_added if len(list_added) != 0 ]

        # if len(list_missing) != 0:
        #     print list_missing
        #     for efile in list_missing:
        #         #self.client.remove(efile)
        #         #self.client.checkin(efile, " ")
        #         allCommitList.append([efile,"missing"])

        [ allCommitList.append([efile,"missing"]) for efile in list_missing if len(list_missing) != 0 ]

        # if len(list_modified) != 0:
        #     #print list_modified
        #     for efile in list_modified:
        #         #self.client.checkin(efile," ")
        #         allCommitList.append([efile,"modified"])

        [ allCommitList.append([efile,"modified"]) for efile in list_modified if len(list_modified) != 0 ]

        # if len(list_removed) != 0:
        #     #print list_removed
        #     for efile in list_removed:
        #         #self.client.checkin(efile, " ")
        #         allCommitList.append([efile,"removed"])

        [allCommitList.append([efile,"removed"]) for efile in list_removed if len(list_removed) != 0 ]

        # if len(list_conflicted) != 0:
        #     #print list_conflicted
        #     #msg = u"有冲突文件，请到SVN目录操作"
        #     #print msg
        #     for efile in list_conflicted:
        #         allCommitList.append([efile,"conflicted"])
        #
        # return allCommitList

        [ allCommitList.append([efile,"conflicted"]) for efile in list_conflicted  if len(list_conflicted) != 0 ]

        return allCommitList

    def OnOKCommit(self,event=None):
        self.Hide()
        self.allCommitList = self.CheckSvnFile()
        self.client.callback_get_login = self.get_login
        Login,msg = self.AuthUserPass()
        if Login is True:
            count = 0
            fnum = len(self.allCommitList)
            dlg = wx.ProgressDialog(u"进程条",u"正在提交更新文件到SVN服务器，请稍等...",maximum = fnum,style = 0
                                | wx.PD_APP_MODAL| wx.PD_ESTIMATED_TIME| wx.PD_REMAINING_TIME|wx.PD_AUTO_HIDE)
            dlg.ShowModal()
            self.keepGoing = True
            for itemvalues in self.allCommitList:
                if self.keepGoing is False:
                    break
                if itemvalues[1] == "conflicted":
                    msg = u"提交列表中有冲突文件,请到指定SVN目录进行操作."
                    wx.MessageBox(msg,style=wx.ICON_ERROR)
                    return
                if itemvalues[1] == "non-versioned":
                    self.client.add(itemvalues[0])
                if itemvalues[1] == "missing":
                    self.client.remove(itemvalues[0])
                self.client.checkin(itemvalues[0]," ")
                count += 1
                (self.keepGoing,skip) = dlg.Update(count)
            self.Destroy()
            dlg.Destroy()
            if self.keepGoing is True:
                wx.MessageBox(u"文件提交完成.", u"完成确认", style=wx.OK|wx.ICON_INFORMATION)

    def OnCancel(self,event):
        self.Destroy()

class SvnUpdateUI(SvnCommitUI):

    def __init__(self,username,password,url,svnDir,title,size):
         SvnCommitUI.__init__(self,username=username,password=password,url=url,svnDir=svnDir,title=title,size=size)

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
        #self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.vsizer.Add(self.commitBtn,0,wx.ALIGN_CENTER_HORIZONTAL)
        #self.hsizer.Add(cancelBtn,0,wx.EXPAND|wx.ALL,5)
        #self.vsizer.Add(self.hsizer,0,wx.ALIGN_RIGHT|wx.ALL,5)
        self.SetSizer(self.vsizer)

        self.Bind(wx.EVT_BUTTON,self.OnOKUpdate,id = GL.Update_OK_ID)
        #self.Bind(wx.EVT_BUTTON,self.OnCancel,id = GL.Commit_Cancel_ID)

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