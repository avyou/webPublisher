#coding:utf-8

import os
import cPickle as pickle
import base64
from ConfigParser import SafeConfigParser

public_key = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCaGOAQ+XdZhbpOot5KAGS4Hfms
/ELpv8kgNazBEADUT/65Xq3BH4c9XwFnDnfLSiGf1Nbiw8V406OYzvugCmYdcs8T
qEpkquGdfT0QgTKf5SLtyOLI1bq2rkZmn1Vqs0MKes884RUy5eCZDH0WN2QY3fEM
oiiJVPhiKSnIgpnCRQIDAQAB
-----END PUBLIC KEY-----
"""
pass_private_key = """
-----BEGIN RSA PRIVATE KEY-----
MIICXAIBAAKBgQCrE1yvqcwvqL1hWPHzA6PnMBvqKvUXuzw6LyHrYRT7A7+Y4fft
ef5Q+F0sRQZ2p2Q2q76IhdxL6zGx0crLPyAseNsd/KuKR+AlYaE9nBUHGCnT7BPs
wk0yMFAlY4iGf9rH+rB+lNI0qDyY5gVJRs/qDJBP3UodY0FR3XsqmZPkGwIDAQAB
AoGADnt5ITXSn0Y9ofwRn2zzdyLPeidg0D19f791s6NoT0el9J9MicIGEXy1BoZh
YbIR/b7URmJun86tSkxkSohxhK7XzAZ5HszOODN3AA3Jp1nFbwSQfH6RO1igBfHc
rD0FU9m5oFpqimwv8nekVXwkuaIqP0lhugcx4AszcspzykECQQDRSItNh103BZkq
hU683ZkBKIeknvTBhhqozkn7RNp9SEh2Kj705iOQxVItmDZfHP5DSkMdRhsoy7UC
YJQ//loZAkEA0UNxucsncJlZAumRQhFbGweJduofXD7KSv8/LFexeBJdma6S3UAx
RAXTwGr914oMgapjszvGwQQi/UXenTPeUwJAEfdCTiOCswh9/5J2EeyMB/dsvYsP
w9U5UKh03WcpwnuEDPDPesKO5wypY1SfxkZ85VXosQilqDjkjxGvaFbzcQJAEjkI
T0CUp6aC7NEAGDvArkLiwpsyreq93PgLPUZJqwYWZoqgOWocoCrNvMTUZA+edTAs
THBZJ3e/wER0VUYuBwJBANANUT2wRCEOlyCIiFxigU1DrWOW68+y2q7iJ1QJS9nf
xMSFMucvpKk3I+rsP+DhVtV3Iqqyi3XZgqH2diFhg7A=
-----END RSA PRIVATE KEY-----
"""

pass_public_key = """
-----BEGIN PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCrE1yvqcwvqL1hWPHzA6PnMBvq
KvUXuzw6LyHrYRT7A7+Y4fftef5Q+F0sRQZ2p2Q2q76IhdxL6zGx0crLPyAseNsd
/KuKR+AlYaE9nBUHGCnT7BPswk0yMFAlY4iGf9rH+rB+lNI0qDyY5gVJRs/qDJBP
3UodY0FR3XsqmZPkGwIDAQAB
-----END PUBLIC KEY-----
"""
str_key = "123456-TEST"

def SaveSSHAuthToFile(sshAuthDict,AuthFile,enkey,private_key):
    from passEncrypt import GetKey,EncodeAES,EncryptCode
    cipher = GetKey(enkey)
    for each_key in sshAuthDict:
        encoded = EncodeAES(cipher,sshAuthDict[each_key],32)
        sshAuthDict[each_key] = EncryptCode(encoded,private_key)

    with open(AuthFile,"wb") as f:
        pickle.dump(base64.b64encode(str(sshAuthDict)),f)


if __name__ == "__main__":
    #import globalDef as GL
    #if not os.path.exists(GL.ConfFile):
    #UpdateSectionDict(GL.ConfFile,sections,"Auth","password","123456")
    #SaveConf(GL.ConfFile,GL.DefaultConfDict)
    #a = ReadAllConf(GL.ConfFile,GL.sections)
    #print type(a)
    SaveSSHAuthToFile({"password":"sVduNZnWWC$9"},"AuthFile.db",str_key,pass_private_key)