#coding:utf-8
import wx
import paramiko
import globalDef as GL
import os
import logHandler as LoadLog
import time

class MyProgressDialog(wx.Dialog):
    def __init__(self):
        """Constructor"""
        wx.Dialog.__init__(self, None, title="Progress")
        self.count = 0
        self.progress = wx.Gauge(self, range=20)
        #self.client = ssh_client
        #self.publish_list = publish_list
        #self.fnum = len(publish_list)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.progress, 0, wx.EXPAND)
        self.SetSizer(sizer)
        #pub.subscribe(self.updateProgress, "update")
        #self.updateProgress()
    #----------------------------------------------------------------------
    #def updateProgress(self):
        #self.client.publish_cmd(self.publish_list,GL.RHost,self.progress)
        #
        # self.count += 1
        # if self.count >= self.fnum:
        # self.Destroy()
        # self.progress.SetValue(self.count)
class SSHConect():
    def __init__(self, hostname, port, username, password=None, key_filename=None,timeout=None):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.timeout = timeout
        self.client = None
        self.connect()
    def connect(self):
        #print self.port
        #print self.password
        if self.client is None:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.hostname, self.port, self.username, self.password, key_filename=self.key_filename,timeout=self.timeout)

    def OpenUpload(self,rhost,monitor_dir,monitor_upload_file,rport=22):
        cmd_openUpload = """ssh -p %d %s  'test ! -d %s && mkdir -pv %s;\
        echo "0">%s  && chmod 640 %s'""" \
                         %(rport,rhost,monitor_dir,monitor_dir,monitor_upload_file,monitor_upload_file)
        #LoadLog.LogMsg(GL.logger_sysLog.info,u"打开上传")
        stdin, stdout, stderr = self.client.exec_command(cmd_openUpload)
        exit_status = stdout.channel.recv_exit_status()
        message = stdout.readlines()
        error = stderr.readlines()
        print message,exit_status
        if len(error)>0 :
            msg = u"打开允许上传失败,错误信息:%s" % message
            LoadLog.LogMsg(GL.logger_sysLog.error,msg)
        else:
            LoadLog.LogMsg(GL.logger_sysLog.info,u"已经开启上传选项")

    def ShutdownUpload(self,rhost,monitor_upload_file,rport=22):
        cmd_shutdownUpload = """ssh -p %d %s  'echo "1">%s && chmod 640 %s'""" %(rport,rhost,monitor_upload_file,monitor_upload_file)
        stdin, stdout, stderr = self.client.exec_command(cmd_shutdownUpload)
        exit_status = stdout.channel.recv_exit_status()
        message = stdout.readlines()
        error = stderr.readlines()
        if len(error)>0 or  exit_status != 0:
            msg = u"未能正常关闭上传，错误信息:%s" % message
            LoadLog.LogMsg(GL.logger_sysLog.error,msg)
        else:
            LoadLog.LogMsg(GL.logger_sysLog.info,u"已经关闭上传选项")

    def publish_cmd(self,flist,LocalDir,BackupDir,RemoteDir,rhost,rport=22):
        self.connect()
        self.OpenUpload(GL.RIPaddr,GL.MonitorDir,GL.Monitor_Upload_File,GL.RPort)
        count = 0
        fnum = len(flist)
        #update_list = []
        GL.PublishList = []
        GL.backup_list = []
        dlg = wx.ProgressDialog(u"进程条",u"正在上传更新，请稍等...",maximum = fnum,style = 0
                                | wx.PD_APP_MODAL| wx.PD_CAN_ABORT| wx.PD_ESTIMATED_TIME| wx.PD_REMAINING_TIME|wx.PD_AUTO_HIDE)
        dlg.ShowModal()
        self.keepGoing = True
        for each_file in flist:
            #print self.keepGoing,count
            if self.keepGoing is False:
                break
            commands = []
            nowtime = time.strftime("%Y%m%d-%H%M%S", time.localtime())

            full_local_each_file = ''.join([LocalDir,each_file])
            full_remote_each_file = ''.join([RemoteDir,each_file])
            backup_file = "".join([BackupDir,each_file,'_bak_',nowtime])
            #print backup_file
            #print full_each_file
            predir = os.path.dirname(full_remote_each_file)
            #print predir
            cmd_testdir = "ssh -p %d %s 'test ! -d %s && mkdir -pv %s; \
                                   test ! -d %s && mkdir -pv %s'" \
                                   %(rport,rhost,predir,predir,os.path.dirname(backup_file),os.path.dirname(backup_file))
            cmd_backup = "ssh -p %d %s 'test -f %s && /bin/cp -a %s %s'" \
                         %(rport,rhost,full_remote_each_file,full_remote_each_file,backup_file)
            cmd_scp = "scp -P %d -r %s %s\:%s" %(rport,full_local_each_file,rhost,full_remote_each_file)
            cmd_chown = "ssh -p %d %s 'chown www.www %s'" %(rport,rhost,full_remote_each_file)

            #print full_local_each_file,rhost,full_remote_each_file

            commands.append(cmd_testdir)
            commands.append(cmd_backup)
            commands.append(cmd_scp)
            commands.append(cmd_chown)
            for each_cmd in commands:
                stdin, stdout, stderr = self.client.exec_command(each_cmd)
                exit_status = stdout.channel.recv_exit_status()
                message = stdout.readlines()
                error = stderr.readlines()
                if each_cmd == cmd_backup:
                    #print stdout.readlines()
                    if len(error)>0:
                        msg = u"备份文件 %s 失败，错误信息: %s" %(full_local_each_file,message)
                        LoadLog.LogMsg(GL.logger_BakLog.warning,msg)
                    else:
                        if exit_status != 0:
                            msg = u"原文件 %s 不存在,未备份." % each_file
                        else:
                            msg = u"文件已备份为: %s" % backup_file
                            GL.backup_list.append(backup_file)
                    LoadLog.LogMsg(GL.logger_BakLog.info,msg)
                if each_cmd == cmd_scp:
                    if len(error) > 0:
                        msg = u"更新文件 %s 失败，错误信息: %s" %(full_local_each_file,message)
                        gmsg = u"%s, 失败" % full_local_each_file
                        LoadLog.LogMsg(GL.logger_PubLog.warning,msg)
                        GL.PublishList.append(gmsg)
                    else:
                        msg = u"成功更新文件: %s" % full_local_each_file
                        gmsg = u"%s, 成功" % full_local_each_file
                        LoadLog.LogMsg(GL.logger_PubLog.info,msg)
                        GL.PublishList.append(gmsg)
            count += 1
            (self.keepGoing,skip) = dlg.Update(count)
        dlg.Destroy()
        if self.keepGoing is True:
            wx.MessageBox(u"完成文件的更新发布! 详细请查看日志.", u"完成确认", style=wx.OK|wx.ICON_INFORMATION)
        else:
            wx.MessageBox(u"已经中止更新!", u"信息", style=wx.OK|wx.ICON_INFORMATION)
                    #update_list.append(msg)
        # for each_msg in update_list:
        # LoadLog.LogMsg(GL.loggera.warning,each_msg)
        # LoadLog.LogMsg(GL.loggera.warning,"")
        # #
        # for each_msg in backup_list:
        # LoadLog.LogMsg(GL.loggerb.warning,each_msg)
        GL.logger_PubLog.info("")
        GL.logger_BakLog.info("")
        self.ShutdownUpload(GL.RIPaddr,GL.Monitor_Upload_File,GL.RPort)

    def rollback_cmd(self,flist,RemoteDir,BackupDir,rhost,rport=22):
        self.connect()
        self.OpenUpload(GL.RIPaddr,GL.MonitorDir,GL.Monitor_Upload_File,GL.RPort)
        GL.rollbacked_list = []
        count = 0
        fnum = len(flist)
        #update_list = []
        #GL.backup_list = []
        dlg = wx.ProgressDialog(u"进程条",u"正在上传更新，请稍等...",maximum = fnum,style = 0
                                | wx.PD_APP_MODAL| wx.PD_CAN_ABORT| wx.PD_ESTIMATED_TIME| wx.PD_REMAINING_TIME|wx.PD_AUTO_HIDE)
        dlg.ShowModal()
        self.keepGoing = True
        for each_file in flist:
            if '_bak_' not in each_file:
                continue
            #print each_file.split('_bak_')[0]
            #print each_file.split('_bak_')[0].split(BackupDir)[1]
            ori_each = "".join([RemoteDir,each_file.split('_bak_')[0].split(BackupDir)[1]])
            #print ori_each
            cmd_copy = "ssh -p %d  %s 'cp -a %s %s;chown -R www.www %s'" %(rport,rhost,each_file,ori_each,ori_each)
            stdin, stdout, stderr = self.client.exec_command(cmd_copy)
            message = stdout.readlines()
            error = stderr.readlines()
            if len(error)>0:
                msg = u"还原文件 %s 失败，错误信息: %s" %(each_file,message)
                gmsg = u"%s, 失败" %each_file
                LoadLog.LogMsg(GL.logger_PubLog.warning,msg)
                GL.rollbacked_list.append(gmsg)
            else:
                exit_status = stdout.channel.recv_exit_status()
                if exit_status != 0:
                    msg = u"还原文件发生错误，文件 %s 不存在，请检查。" % each_file
                    gmsg = u"%s, 失败" %each_file
                    LoadLog.LogMsg(GL.logger_PubLog.error,msg)
                    GL.rollbacked_list.append(gmsg)
                else:
                    msg = u"已还原文件 %s" %each_file
                    gmsg = u"%s, 成功" %each_file
                    LoadLog.LogMsg(GL.logger_PubLog.info,msg)
                    GL.rollbacked_list.append(gmsg)
            count += 1
            (self.keepGoing,skip) = dlg.Update(count)
        dlg.Destroy()
        if self.keepGoing is True:
            wx.MessageBox(u"列表中的文件已还原! 详细请查看日志.", u"完成确认", style=wx.OK|wx.ICON_INFORMATION)
        else:
            wx.MessageBox(u"还原中止更新!", u"信息", style=wx.OK|wx.ICON_INFORMATION)
        GL.logger_PubLog.info("")
        self.ShutdownUpload(GL.RIPaddr,GL.Monitor_Upload_File,GL.RPort)

    def close(self):
        self.client.close()
# def main():
# client = SSHConect(GL.SVN_HOST, GL.SVN_PORT,GL.SVN_USERNAME,GL.SVN_PASSWORD)
# #client.publish_cmd(flist,rhost)
# client.close()
#
# if __name__ == '__main__':
# main()