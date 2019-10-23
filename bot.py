import discord
from classe import Commande
from datetime import date
from edt import Time_Schedule
from constant import *
from threading import Thread
import puissance4
import random,asyncio,requests,re,json

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
    global P4
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
                print("already created")
                if P4.mod == 0:
                    await P4.start(cmd.args[0],message.author.id,message)
                else:
                    await P4.start_bot(cmd.args[0],message.author.id,message)
            if P4.P4_inGame == False:
                P4 = None

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
        # today = today.strftime("%d/%m/%Y")
        # bot.get_channel("625675545061097472").fetch_message("625696053794177034").edit("updated - "+str(today))
        # bot.get_channel("625675545061097472").fetch_message("625696059179401246").edit(embed=await edit1.Parsing())
        # bot.get_channel("625675545061097472").fetch_message("631869467902738432").edit(embed=await edit3.Parsing())
        # bot.get_channel("625675545061097472").fetch_message("631869982178934784").edit(embed=await edit4.Parsing())
        await asyncio.sleep(edt_reload)


# @client.event
# async def on_member_join(member):
if __name__ == "__main__":
    bot.run(ID['token'])
