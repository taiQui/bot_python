import discord
from classe import Commande
from datetime import date
from edt import Time_Schedule
from constant import *
from threading import Thread
import puissance4,pendu
import random,asyncio,requests,re,json,time
from cleverbot import async_ as cleverbot

"""
Author : taiQui
Description : Bot discord
"""

bot = discord.Client()

"""
Global variable
"""
ID = json.load(open('.token','r'))
edt1 = Time_Schedule(ID['M1-FI']['username'],ID['M1-FI']['password'],1)
edt2 = Time_Schedule(ID['M2-FI']['username'],ID['M2-FI']['password'],2)
# edt3 = Time_Schedule(USERNAME,PASSWORD,3)
edt4 = Time_Schedule(ID['M2-FA']['username'],ID['M2-FA']['password'],4)

P4 = None
PD = None
#####################
@bot.event
async def on_ready():
    print('Connexion')
    await bot.change_presence(activity=discord.Game(name="Hacking in progress ..."))
    await bot.user.edit(username="HackerBot")
    edt1.start()
    edt2.start()
    edt4.start()
    # today = date.today()
    await asyncio.run(await update_schedule())



@bot.event
async def on_message(message):
    global P4,PD
    if message.content == "exit":
        exit()
    # If message come from bot
    if message.author == bot.user:
        return
    #If message is commands
    if message.content.startswith('!'):
        cmd = Commande(message.content)
        # All commande
        if cmd.cmd == "dice":
            await message.channel.send("Throwing dice : "+str(random.randrange(0,10)))
        elif cmd.cmd == "delmsg":
            if cmd.size() == 0:
                await message.channel.send("Err | !delmsg [number]")
                return
            else:
                if cmd.args[0].isdigit():
                    if check_permission("manage_messages",message):
                        await message.channel.purge(limit=int(cmd.args[0])+1);
                    else:
                        await message.channel.send("Err | Not enough right")
                        return
                else:
                    await message.channel.send("Err | Not a number")
                    return
        elif cmd.cmd == "start":
            if cmd.size() >= 2:
                for i in cmd.args:
                    if not i.isdigit():
                        return
                await asyncio.sleep((int(cmd.args[0])*3600 + int(cmd.args[1])*60)/2)
                await message.channel.send("PAUSE ! ")
            else:
                await message.channel.send("Err | !start [hours] [minutes]")
                return
        elif cmd.cmd == "rm":
            if cmd.size() == 0:
                await message.channel.send("Err | !rm [RootMe Name]")
                return
            r = requests.get("https://www.root-me.org/"+cmd.args[0]+"?lang=fr")
            if "L'adresse URL que vous demandez n'existe pas. Le plan du site peut vous aider à trouver l'information recherchée." in r.text:
                await message.channel.send("No user found with : "+cmd.args[0])
                return
            regex = re.compile("<li>Score&nbsp;:&nbsp;<span>([0-9]+)</span></li>")
            result = regex.match(r.text)
            await message.channel.send(cmd.args[0]+" - "+str(result.group(1)))
            return
        elif cmd.cmd == "rmstat":
            if cmd.size() == 0:
                await message.channel.send("Err | !rmstat [RootMe Name]")
                return
            r = requests.get("https://www.root-me.org/"+cmd.args[0]+"?inc=score&lang=fr")
            if "L'adresse URL que vous demandez n'existe pas. Le plan du site peut vous aider à trouver l'information recherchée." in r.text:
                await message.channel.send("No user found with : "+cmd.args[0])
                return
            regex = re.compile("<div class=\"gris\">([0-9%]+)</div>")
            result = regex.findall(r.text)
            regex2 = re.compile("<a href=\".*\" title=\".*\">([a-zA-Z-éè ]+)</a>")
            result2 = regex2.findall(r.text)
            pt = r.text.split("<li>\n<b class=\"tl\">Challenges :</b>\n<span class=\"color1 tl\">\n")[1].split("&")[0]
            sc = r.text.split("<li>\n<b class=\"tl\">Challenges :</b>\n<span class=\"color1 tl\">\n")[1].split("\"gris tm\">\n")[1].split("\n")[0]
            regex3 = re.compile('Place :</b>\n<span class="color1 tl">\n([0-9]+)<span class="gris">/([0-9]+)</span>')
            ranked = regex3.findall(r.text)
            rang = r.text.split("<b class=\"tl\">Rang :</b>")[1].split("&nbsp")[0].split(">")[1]
            embed = discord.Embed(
                                    title="RootMe stat : "+cmd.args[0],
                                    url = "https://www.root-me.org/"+cmd.args[0]+"?inc=score&lang=fr"
                                )
            embed.add_field(name="Points",value=pt)
            embed.add_field(name="Challenge solved",value=sc)
            embed.add_field(name="rank",value=rang)
            embed.add_field(name="ranked",value=ranked[0][0]+"/"+ranked[0][1])
            for i in range(len(result)):
                embed.add_field(name=result2[i],value=result[i],inline=True)
            await message.channel.send(embed=embed)
        elif cmd.cmd == "edt":
            if cmd.size() == 0:
                await message.channel.send("Err | !edt [class] ")
                return
            if not cmd.args[0].isdigit():
                await message.channel.send("Err | Not a Number")
                return
            if cmd.args[0] == "1":
                await message.channel.send(embed=await edt1.Parsing())
            elif cmd.args[0] == "2":
                await message.channel.send(embed=await edt2.Parsing())
            elif cmd.args[0] == "3":
                pass
            elif cmd.args[0] == "4":
                await message.channel.send(embed=await edt4.Parsing())
        elif cmd.cmd == "edtnext":
            if cmd.size() == 0:
                await message.channel.send("Err | !edtnext [class] [[Number week after] default 1]")
                return
            if not cmd.args[0].isdigit():
                await message.channel.send("Err | Not a number")
                return
            numberweek = 1
            if cmd.args[0] == "1":
                edt = Time_Schedule(ID['M1-FI']['username'],ID['M1-FI']['password'],int(cmd.args[0]),next=numberweek)
            elif cmd.args[0] == "2":
                edt = Time_Schedule(ID['M2-FI']['username'],ID['M2-FI']['password'],int(cmd.args[0]),next=numberweek)
            elif cmd.args[0] == "3":
                edt = Time_Schedule(ID['M1-FA']['username'],ID['M1-FA']['password'],int(cmd.args[0]),next=numberweek)
            elif cmd.args[0] == "4":
                edt = Time_Schedule(ID['M2-FA']['username'],ID['M2-FA']['password'],int(cmd.args[0]),next=numberweek)
            # if cmd.size() >= 2:
            #     if not cmd.args[1].isdigit():
            #         await message.channel.send("Err | Not a Number")
            #         return
            #     numberweek = cmd.args[1]
            edt.connection()
            await message.channel.send(embed=await edt.Parsing())
        elif cmd.cmd == "timer":
            if cmd.size() == 0:
                await message.channel.send("Err | !time HH:MM:SS")
                return
            for i in cmd.args[0].split(":"):
                if len(i) != 2:
                    await message.channel.send("Err | !time HH:MM:SS")
                    return
                if not i.isdigit():
                    await message.channel.send("Err | !time HH:MM:SS")
                    return
            hours = cmd.args[0].split(":")[0]
            minutes = cmd.args[0].split(":")[1]
            secondes = cmd.args[0].split(":")[2]
            await message.channel.send("Timer start !")
            await asyncio.sleep(int(hours)*3600 + int(minutes)*60 + int(secondes))
            msg = " " if cmd.size() == 1 else cmd.args[1]
            await message.channel.send("TIME UP ! "+msg)
        elif cmd.cmd == "p4":
            if P4 == None:
                print("creation")
                if cmd.size()==0:
                    P4 = puissance4.Puissance4()
                    await P4.init(message.author.id,bot.user.id,message.channel.id,message,1)
                    await P4.print(message)
                    return
                id = getID(cmd.args[0])
                if id == None:
                    await message.channel.send("Err | "+cmd.args[0]+" not found !")
                    return
                P4 = puissance4.Puissance4()
                await P4.init(message.author.id,id,message.channel.id,message,0)
                await P4.print(message)
            else:
                if cmd.size() == 0:
                    return
                if P4.mod == 0:
                    await P4.start(cmd.args[0],message.author.id,message)
                else:
                    await P4.start_bot(cmd.args[0],message.author.id,message)
            if P4.P4_inGame == False:
                P4 = None
        elif cmd.cmd == "pd":
            if PD == None:
                PD = pendu.Pendu(message)
                await PD.init(message)
            else:
                if cmd.size() == 0:
                    return
                await PD.start(message,cmd.args[0],message.author.id)
            if PD.Pendu_inGame == False:
                PD = None
        elif cmd.cmd == "insult":
            if cmd.size() == 0:
                embed = discord.Embed(
                                        title="Sweet Word",
                                        colour=0x000000
                                    )
                r = requests.get("https://evilinsult.com/generate_insult.php?type=plain&lang=en")
                embed.add_field(name="From : "+message.author.name,value=r.text)
                await message.channel.send(embed=embed)
            else:
                id = getID(cmd.args[0])
                if id == None:
                    await message.channel.send("Err | No one with this name")
                    return
                r = requests.get("https://evilinsult.com/generate_insult.php?type=plain&lang=en")
                embed = discord.Embed(
                                        title="Sweet Word",
                                        colour=0x000000
                                    )
                r = requests.get("https://evilinsult.com/generate_insult.php?type=plain&lang=en")
                embed.add_field(name="From : Someone who think about you",value=r.text)
                user = await bot.fetch_user(id)
                await user.send(embed=embed)
                return
        elif cmd.cmd == "ctftime":
            number = 5
            if cmd.size() > 0 :
                if not cmd.args[0].isdigit():
                    await message.channel.send("Err | Not a Number")
                    return
                if int(cmd.args[0]) > 15:
                    await message.channel.send("Err | !ctftime [nb <= 15]")
                    return
                number = int(cmd.args[0])
            url = "https://ctftime.org/api/v1/events/?limit="+str(number)+"&start="+str(int(time.time()))+"&finish="+str(int(time.time()+100000000))
            header = requests.utils.default_headers()
            header.update({"User-Agent":"ctf_time_discord_bot"})
            r = requests.get(url,headers=header)
            json_format = json.loads(r.text)
            count = 0
            for i in json_format:
                embed = discord.Embed( title=i['title'], colour = 0x000000 if count%2 == 0 else 0xFFFFFF )
                embed.add_field(name=i['url'],value=i['description'])
                embed.add_field(name=i['format'],value="online : "+str(i['onsite']))
                embed.add_field(name="participants : "+str(i['participants']),value="Durations : "+str(i['duration']['days'])+"d:"+str(i['duration']['hours'])+"h")
                embed.add_field(name="start : "+i['start'],value="finish : "+i['finish'])
                count += 1
                await message.channel.send(embed=embed)
        elif cmd.cmd == "help":
            if cmd.size()== 0:
                embed = discord.Embed(
                                            colour=0x01FF00
                                        )
                embed.add_field(name="HELP",value="-----",inline=False)
                embed.add_field(name="Game",value="!help game",inline=True)
                embed.add_field(name="dice",value="!dice => run a dice [1-10]",inline=True)
                embed.add_field(name="delmsg",value="!delmsg [number] => dell $number message",inline=True)
                embed.add_field(name="start",value="!start hh mm => Send message when time given is half ended",inline=True)
                embed.add_field(name="rm",value="!rm [RootMe Name] => give root me point",inline=True)
                embed.add_field(name="rmstat",value="!rmstat [RootMe Name] => Give rootme stats",inline=True)
                embed.add_field(name="edt",value="!edt [class] => give the edt for given class\n        1 : Master 1 FI\n        2 : Master 2 FI\n        3 : Master 1 FA\n        4 : Master 2 FA",inline=False)
                embed.add_field(name="edtnext",value="!edtnext [class] same as !edt but for next week",inline=True)
                embed.add_field(name="timer",value="!timer hh:mm:ss => run timer which gonna end in given time",inline=True)
                embed.add_field(name="insult",value="!insult [Name]=> Send sweet words in current channel, if name is given send DM instead")
                embed.add_field(name="ctftime",value="!ctftime [number default 5] => print [number] upcomming ctf")
                embed.add_field(name="help",value="print this shit")
                await message.channel.send(embed=embed)
            else:
                if cmd.args[0] == "game":
                    embed = discord.Embed(colour=0x01FF00)
                    embed.add_field(name="P4",value="Puissance4 game, run game with !p4 [[namePlayer2] if empty play against bot]\nThen play with !p4 number [1-7]")
                    embed.add_field(name="PD",value="Pendu game, run !pd to begin game then !pd [letter to play] !",inline=True)
                    await message.channel.send(embed=embed)
        else:
            await message.channel.send('Command not found !')
    else:
        return
