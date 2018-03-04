#coding:utf-8
import logging
import time

class LogConsoleHandler(logging.StreamHandler):
    def __init__(self, textctrl):
        logging.StreamHandler.__init__(self)
        self.textctrl = textctrl

    def emit(self, record):
        #msg = self.format(record)
        #self.textctrl.AppendText(msg + "\n")
        #print gen.MSG_MAX
        # if len(self.textctrl.GetValue()) > gen.MSG_MAX:
        # self.textctrl.SetValue('')
        #if GL.console_switch == True:
            #level = GL.LEVELS.get("error",logging.NOTSET)
            # if record.levelno < level:
            #     return
        tstr = time.strftime('%Y-%m-%d %H:%M:%S')
        #print record.levelname
        self.textctrl.AppendText("[%s]-[%s]: %s\n"%(tstr,record.levelname,record.getMessage()))
        self.flush()


def LogMsg(loglevel,msg):
    #if GL.logswitch is True:
    loglevel(msg)

# def DefineLog(self):
#
#     ahandlers = logging.handlers.RotatingFileHandler(GL.publish_logfile,maxBytes=GL.LOG_MAX_BYTES,backupCount=GL.BACKUP_COUNT,)
#     ahandlers.setFormatter(GL.formatter)
#     bhandlers = logging.handlers.RotatingFileHandler(GL.backup_logfile,maxBytes=GL.LOG_MAX_BYTES,backupCount=GL.BACKUP_COUNT,)
#     bhandlers.setFormatter(GL.formatter)
#     chandlers = logging.handlers.RotatingFileHandler(GL.gloabl_publish_logfile,maxBytes=GL.LOG_MAX_BYTES,backupCount=GL.BACKUP_COUNT,)
#     dhandlers = logging.handlers.RotatingFileHandler(GL.global_backup_logfile,maxBytes=GL.LOG_MAX_BYTES,backupCount=GL.BACKUP_COUNT,)
#     ehandlers = logging.handlers.RotatingFileHandler(GL.system_logfile,maxBytes=GL.LOG_MAX_BYTES,backupCount=GL.BACKUP_COUNT,)
#     ehandlers.setFormatter(GL.formatter)
#
#     GL.logger_PubLog.addHandler(ahandlers)
#     GL.logger_PubLog.setLevel(logging.INFO)
#
#     GL.logger_BakLog.addHandler(bhandlers)
#     GL.logger_BakLog.setLevel(logging.INFO)
#
#     GL.logger_gPubLog.addHandler(chandlers)
#     GL.logger_gPubLog.setLevel(logging.INFO)
#
#     GL.logger_gBakLog.addHandler(dhandlers)
#     GL.logger_gBakLog.setLevel(logging.INFO)
#
#     GL.logger_sysLog.addHandler(ehandlers)
#     GL.logger_sysLog.setLevel(logging.INFO)



