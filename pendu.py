class Pendu:
    def __init__(self,id):
        self.lvl0 = ""
        self.lvl1 = "___ _____ ___ ______ ____"
        self.lvl2 = "    |\n    |\n    |\n    |\n___ _____ ___ __"
        self.lvl3 = "----------------\n    |\n    |\n    |\n    |\n___ _____ ___ ______ ____"
        self.lvl4 = "----------------\n    |      |\n    |      |\n    |\n    |\n    |\n    |\n___ _____ ___ ______ ____"
        self.lvl5 = "----------------\n    |      |\n    |      |\n    |      0\n    |\n    |\n    |\n___ _____ ___ ______ ____"
        self.lvl6 = "----------------\n    |      |\n    |      |\n    |      0\n    |      |\n    |\n    |\n___ _____ ___ ______ ____"
        self.lvl7 = "----------------\n    |      |\n    |      |\n    |      0\n    |     -|\n    |\n    |\n___ _____ ___ ______ ____"
        self.lvl8 = "----------------\n    |      |\n    |      |\n    |      0\n    |     -|-\n    |\n    |\n___ _____ ___ ______ ____"
        self.lvl9 = "----------------\n    |      |\n    |      |\n    |      0\n    |     -|-\n    |     /\n    |\n___ _____ ___ ______ ____"
        self.lvl10 = "----------------\n    |      |\n    |      |\n    |      0\n    |     -|-\n    |     /\\\n    |\n___ _____ ___ ______ ____"
        self.Pendu_inGame = False
        self.Pendu_GamePlayer = id
        self.mots = ""
        self.devinemot = ""
        self.currentLvl = self.lvl0
        self.lettersaid = ""
        self.Pendu_gameMessage = ""
        self.Pendu_gameServer = ""
        self.init()
    def stop(self):
        self.Pendu_inGame = false
        self.Pendu_GamePlayer = 0
        self.mots = ""
        self.devinemot = ""
        self.currentLvl = self.lvl0
        self.lettersaid = ""
        self.Pendu_gameMessage
        self.Pendu_gameServer = ""
    def init(self):
        self.mots = open('pendu.txt','r').read().split('\n')[:-1]
        self.mots = self.mots[random.randrange(0,len(self.mots),1)]
        for i in range(len(self.mots)):
            self.devine += "@"
    def prepare(self):
        embed = discord.Embed()
        embed.add_field(name="Pendu",value=self.devinemot)
        embed.add_field(name=self.currentLvl,value=self.lettersaid)
        return embed

    async def start(self,message,id):
        if id != self.Pendu_GamePlayer or message.channel.id != self.Pendu_gameServer:
            return
