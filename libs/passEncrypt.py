#coding:utf-8
# import bz2
import base64
from Crypto.Cipher import AES
from M2Crypto import RSA, BIO
from M2Crypto import EVP
from base64 import b64decode


##字符串使用私钥加密
def EncryptCode(string,private_key):
    priv_bio = BIO.MemoryBuffer(private_key)
    rsa = RSA.load_key_bio(priv_bio)
    priv_key = EVP.load_key_string(private_key)
    encrypted = rsa.private_encrypt(string, RSA.pkcs1_padding)
    enstring = encrypted.encode('base64')
    return enstring

##字符串使用公钥解密
def Dencrypt(string,public_key):
    pub_bio = BIO.MemoryBuffer(public_key)
    rsa = RSA.load_pub_key_bio(pub_bio)
        #pub_key = EVP.load_key_string(public)
    destring = rsa.public_decrypt(b64decode(string),RSA.pkcs1_padding)
    return destring

##普通字符串加密
def EncodeAES(key, DefineString,BLOCK_SIZE):
    if len(DefineString) == 0:
        return DefineString
    PADDING = '{'
    pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
    EnString = base64.b64encode(key.encrypt(pad(DefineString)))
    return EnString
##普通字符解密
def DecodeAES(key, EncryptString,BLOCK_SIZE):
    #print EncryptString
    PADDING = '{'
    try:
        DeString = key.decrypt(base64.b64decode(EncryptString)).rstrip(PADDING)
    except:
        #print u"未解密"
        DeString = EncryptString
    return DeString

##设定key的处理
def GetKey(defineKey):
    count = len(defineKey)
    if count < 16:
        add = (16-count)
        defineKey = defineKey + ('\0' * add)
    elif 16 <count <32:
        add = (16-(count % 16))
        defineKey = defineKey + ('\0' * add)
    elif count > 32:
        defineKey = defineKey[0:32]
    cipher = AES.new(defineKey)
    return cipher

if __name__ == "__main__":
    import globalDef as GL
    PasswordStr = "root"
    cipher = GetKey(GL.str_key)
    encoded = EncodeAES(cipher, PasswordStr,32)
    print 'Encrypted string: %s' % encoded
    encoded_second =  EncryptCode(encoded,GL.pass_private_key)
    print encoded_second
    decoded_first =  Dencrypt(encoded_second,GL.pass_public_key)
    decoded = DecodeAES(cipher, decoded_first,32)
    print decoded_first
    print 'Decrypted string: %s' % decoded