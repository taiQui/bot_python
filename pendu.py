import discord,random
class Pendu:
    def __init__(self,message):
        """
            Init Hangman game (pendu)
        """
        self.lvl0 = ""
        self.lvl1 = "___ _____ ___ ______ ____"
        self.lvl2 = "    |\n    |\n    |\n    |\n___ _____ ___ __"
        self.lvl3 = "\n----------------\n    |\n    |\n    |\n    |\n___ _____ ___ ______ ____"
        self.lvl4 = "\n----------------\n    |      |\n    |      |\n    |\n    |\n    |\n    |\n___ _____ ___ ______ ____"
        self.lvl5 = "\n----------------\n    |      |\n    |      |\n    |      0\n    |\n    |\n    |\n___ _____ ___ ______ ____"
        self.lvl6 = "\n----------------\n    |      |\n    |      |\n    |      0\n    |      |\n    |\n    |\n___ _____ ___ ______ ____"
        self.lvl7 = "\n----------------\n    |      |\n    |      |\n    |      0\n    |     -|\n    |\n    |\n___ _____ ___ ______ ____"
        self.lvl8 = "\n----------------\n    |      |\n    |      |\n    |      0\n    |     -|-\n    |\n    |\n___ _____ ___ ______ ____"
        self.lvl9 = "\n----------------\n    |      |\n    |      |\n    |      0\n    |     -|-\n    |     /\n    |\n___ _____ ___ ______ ____"
        self.lvl10 = "\n----------------\n    |      |\n    |      |\n    |      0\n    |     -|-\n    |     /\\\n    |\n___ _____ ___ ______ ____"
        self.Pendu_inGame = True
        self.Pendu_GamePlayer = message.author.id
        self.mots = ""
        self.devinemot = ""
        self.currentLvl = self.lvl0
        self.lettersaid = ""
        self.Pendu_gameMessage = ""
        self.Pendu_gameServer = message.channel.id

    def stop(self):
        """
            Game is stopped
        """
        self.Pendu_inGame = False
        self.Pendu_GamePlayer = 0
        self.mots = ""
        self.devinemot = ""
        self.currentLvl = self.lvl0
        self.lettersaid = ""
        self.Pendu_gameMessage
        self.Pendu_gameServer = ""
    async def init(self,message):
        """
            Init the game with new word and reinit all variable
        """
        self.mots = open('pendu.txt','r').read().split('\n')[:-1]
        self.mots = self.mots[random.randrange(0,len(self.mots),1)]
        for i in range(len(self.mots)):
            self.devinemot += "@"
        await message.channel.send("Welcome to the Pendu Game !")
        self.Pendu_gameMessage = message.channel.last_message
        if self.Pendu_gameMessage.author.id == self.Pendu_GamePlayer:
            while self.Pendu_gameMessage.author.id == self.Pendu_GamePlayer:
                self.Pendu_gameMessage = message.channel.last_message
        embed = discord.Embed()
        embed.add_field(name="Pendu",value=self.devinemot+"\n\n"+self.currentLvl+"\n\n"+self.lettersaid)
        await self.Pendu_gameMessage.edit(embed=embed)
        print("word : "+self.mots)

    async def start(self,message,content,id):
        """
            Start the game
        """
        if id != self.Pendu_GamePlayer or message.channel.id != self.Pendu_gameServer:
            return
        letter = content
        # if letter in words to find
        if len(letter) > 1:
            if letter == self.mots:
                self.devinemot = self.mots
                embed = discord.Embed()
                embed.add_field(name="Pendu",value=self.devinemot+"\n\n"+self.currentLvl+"\n\n"+self.lettersaid+"\n\n Gg ! ")
                await self.Pendu_gameMessage.edit(embed=embed)
                self.stop()
            else:
                self.change_level()
                self.lettersaid += letter +" "
                embed = discord.Embed()
                embed.add_field(name="Pendu",value=self.devinemot+"\n\n"+self.currentLvl+"\n\n"+self.lettersaid)
                await self.Pendu_gameMessage.edit(embed=embed)
        # if the letter is in the word and not already said
        elif letter in self.mots and letter not in self.devinemot:
            for i in range(len(self.mots)):
                if self.mots[i] == letter:
                    self.devinemot = self.devinemot[0:i] + letter + self.devinemot[i+1:]
            self.lettersaid += letter + " "
            embed = discord.Embed()
            embed.add_field(name="Pendu",value=self.devinemot+"\n\n"+self.currentLvl+"\n\n"+self.lettersaid)
            await self.Pendu_gameMessage.edit(embed=embed)
        # If the letter isn't in the word and not already said
        elif letter not in self.mots and letter not in self.lettersaid:
            self.change_level()
            self.lettersaid += letter +" "
            if self.currentLvl == self.lvl10:
                embed = discord.Embed()
                embed.add_field(name="Pendu",value=self.devinemot+"\n\n"+self.currentLvl+"\n\n"+self.lettersaid+"\n\n"+"LOSE ! \nThe word was : " + self.mots)
                await self.Pendu_gameMessage.edit(embed=embed)
                self.Pendu_inGame = False
                return
            embed = discord.Embed()
            embed.add_field(name="Pendu",value=self.devinemot+"\n\n"+self.currentLvl+"\n\n"+self.lettersaid+"\n\n"+"NOP")
            await self.Pendu_gameMessage.edit(embed=embed)
        # If the letter is already said
        elif letter in self.lettersaid:
            embed = discord.Embed()
            embed.add_field(name="Pendu",value=self.devinemot+"\n\n"+self.currentLvl+"\n\n"+self.lettersaid+"\n\n"+"You already said this letter")
            await self.Pendu_gameMessage.edit(embed=embed)
        if self.devinemot == self.mots:
            await message.channel.send("You find the right word !  :ok_hand: ")
            self.stop()
        await message.delete()
    def change_level(self):
        """
            Change the state of the hang man
        """
        if self.currentLvl == self.lvl0:
            self.currentLvl = self.lvl1
        elif self.currentLvl == self.lvl1:
            self.currentLvl = self.lvl2
        elif self.currentLvl == self.lvl2:
            self.currentLvl = self.lvl3
        elif self.currentLvl == self.lvl3:
            self.currentLvl = self.lvl4
        elif self.currentLvl == self.lvl4:
            self.currentLvl = self.lvl5
        elif self.currentLvl == self.lvl5:
            self.currentLvl = self.lvl6
        elif self.currentLvl == self.lvl6:
            self.currentLvl = self.lvl7
        elif self.currentLvl == self.lvl7:
            self.currentLvl = self.lvl8
        elif self.currentLvl == self.lvl8:
            self.currentLvl = self.lvl9
        elif self.currentLvl == self.lvl9:
            self.currentLvl = self.lvl10
