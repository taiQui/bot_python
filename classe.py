class Commande:
    def __init__(self,command):
        # Full command
        self.fc = command[1:].split(' ')
        # Command
        self.cmd = self.fc[0]
        # Args of command
        if len(self.fc) > 1:
            self.args = self.fc[1:]
        else:
            self.args = []
    def size(self,arg = -1):
        if arg == -1 :
            return len(self.args)
