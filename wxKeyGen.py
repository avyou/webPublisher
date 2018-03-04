#coding:utf-8
import wx
from M2Crypto import RSA, BIO
from M2Crypto import EVP
from base64 import b64decode
private_key = """
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCaGOAQ+XdZhbpOot5KAGS4Hfms/ELpv8kgNazBEADUT/65Xq3B
H4c9XwFnDnfLSiGf1Nbiw8V406OYzvugCmYdcs8TqEpkquGdfT0QgTKf5SLtyOLI
1bq2rkZmn1Vqs0MKes884RUy5eCZDH0WN2QY3fEMoiiJVPhiKSnIgpnCRQIDAQAB
AoGBAIEeitFuVwUaOowdiGk1fy+PXmAGWAMJAnwMvZ5fzHIaPXQR00HZKzbPXpt9
0f7zNM16SDxmkha2L4ShGtJ1JC4HzxW1W8qxPR071qL/mncaZvHbAlj48x4e5NFi
RpF7Y0CRJqPX6JvoDTFdNtrHmyHWASadPOQK4hzH0BGmAIEZAkEAyzcrnE0GVXOV
scU4xx0U5TgrVAYqshHRcGtFU4QAAwqyCQgqcxM0lSFpyVdoaYgPNnQCSo3CbHKT
PlWV2xZ7ewJBAMIfk9CSgnoN2GOJrMpPUYZHu+lXaRmnsA8yKkw4G9j9NKYknv2l
aQWQn/vKyFGJwkkcEkP4pEf/EGz+IQEabT8CQCvnZH2lSnwFt86rbGPgTZZkN0A1
AN5t6RDfrB+qAhKmKea3o+wutwqNKHy+bKl4IslB8QjIbbveWR97gB/QUKcCQHyP
ToWSvO4cXDDicmEOLD2BYe4EDIhNtQbLJaDqj9PYBSRmcy5GKPFNL5qdL5RCVMwc
mwvKS393Bs8o8XyHvHkCQHnrdejnQtKvFa/8KTol8gELTcPcWKDIMpTUIUHE8FGo
Qgtw3HVrShWg2x3xqLkT8h3QxRUt4HVRpnL2WBL5YG8=
-----END RSA PRIVATE KEY-----
"""
public_key = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCaGOAQ+XdZhbpOot5KAGS4Hfms
/ELpv8kgNazBEADUT/65Xq3BH4c9XwFnDnfLSiGf1Nbiw8V406OYzvugCmYdcs8T
qEpkquGdfT0QgTKf5SLtyOLI1bq2rkZmn1Vqs0MKes884RUy5eCZDH0WN2QY3fEM
oiiJVPhiKSnIgpnCRQIDAQAB
-----END PUBLIC KEY-----
"""
class KeyGenFrame(wx.Frame):
    def __init__(self,title,size):
        wx.Frame.__init__(self,None, -1, title=title, size=size,style=wx.CAPTION |wx.CLOSE_BOX)
        panel = wx.Panel(self,-1)
        self.mcodeLabel = mcodeLabel = wx.StaticText(panel, -1, u"机器码:")
        self.mcodeText = mcodeText = wx.TextCtrl(panel, -1, "", size=(300,30))
        genBtn = wx.Button(panel, label=u"生成", pos=(50,20),id=wx.NewId())
        genLabel = wx.StaticText(panel, -1, u"注册码:")
        self.genCodeText = genCodeText = wx.TextCtrl(panel, -1, "", size=(300,150),style=wx.TE_READONLY|
                                                                                         wx.MULTIPLE|wx.TE_WORDWRAP)
        self.genCodeText.SetBackgroundColour("pick")
        #genCode.SetValue("aaaaaaaaaaaaaaaa")
        cpBtn = wx.Button(panel, label=u"复制", pos=(50,20),id=wx.NewId())
        vsizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(mcodeLabel,0,wx.ALL,5)
        hsizer.Add(mcodeText,0,wx.ALL,5)
        hsizer.Add(genBtn,0,wx.ALL,5)
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.Add(genLabel,0,wx.ALL,5)
        hsizer2.Add(genCodeText,0,wx.ALL,5)
        hsizer2.Add(cpBtn,0,wx.ALL,5)
        vsizer.Add(hsizer,0,wx.TOP,20)
        vsizer.Add(hsizer2,0,wx.BOTTOM,5)
        panel.SetSizerAndFit(vsizer)
        self.Bind(wx.EVT_BUTTON,self.OnGenerateBtn,genBtn)
        self.Bind(wx.EVT_BUTTON,self.OnCopyBtn,cpBtn)
    def OnGenerateBtn(self,event):
        if self.mcodeText.IsEmpty():
            wx.MessageBox(u"机器码内容不能为空.", "Error",style=wx.ICON_ERROR)
            return
        machine_code = str(self.mcodeText.GetValue())
        print self.genEncryptCode(machine_code,private_key)
        reg_code = self.genEncryptCode(machine_code,private_key)
        self.genCodeText.SetValue(reg_code)
    def OnCopyBtn(self,event):
        regCode = self.genCodeText.GetValue()
        dataObj = wx.TextDataObject()
        dataObj.SetText(regCode)
        try:
            with wx.Clipboard.Get() as clipboard:
                clipboard.SetData(dataObj)
        except TypeError:
            wx.MessageBox(u"复制出错", "Error")
            return
    def genEncryptCode(self,machine_code,private_key):
        priv_bio = BIO.MemoryBuffer(private_key)
        rsa = RSA.load_key_bio(priv_bio)
        priv_key = EVP.load_key_string(private_key)
        encrypted = rsa.private_encrypt(machine_code, RSA.pkcs1_padding)
        regCode = encrypted.encode('base64')
        return regCode
    def dencrypt(self,regCode,public_key):
        pub_bio = BIO.MemoryBuffer(public_key)
        rsa = RSA.load_pub_key_bio(pub_bio)
        #pub_key = EVP.load_key_string(public)
        machine_code = rsa.public_decrypt(b64decode(regCode),RSA.pkcs1_padding)
        return machine_code
if __name__ == "__main__":
    app = wx.App()
    frame = KeyGenFrame(u"web Publisher 注册机",(450,200))
    frame.Center()
    frame.Show()
    app.MainLoop()