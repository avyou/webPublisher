#coding:utf-8

import os
import cPickle as pickle
import base64
from ConfigParser import SafeConfigParser


class SafeConfigParser(SafeConfigParser):
    def optionxform(self, option):
        return option

def SaveConf(configfile,confdict):
    scp = SafeConfigParser()
    with open(configfile,'w') as f:
        for section in confdict:
            #print section
            scp.add_section(section)
            for key in confdict[section]:
                #print key, confdict[section][key]
                scp.set(section,key,confdict[section][key])
        scp.write(f)

def UpdateSectionDict(configfile,DefaultConfDict,sections,section,key,value):
    if not os.path.exists(configfile):
        confDict = DefaultConfDict
    else:
        confDict = ReadAllConf(configfile,sections,DefaultConfDict)
        #print confdict
    confDict[section][key] = value
    #print confDict
    SaveConf(configfile,confDict)

def ReadAllConf(configfile,sections,DefaultConfDict=None):
    confDict = {}
    scp = SafeConfigParser()
    with open(configfile,'r') as f:
        f.seek(0)
        try:
            scp.readfp(f)
        except:
            confDict = {}
        else:
            for section in scp.sections():
                optionDict = {}
                options = scp.options(section)
                #print options
                for key in options:
                    #print key,scp.get(section,key)
                    try:
                        value = scp.get(section,key)
                    except:
                        value = ""
                    optionDict[key] = value
                    confDict[section] = optionDict
    if len(confDict) == 0:
        confDict = DefaultConfDict
    return confDict

def ReadConf(configfile,section,key):
    scp = SafeConfigParser()
    with open(configfile,'r') as f:
        f.seek(0)
        scp.readfp(f)
        value = scp.get(section,key)
    return value

def ReadSSHAuthFile(AuthFile,enkey,public_key,pass_fild):
    try:
        with open(AuthFile,"rb",-1) as f:
            sshAuthDict = pickle.load(f)
    except:
        sshAuthDict = {pass_fild:""}
    else:
        from passEncrypt import GetKey,DecodeAES,Dencrypt
        try:
            sshAuthDict = eval(base64.b64decode(sshAuthDict))
        except:
            sshAuthDict = {pass_fild:""}
        else:
            if type(sshAuthDict) == dict and sshAuthDict.has_key(pass_fild):
                cipher = GetKey(enkey)
                decoded = Dencrypt(sshAuthDict[pass_fild],public_key)
                sshAuthDict[pass_fild] = DecodeAES(cipher, decoded,32)
            else:
                sshAuthDict = {pass_fild:""}
    return  sshAuthDict

def SaveSSHAuthToFile(sshAuthDict,AuthFile,enkey,private_key):
    from passEncrypt import GetKey,EncodeAES,EncryptCode
    cipher = GetKey(enkey)
    for each_key in sshAuthDict:
        encoded = EncodeAES(cipher,sshAuthDict[each_key],32)
        sshAuthDict[each_key] = EncryptCode(encoded,private_key)

    with open(AuthFile,"wb") as f:
        pickle.dump(base64.b64encode(str(sshAuthDict)),f)


if __name__ == "__main__":
    import globalDef as GL
    #if not os.path.exists(GL.ConfFile):
    #UpdateSectionDict(GL.ConfFile,sections,"Auth","password","123456")
    #SaveConf(GL.ConfFile,GL.DefaultConfDict)
    #a = ReadAllConf(GL.ConfFile,GL.sections)
    #print type(a)
    SaveSSHAuthToFile({"password":"svn229develop#"},GL.AuthFile,GL.str_key,GL.pass_private_key)

    #print GL.SvnUrl
    #print ReadSSHAuthFile(GL.AuthFile,GL.str_key,GL.pass_public_key,"password")