import datetime


class Debug:
    def __init__(self,_config):
        self.config = _config
        self.type = _config.get('Debug','type')
        if type == "File":
            self.f = open(_config.get('Debug','file'), 'w')

    def write(self,message):
        if not self.config.getboolean('Debug','debug'):
            return True
        if type == "File":
            self.f.write("%s: %s"%(datetime.now(),message))
        else:
            print (message)
 

