#coding:utf-8
import wx
import cPickle as pickle
import readHardware
import globalDef as GL

class RegisterUI(wx.Dialog):
    def __init__(self,size,machineCode,rCode,public_key):
        self.machineCode = machineCode
        self.rCode = rCode
        self.public_key = public_key
        title_info = self.TitleInfo(GL.Active)
        wx.Dialog.__init__(self, None, -1,title_info, size=size)

        font = wx.Font(12, wx.MODERN, wx.NORMAL, wx.BOLD, False, u'Consolas')
        text_information = wx.StaticText(self,label=u"软件注册")
        text_information.SetFont(font)

        #img=wx.Image("Img\prestart.png")
        #img.Rescale(70,70)
        #image = wx.BitmapFromImage(img)
        #icon = wx.StaticBitmap(self, bitmap=image)
        line = wx.StaticLine(self)

        text_Mname = wx.StaticText(self,label=u"机器码:")
        text_Rname = wx.StaticText(self,label=u"注册码:")

        self.tc_mCode = tc_mCode= wx.TextCtrl(self,style=wx.CB_READONLY)
        tc_mCode.SetValue(self.machineCode)

        self.tc_rCode = tc_rCode = wx.TextCtrl(self,size=(400,200),style=wx.MULTIPLE,id=GL.RegCodeTextID)
        self.tc_rCode.SetValue(self.rCode)

        self.regBtn = regBtn = wx.Button(self,label=u"注册",id=GL.RegisterID)
        if GL.Active is True:
            self.regBtn.Disable()
        #regBtn.Disable()
        cancelBtn = wx.Button(self,label=u"取消",id = GL.Register_Cancel_ID)

        sizer = wx.GridBagSizer(4,5)
        sizer.Add(text_information,pos=(0,0),span=(1,3),flag=wx.TOP|wx.LEFT|wx.BOTTOM, border=10)
        #sizer.Add(icon,pos=(0,4),flag=wx.ALIGN_RIGHT|wx.LEFT)
        sizer.Add(line, pos=(1,0), span=(1,5), flag=wx.EXPAND, border=10)

        sizer.Add(text_Mname,pos=(2,0),span=(1,1),flag=wx.ALIGN_RIGHT|wx.TOP|wx.LEFT, border=10)
        sizer.Add(text_Rname,pos=(3,0),span=(1,1),flag=wx.ALIGN_RIGHT|wx.TOP|wx.LEFT, border=10)

        sizer.Add(tc_mCode,pos=(2,1),span=(1,4),flag=wx.TOP|wx.RIGHT|wx.EXPAND, border=10)
        sizer.Add(tc_rCode,pos=(3,1),span=(1,4),flag=wx.EXPAND|wx.RIGHT|wx.TOP, border=10)

        bsizer = wx.BoxSizer(wx.HORIZONTAL)
        bsizer.Add(regBtn,0,wx.ALL,5)
        bsizer.Add(cancelBtn,0,wx.ALL,5)
        #sizer.Add(button_save,pos=(4,3),span=(1,1),flag=wx.ALIGN_RIGHT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=10)
        sizer.Add(bsizer,pos=(4,4),span=(1,1),flag=wx.ALIGN_RIGHT|wx.RIGHT|wx.TOP|wx.BOTTOM, border=10)
        sizer.AddGrowableCol(2)
        sizer.AddGrowableCol(1)
        sizer.AddGrowableCol(3)
        self.SetSizerAndFit(sizer)
        sizer.SetSizeHints(self)

        self.Bind(wx.EVT_BUTTON,self.OnRegister,id=GL.RegisterID)
        self.Bind(wx.EVT_BUTTON,self.OnCancel,id=GL.Register_Cancel_ID)
        self.Bind(wx.EVT_TEXT,self.OnRegCodeText,id=GL.RegCodeTextID)

    def OnRegister(self,event):
        if self.tc_rCode.IsEmpty():
            wx.MessageBox(u"注册码不能为空",u"错误",style=wx.ICON_ERROR)
        else:
            self.rCode = self.tc_rCode.GetValue()
            print self.rCode
            DeMachine = str(readHardware.DencryptForRegCode(self.rCode,self.public_key))
            print DeMachine

            try:
                with open(GL.RegisterFile,"wb") as f:
                    pickle.dump(self.rCode,f,-1)
            except:
                wx.MessageBox(u"写入注册信息失败,请查看文件权限.",u"错误",style=wx.ICON_ERROR)
                return

            if self.machineCode == DeMachine:
                GL.Active = True
                wx.MessageBox(u"注册成功",u"信息",style=wx.ICON_INFORMATION)
                self.regBtn.Disable()
            else:
                GL.Active = False
                wx.MessageBox(u"无效注册码,注册失败.",u"信息",style=wx.ICON_INFORMATION)

            title_info = self.TitleInfo(GL.Active)
            self.SetTitle(title_info)

    def OnCancel(self,event):
        self.Destroy()

    def OnRegCodeText(self,event):
        self.regBtn.Enable()

    def TitleInfo(self,IsActive):
        if IsActive is True:
            title_info = u"License" + u" 已注册"
        else:
            title_info = u"License" + u" 未注册"
        return title_info

if __name__ == '__main__':
    try:
        with open(GL.RegisterFile,"rb",-1) as f:
            rCode = pickle.load(f)
    except:
        rCode = ""
    machineCode = str(readHardware.get_disk_info(GL.str_key)).lstrip("-")
    if len(rCode) != 0:
        deMachineCode = str(readHardware.DencryptForRegCode(rCode,GL.public_key))
        if deMachineCode == machineCode:
            GL.Active = True
        else:
            GL.Active = False

    app = wx.App()
    app.MainLoop()
    dialog = RegisterUI((500,400),machineCode,rCode,GL.public_key)
    dialog.ShowModal()
    #dialog.Destroy()