# Adding and removing role Master 1 & 2 in adding/removing reaction on message in #Role
# Not using on_reaction_add and on_reaction_remove because only works on cached message
@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    role = None
    if message_id == "619622989323042816":
        role = discord.utils.get(guild.roles,name="Master 1ère année")

    if message_id == "619623025557372951":
        role = discord.utils.get(guild.roles,name="Master 2ème année")
    if role is not None:
        member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
        if member is not None:
            await member.add_roles(role)
@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    role = None
    if message_id == "619622989323042816":
        role = discord.utils.get(guild.roles,name="Master 1ère année")

    if message_id == "619623025557372951":
        role = discord.utils.get(guild.roles,name="Master 2ème année")
    if role is not None:
        member = discord.utils.find(lambda m: m.id == payload.user_id, guild.members)
        if member is not None:
            await member.remove_roles(role)

def check_permission(perm,msg):
    for i in msg.author.permissions_in(msg.channel):
        if i[0] == perm:
            return True
    return False

def getID(name):
    for i in bot.users:
        if i.name == name:
            return i.id
    return None
async def update_schedule():
    while True:
        # today = date.today()
        # today = today.strftime("%d/%m/%Y, %H:%M:%S")
        # await bot.get_channel(625675545061097472).fetch_message(625696053794177034).edit("updated - "+str(today))
        # await bot.get_channel(625675545061097472).fetch_message(625696059179401246).edit(embed=await edit1.Parsing())
        # await bot.get_channel(625675545061097472).fetch_message(631869467902738432).edit(embed=await edit3.Parsing())
        # await bot.get_channel(625675545061097472).fetch_message(631869982178934784).edit(embed=await edit4.Parsing())
        # if edt1.bchange == True:
        #     await bot.get_channel(388286013828759553).send("<@619596015615344669> FI There is a changements in your Schedule look <#625675545061097472>")
        #     edt1.bchange = False
        # if edt2.bchange == True:
        #     await bot.get_channel(493180046073397249).send("<@514021108484276224> FI There is a changements in your Schedule look <#625675545061097472> ")
        #     edt2.bchange = False
        # if edt4.bchange == True:
        #     await bot.get_channel(493180046073397249).send("<@619596015615344669> FA There is a changement in your Schedule look <#625675545061097472> ")
        #     edt4.bchange = False

        await asyncio.sleep(edt_reload)


# @client.event
# async def on_member_join(member):
if __name__ == "__main__":
    bot.run(ID['token'])
