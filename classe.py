import discord,time
from datetime import datetime
from threading import Thread
bot = discord.Client()

# Log class to log all error or some information
async def Log(msg,type,bot,info=None):
    today = datetime.today().strftime("%d/%m/%Y %H:%M:%S")
    if type != None :
        if info != None:
            await bot.get_channel(582307485239476224).send(today+" | "+str(msg)+str(info)[-300:])
        else:
            await bot.get_channel(582307485239476224).send(today+" | "+str(msg))
    with open('log.txt','a') as log_file:
        log_file.write(today+"\n"+str(msg)+"\n&&&&&\n")
# Basic class command to a better use
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

# Class vote
class Vote(Thread):
    def __init__(self,id,msg,time):
        """
            Use to initiate the variable
        """
        Thread.__init__(self)
        self.question = ""
        self.response = []
        self.react = ['0⃣','1⃣','2⃣','3⃣','4⃣','5⃣','6⃣','7⃣','8⃣','9⃣']
        self.message = msg
        self.id = id
        self.time = time
    def setQ(self,question):
        """
            Use to set a question
        """
        for i in question:
            self.question += i+" "
    def setR(self,response):
        """
            Use to set a question
        """
        if len(self.response) <= 10:
            text = ""
            for i in response:
                text += i+" "
            self.response.append(text)
    async def prepare(self):
        """
            Use to update the vote before launching it
        """
        embed = discord.Embed(
                        title="Vote !",
                        colour=0x7C08F5
                             )
        embed.add_field(name=self.question,value="-"*len(self.question),inline=False)
        for i in range(len(self.response)):
            embed.add_field(name=self.response[i]+" => "+self.react[i],value="#"*len(self.response[i]),inline=False)
            await self.message.add_reaction(self.react[i])
        await self.message.edit(embed=embed,content="")
    def run(self):
        """
            Use to start the vote
        """
        start = time.time()
        while time.time()-start < self.time*10:
            pass
    async def end(self):
        """
            Use to close the vote and print result
        """
        total = 0
        count = []
        test = dict()
        msg = await self.message.channel.fetch_message(self.id)
        user = []
        for i in msg.reactions:
            async for j in i.users():
                if j.bot:
                    pass
                elif j.id not in user:
                    user.append(j.id)
                else:
                    await i.remove(j)
        msg = await self.message.channel.fetch_message(self.id)
        for i in msg.reactions:
            count.append(int(i.count)-1)
            total += int(i.count)-1
        print(len(count))
        embed = discord.Embed(title = "Resultat     -      "+self.question,colour=0x7C08F5)
        for i in range(len(self.response)):
            embed.add_field(name=self.response[i],value="0" if total == 0 else str("%.2f"%((count[i]/total)*100)+"%"))
        await self.message.channel.send(embed=embed)
