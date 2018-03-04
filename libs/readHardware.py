#coding:utf-8
import wx
import wmi,zlib
from M2Crypto import RSA, BIO
from base64 import b64decode,b64encode

def get_disk_info(define_str):
    encrypt_define_str = encrypt_str(define_str)
    c = wmi.WMI ()
    for cpu in c.Win32_Processor():
        encrypt_define_str = encrypt_define_str + cpu.ProcessorId.strip()

    try:
        #for physical_disk in c.Win32_DiskDrive():
            #encrypt_define_str = encrypt_define_str + physical_disk.SerialNumber.strip()
        for board_id in c.Win32_BaseBoard():
            encrypt_define_str = encrypt_define_str + board_id.SerialNumber.strip()
    except:
        #wx.MessageBox(u"无法获取机器码，请检测是否有移动设备.",u"错误", style=wx.ICON_ERROR)
        GenMachineCode = None
        return GenMachineCode

    GenMachineCode = zlib.adler32(encrypt_define_str)
    print GenMachineCode
    return GenMachineCode

def encrypt_str(str_key):
    crypt_strkey = b64encode(str_key)
    return crypt_strkey

def DencryptForRegCode(regCode,public_key):
    pub_bio = BIO.MemoryBuffer(public_key)
    rsa = RSA.load_pub_key_bio(pub_bio)
    #pub_key = EVP.load_key_string(public)
    try:
        machine_code = rsa.public_decrypt(b64decode(regCode),RSA.pkcs1_padding)
    except:
        machine_code = ""
    return machine_code

def VerifyReturnValue():
    from globalDef import public_key,str_key
    demachine = str(DencryptForRegCode(reg_code,public_key))
    machineCode = str(get_disk_info(str_key)).lstrip("-")
    if demachine == machineCode:
        active = True
    else:
        active = False
    return active
if __name__ == "__main__":
    import globalDef as GL
    reg_code = """
G1OcPbLbj+3KsF22ScN8XuB/PVmQpE+elI8Q9ElWj/5rncYkG1aZYwj5DeHAG8ieSbuMlRhwcW6P
15MEIKpRvIXh5p/kmgHlEj1jwNet7b5HV1oxHzup9KE8czQkIXTeZ4MjeXSnDDEb4UdGknkkb+Mg
9+eytlYHAcwFDT8uMi8=
"""
    print GL.Active
    verify_value = VerifyReturnValue()
    #print verify_value
    GL.Active = verify_value
    print GL.Active
