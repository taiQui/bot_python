import discord
from classe import Commande,Vote,Log
from datetime import date,datetime
from edt import Time_Schedule
from constant import *
from threading import Thread,RLock
import puissance4,pendu
import random,asyncio,requests,re,json,time
from PIL import Image,ImageFont,ImageDraw
from io import BytesIO
from epic_free import Epic_Free
"""
Author : taiQui
Description : Bot discord
Github : https://github.com/taiQui/ ( private repository )
Doc : https://discordpy.readthedocs.io/en/rewrite/api.html
Comments :  [ !!! IMPORTANT !!! ]
            The bot need Bot token ID to be launched
            The bot need Credentials to start time schedules, one creds by class
            The bot need Token for get box for HackTheBox(!htb_m) commande
            All this creds are located in .token file, this file is json format

            Discord bot use async/await function to synchronize the requests
            To use a async function ( look doc ), use 'await' keyword before the call of this function





Global variable
    edt* => Represent time schedule for class
        1 => Master 1 - FI
        2 => Master 2 - FI
        3 => Master 1 - FA
        4 => Master 2 - FA
    P4 => Var to initiate the 'Connect 4' (puissance 4)
    PD => Var to initiate the 'Hangman' ( le pendu )
    vote => Var to initiate the vote class
    verrou => currently not used
    insulttab => currently not used ( in developpement )
"""



intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = discord.Client(intents=intents)

ID = json.load(open('.token','r')) # get json file with ID
#create Thread to read schedule
edt1 = Time_Schedule(ID['M1-FI']['username'],ID['M1-FI']['password'],1)
edt2 = Time_Schedule(ID['M2-FI']['username'],ID['M2-FI']['password'],2)
# edt3 = Time_Schedule(USERNAME,PASSWORD,3)
edt4 = Time_Schedule(ID['M2-FA']['username'],ID['M2-FA']['password'],4)
epic_free = Epic_Free()

P4 = None
PD = None
vote = None
insulttab = []
verrou = RLock()
last = 0
#####################
"""
    When the bot is ready, it run this function
        Write in 'log_bot' channel it is open
        change his name and his activity
        Start all thread related to time schedule
        start main loop related to changement in time schedule
"""
@bot.event
async def on_ready():

    await Log("online - ",True,bot)
    print('Connexion')
    await bot.change_presence(activity=discord.Game(name="Hacking in progress ..."))
    await bot.user.edit(username="HackerBot 2.0")
    edt1.start()
    edt2.start()
    edt4.start()
    epic_free.start()
    # today = date.today()
    await asyncio.run(await update_schedule())


# Each Time a message is sent, this function is ran
# Test if the message come from the bot => return
#     or if the message come from some user => parsing
# check if the message begin with '!' => message == command
#     else return


@bot.event
async def on_message(message):
    global P4,PD,vote,insulttab,verrou
    # If message come from bot
    if message.author == bot.user:
        return
    #If message is commands
    if message.content.startswith('!'):
        cmd = Commande(message.content)
        await Log("command : "+cmd.cmd+" with args : "+str(cmd.args)+" by "+message.author.name,True,bot)
        # All commande
        # Throw a dice between 0 and 9
        if cmd.cmd == "dice":
            try :
                await message.channel.send("Throwing dice : "+str(random.randrange(0,10)))
            except Exception as e:
                await Log("Error in 'dice' command ",True,bot,info=e)
        # delete [number] message ( limit : 100 ), all message have to be cached by the server to be deleted
        elif cmd.cmd == "delmsg":
            try:
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
            except Exception as e:
                await Log("Error in 'delmsg' command ",True,bot,info=e)
        # Start a timer with [hours] [minutes] which throw BREAK when middle time of the coutdown is reached
        elif cmd.cmd == "start":
            try:
                if cmd.size() >= 2:
                    for i in cmd.args:
                        if not i.isdigit():
                            return
                    await asyncio.sleep((int(cmd.args[0])*3600 + int(cmd.args[1])*60)/2)
                    await message.channel.send("PAUSE ! ")
                else:
                    await message.channel.send("Err | !start [hours] [minutes]")
                    return
            except Exception as e:
                await Log("Error in 'start' command ",True,bot,info=e)
        # Print root-me score for [user]
        # I'm not using the API, this code is older than root-me API, i'm just parsing the source code
        elif cmd.cmd == "rm":
            try:
                if cmd.size() == 0:
                    await message.channel.send("Err | !rm [RootMe Name]")
                    return
                r = requests.get("https://www.root-me.org/"+cmd.args[0]+"?lang=fr")
                if "L'adresse URL que vous demandez n'existe pas. Le plan du site peut vous aider à trouver l'information recherchée." in r.text:
                    await message.channel.send("No user found with : "+cmd.args[0])
                    return
                result = r.text.split('Points</span>')[0].split('</h3>')[-2].split(';')[-1]
                await message.channel.send(cmd.args[0]+" - "+str(result))
                return
            except Exception as e:
                await Log("Error in 'rm' command ",True,bot,info=e)
        # Print root-me stats of all category
        # I'm not using the API, this code is older than root-me API, i'm just parsing the source code
        elif cmd.cmd == "rmstat":
            try:
                if cmd.size() == 0:
                    await message.channel.send("Err | !rmstat [RootMe Name]")
                    return
                r = requests.get("https://www.root-me.org/"+cmd.args[0]+"?inc=info&lang=fr")
                if "L'adresse URL que vous demandez n'existe pas. Le plan du site peut vous aider à trouver l'information recherchée." in r.text:
                    await message.channel.send("No user found with : "+cmd.args[0])
                    return
                reg = re.compile('href="fr/Challenges/([A-Za-z0-9é àè-]*)/">([0-9% ]*)')
                result = reg.findall(r.text.split('small-12 columns')[-3])
                pt = r.text.split('Points</span>')[0].split('</h3>')[-2].split(';')[-1]
                sc = r.text.split('class="gras">Challenges</span>')[0].split('</h3>')[-2].split(';')[-1]

                ranked = r.text.split('class="gras">Place</span>')[0].split('</h3>')[-2].split(';')[-1]
                embed = discord.Embed(
                                        title="RootMe stat : "+cmd.args[0],
                                        url = "https://www.root-me.org/"+cmd.args[0]+"?inc=score&lang=fr"
                                    )
                embed.add_field(name="Points",value=pt)
                embed.add_field(name="Challenge solved",value=sc)
                embed.add_field(name="ranked",value=ranked)
                embed.add_field(name="---",value="___",inline=False)
                for i in result:
                    embed.add_field(name=i[0],value=i[1],inline=True)
                await message.channel.send(embed=embed)
            except Exception as e:
                await Log("Error in 'rmstat' command ",True,bot,info=e)
        # Print time schedule for given class
        # Refer to top of this source code to know the code of your class
        # Use the credential of one student by class to know the time schedule
        # This class is located in edt.py file
        elif cmd.cmd == "edt":
            try:
                if cmd.size() == 0:
                    await message.channel.send("Err | !edt [class] ")
                    return
                if not cmd.args[0].isdigit():
                    await message.channel.send("Err | Not a Number")
                    return
                if cmd.args[0] == "1":
                    await message.channel.send(embed=edt1.Parsing())
                elif cmd.args[0] == "2":
                    await message.channel.send(embed=edt2.Parsing())
                elif cmd.args[0] == "3":
                    pass
                elif cmd.args[0] == "4":
                    await message.channel.send(embed=edt4.Parsing())
            except Exception as e:
                await Log("Error in 'edt' command ",True,bot,info=e)
        # Print newt week's time schedule for given class
        # same as !edt commande above
        elif cmd.cmd == "edtnext":
            try:
                if cmd.size() == 0:
                    await message.channel.send("Err | !edtnext [class] [[Number week after] default 1]")
                    return
                if not cmd.args[0].isdigit():
                    await message.channel.send("Err | Not a Number")
                    return
                numberweek = 1
                if cmd.size() == 2:
                    if not cmd.args[1].isdigit():
                        await message.channel.send("Err | Not a Number")
                        return
                    numberweek = cmd.args[1]
                if cmd.args[0] == "1":
                    edt = Time_Schedule(ID['M1-FI']['username'],ID['M1-FI']['password'],int(cmd.args[0]),next=numberweek)
                elif cmd.args[0] == "2":
                    edt = Time_Schedule(ID['M2-FI']['username'],ID['M2-FI']['password'],int(cmd.args[0]),next=numberweek)
                elif cmd.args[0] == "3":
                    edt = Time_Schedule(ID['M1-FA']['username'],ID['M1-FA']['password'],int(cmd.args[0]),next=numberweek)
                elif cmd.args[0] == "4":
                    edt = Time_Schedule(ID['M2-FA']['username'],ID['M2-FA']['password'],int(cmd.args[0]),next=numberweek)
                else:
                    return
                # if cmd.size() >= 2:
                #     if not cmd.args[1].isdigit():
                #         await message.channel.send("Err | Not a Number")
                #         return
                #     numberweek = cmd.args[1]
                edt.connection()
                await message.channel.send(embed=edt.Parsing())
            except Exception as e:
                await Log("Error in 'edtnext' command ",True,bot,info=e)
        # Run a countdown which have to be of this shape : HH:MM:SS with HH : hours MM: minutes SS: seconds
        elif cmd.cmd == "timer":
            try:
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
            except Exception as e:
                await Log("Error in 'timer' command ",True,bot,info=e)
        # Allow to begin a game of 'connect 4' game (puissance 4)
        # !p4 [user to play with ] if user is not mentionned, play against bad IA (lol)
        # It's also usefull to play at this game !p4 [line number to play]
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
        # Allow to initiate 'Hangman game' (Pendu)
        # also Usefull to play => !pd [letter/word]
        elif cmd.cmd == "pd":
            try:
                if PD == None:
                    PD = pendu.Pendu(message)
                    await PD.init(message)
                else:
                    if cmd.size() == 0:
                        return
                    await PD.start(message,cmd.args[0],message.author.id)
                if PD.Pendu_inGame == False:
                    PD = None
            except Exception as e:
                await Log("Error in 'pd' command ",True,bot,info=e)
        # The bot request a insult website to insult someone in your name
        # If you give a [user], the bot will send private message with insult to him
        # Currently in developpement to prevent too much insult
        elif cmd.cmd == "insult":
            # i = 0
            # test_ban = False
            # with verrou:
            #     while i < len(insulttab):
            #         if insulttab[i][0] == message.author.id:
            #             if time.time()-insulttab[i][1] < 10:
            #                 guild = bot.get_guild(491530086319783938)
            #                 role = discord.utils.get(guild.roles,name="EXCLUS")
            #                 if role is not None:
            #                     member = discord.utils.find(lambda m: m.id == message.author.id,guild.members)
            #                     if member is not None:
            #                         test_ban = True
            #                         await member.add_roles(role)
            #                         await message.channel.send("You are banned from chat for 1minutes")
            #                         await asyncio.sleep(60)
            #                         await member.remove_roles(role)
            #                         await message.channel.send("You are now able to speak")
            #                     else:
            #                         print("not found")
            #             insulttab = insulttab[0:i]+insulttab[i+1:]
            #         else:
            #             i+=1
            # if test_ban:
            #     return
            try :
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
            except Exception as e:
                await Log("Error in 'insult' command ",True,bot,info=e)
            # with verrou:
            #     insulttab.append([message.author.id,time.time()])
        # Print ctf available on website
        # You can give [number] of ctf you want print else 5 will be print
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
            try:
                url = "https://ctftime.org/api/v1/events/?limit="+str(number)+"&start="+str(int(time.time()))+"&finish="+str(int(time.time()+100000000))
                header = requests.utils.default_headers()
                header.update({"User-Agent":"ctf_time_discord_bot"})
                r = requests.get(url,headers=header)
                json_format = json.loads(r.text)
            except Exception as e:
                await Log("Error in 'ctftime' command, test numero 1 ",True,bot,info=e)
            count = 0


            for i in json_format:
                try:
                    title = i['title']
                    title = correction(title)
                except:
                    title = "None"
                try:
                    url = i['url']
                    url = correction(url)
                except:
                    url = "None"
                try:
                    format = i['format']
                    format = correction(format)
                except:
                    format = "None"
                try:
                    desc = i['description']
                    desc = correction(desc)
                except:
                    desc = "None"
                try:
                    online = i['online']
                    online = correction(online)
                except:
                    online = "None"
                try:
                    onsite = i['onsite']
                    onsite = correction(onsite)
                except:
                    onsite = "None"
                try:
                    participants = i['participants']
                    participants = correction(participants)
                except:
                    participants = -1
                try:
                    day = i['duration']['days']
                    day = correction(day)
                except:
                    day = -1
                try:
                    hour =  i['duration']['hours']
                    hour = correction(hour)
                except:
                    hour = -1
                try:
                    start = i['start']
                    start = correction(start)
                except:
                    start = "None"
                try:
                    finish = i['finish']
                    finish = correction(finish)
                except:
                    finish = "None"
                try:
                    embed = discord.Embed( title=title, colour = 0x000000 if count%2 == 0 else 0xFFFFFF )
                    embed.add_field(name=url,value=desc)
                    embed.add_field(name=format,value="online : "+str(not onsite)) if type(onsite) == type(True) else "None"
                    embed.add_field(name="participants : "+str(participants),value="Durations : "+str(day)+"d:"+str(hour)+"h")
                    embed.add_field(name="start : "+start,value="finish : "+finish)
                    count += 1
                    await message.channel.send(embed=embed)
                except Exception as e:
                    await Log("Error in 'ctftime' command, test numero 2",True,bot,info=e)
        # Initiate a vote - a vote haven't be still initiate
        elif cmd.cmd == "vote":
            try:
                if vote == None:
                    msg = await message.channel.send("<@"+str(message.author.id)+"> Start a vote !")
                    utime = 1
                    if cmd.size() != 0:
                        if not cmd.args[0].isdigit():
                            await message.channel.send("Err | Not a Number")
                            return
                        utime = int(cmd.args[0])
                    vote = Vote(msg.id,msg,utime)
                else:
                    await message.channel.send("Err | vote already instantiated")
                    return
            except Exception as e:
                await Log("Error in 'vote' command ",True,bot,info=e)
        # Use to add a question ( only one per vote ) to a vote
        elif cmd.cmd == "vote_q":
            try:
                if vote == None:
                    await message.channel.send("Err | !vote before ")
                    return
                if cmd.size() == 0:
                    await message.channel.send("Err | !vote_q Question")
                    return
                vote.setQ(cmd.args)
                await vote.prepare()
                await message.delete()
            except Exception as e:
                await Log("Error in 'vote_q' command ",True,bot,info=e)
        # Use to add a response to a vote ( max : 15 )
        elif cmd.cmd == "vote_r":
            try:
                if vote == None:
                    await message.channel.send("Err | !vote before ")
                    return
                if cmd.size() == 0:
                    await message.channel.send("Err | !vote_r Response")
                    return
                if len(vote.response) > 10:
                    await message.channel.send("Err | can't add more response : 10 max")
                    return
                vote.setR(cmd.args)
                await vote.prepare()
                await message.delete()
            except Exception as e:
                await Log("Error in 'vote_r' command ",True,bot,info=e)
        # Use to start a vote
        elif cmd.cmd == "vote_s":
            try:
                if vote.question == "" and len(vote.response) < 1:
                    await message.channel.send("Err | Need 1 Question and 1 response")
                    return
                a = await vote.prepare()
                vote.start()
                vote.join()
                await vote.end()
                vote = None
            except Exception as e:
                await Log("Error in 'vote_s' command ",True,bot,info=e)
        # Use to clean a vote
        elif cmd.cmd == "vote_c":
            vote = None
            await message.channel.send("Vote cleared !")
            return
        # Print [number] (default ALL active box) active box from HackTheBox
        # Use the token HackTheBox API located in setting of your account
        elif cmd.cmd == "htb_m":
            try:
                nbbox = 0
                if cmd.size() > 0:
                    if not cmd.args[0].isdigit():
                        await message.channel.send("Err | Not a Number ")
                        return
                    nbbox = int(cmd.args[0])
                url = "https://hackthebox.eu/api/machines/get/all?api_token="+ID['htb_api']
                head = requests.utils.default_headers()
                head.update({"User-Agent":"bot_htb"})
                r = requests.get(url,headers=head)
                print(r.text)
                r = json.loads(r.text)[::-1]
                i = 0
                if nbbox == 0 :
                    nbbox = len(r)
                while i < nbbox:
                    if r[i]['retired'] == False:
                        embed = discord.Embed(  title=r[i]['name']+"\n"+"-"*(len(r[i]['name'])+len(r[i]['name'])//2),
                                                colour = randomColor(),
                                            )
                        url = r[i]['avatar_thumb']
                        embed.set_thumbnail(url=r[i]['avatar_thumb'])
                        embed.add_field(name="OS : "+r[i]['os'],value="IP : "+r[i]['ip'])
                        embed.add_field(name="Rating : "+str(r[i]['rating']),value="Points : "+str(r[i]['points']))
                        embed.add_field(name="User : "+str(r[i]['user_owns']),value="Root : "+str(r[i]['root_owns']))
                        await message.channel.send(embed=embed)
                    i += 1
                return
            except Exception as e:
                await Log("Error in 'htb_m' command ",True,bot,info=e)
        # Print all news from The Hacker News (website)
        elif cmd.cmd == "hn":
            try:
                r = requests.get('https://thehackernews.com/')
                text = r.text.split('body-post clear')[1:]
                for i in text:
                    url = i.split('story-link')[1].split('href="')[1].split('"')[0]
                    thumb = i.split('img-ratio')[1].split('src=\'')[1].split('\'')[0]
                    title = i.split('home-title\'>')[1].split('<')[0]
                    date = i.split('item-label')[1].split('</i>')[1].split('<')[0]
                    desc = i.split('home-desc\'>')[1].split('<')[0]
                    embed = discord.Embed(title=title,colour=randomColor(),url=url)
                    embed.set_thumbnail(url=thumb)
                    embed.add_field(name=desc,value=date)
                    await message.channel.send(embed=embed)
            except Exception as e:
                await Log("Error in 'hn' command ",True,bot,info=e)
        # Print a photo with [user] in the photo, Used to summon [user] to start the debate
        elif cmd.cmd == "attaque":
            try:
                if cmd.size() == 0:
                    await message.channel.send("Err | !attaque [name]")
                    return
                name = ""
                for i in cmd.args:
                    name += i+" "
                name = name[:-1]
                cmd.args[0] = name
                url_av = ""
                for i in bot.users:
                    if i.name == cmd.args[0]:
                        url_av = i.avatar_url
                if url_av == "":
                    await message.channel.send("Err | No one found with this name")
                    return
                img_out = Image.open('img/out.jpg')
                w,h = img_out.size
                img_add = Image.open(requests.get(url_av,stream=True).raw).resize((50,50))
                w2,h2 = img_add.size
                img_back_add = Image.new('RGB',(w2 + 120,h2),(255,255,255,255))
                img_back_add.paste(img_add,(0,0))
                draw = ImageDraw.Draw(img_back_add)
                draw.text((w2+10,h2//2),cmd.args[0],(0,0,0))
                img_out.paste(img_back_add,(190,150))
                img_out.save('img/merge.jpg')
                file = discord.File('img/merge.jpg',filename='img/merge.jpg')
                await message.channel.send("JE T'APELLE <@"+str(getID(cmd.args[0]))+">",file=file)
                return
            except Exception as e:
                await Log("Error in 'attaque' command ",True,bot,info=e)
        # Recall someone from a debate
        elif cmd.cmd == "rappel":
            try:
                if cmd.size() == 0:
                    await message.channel.send("Err | !rappel [name]")
                    return
                name = ""
                for i in cmd.args:
                    name += i+" "
                name = name[:-1]
                cmd.args[0] = name
                url_av = ""
                for i in bot.users:
                    if i.name == cmd.args[0]:
                        url_av = i.avatar_url
                if url_av == "":
                    await message.channel.send("Err | No one found with this name")
                    return
                img_out = Image.open('img/back.jpg')
                w,h = img_out.size
                img_add = Image.open(requests.get(url_av,stream=True).raw).resize((50,50))
                w2,h2 = img_add.size
                img_back_add = Image.new('RGB',(w2 + 120,h2),(255,255,255,255))
                img_back_add.paste(img_add,(0,0))
                draw = ImageDraw.Draw(img_back_add)
                draw.text((w2+10,h2//2),cmd.args[0],(0,0,0))
                img_out.paste(img_back_add,(220,320))
                img_out.save('img/merge.jpg')
                file = discord.File('img/merge.jpg',filename='img/merge.jpg')
                await message.channel.send("Revient <@"+str(getID(cmd.args[0]))+">, Tu as bien combattu !",file=file)
                return
            except Exception as e:
                await Log("Error in 'rappel' command ",True,bot,info=e)
        # Use if someone got rekt in talk
        elif cmd.cmd == "ko":
            try:
                if cmd.size() == 0:
                    await message.channel.send("Err | !rappel [name]")
                    return
                name = ""
                for i in cmd.args:
                    name += i+" "
                name = name[:-1]
                cmd.args[0] = name
                url_av = ""
                for i in bot.users:
                    if i.name == cmd.args[0]:
                        url_av = i.avatar_url
                if url_av == "":
                    await message.channel.send("Err | No one found with this name")
                    return
                img_out = Image.open('img/ko.jpg')
                w,h = img_out.size
                img_add = Image.open(requests.get(url_av,stream=True).raw).resize((50,50))
                w2,h2 = img_add.size
                img_back_add = Image.new('RGB',(w2 + 120,h2),(255,255,255,255))
                img_back_add.paste(img_add,(0,0))
                draw = ImageDraw.Draw(img_back_add)
                draw.text((w2+10,h2//2),cmd.args[0],(0,0,0))
                img_out.paste(img_back_add,(450,150))
                img_out.save('img/merge.jpg')
                file = discord.File('img/merge.jpg',filename='img/merge.jpg')
                await message.channel.send("<@"+str(getID(cmd.args[0]))+"> est KO !",file=file)
                return
            except Exception as e:
                await Log("Error in 'ko' command ",True,bot,info=e)
        # Print all news from Journal du Geek (website)
        # Possible to mentionned which page of the website you want to print
        elif cmd.cmd == "jdg":
            try:
                default_page = "1"
                if cmd.size() == 0:
                    default_page = "1"
                else:
                    if not cmd.args[0].isdigit():
                        await message.channel.send("Err | Not a Number")
                        return
                    default_page = str(cmd.args[0])
                r = requests.get("https://www.journaldugeek.com/articles/page/"+default_page)

                content = r.text.split('section id="js-single-content"')[1]
                articles_list = content.split('class="archive__list__item"')
                print(len(articles_list))
                for i in range(1,len(articles_list)):
                    try:
                        title = articles_list[i-1].split('title="')[-1].split('"')[0]
                        url = articles_list[i-1].split('href="')[-1].split('"')[0]
                        try :
                            description = articles_list[i].split('class="entry__excerpt">')[1].split('</p>')[0]
                        except:
                            description = "Not able to get description"
                        embed = discord.Embed(title=title,url=url,colour=randomColor())
                        embed.add_field(name="-"*len(title),value=description)
                        await message.channel.send(embed=embed)
                    except:
                        await message.channel.send("Err | Unable to get articles")
                return
            except Exception as e:
                await Log("Error in 'jdg' command ",True,bot,info=e)
        # Print all command and syntaxe
        # You can give "game" arguments to have help about game
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
                embed.add_field(name="vote",value="!vote [time in minutes] => Create vote instance running for [time default 1]minutes")
                embed.add_field(name="vote_q",value="!vote_q question => Add question to the vote instance")
                embed.add_field(name="vote_r",value="!vote_r response => Add response to the vote instance")
                embed.add_field(name="vote_s",value="!vote_s => start the vote now")
                embed.add_field(name="htb_m",value="!htb_m [nb] => print all/nb active machine")
                embed.add_field(name="hn",value="!hn => print first cover of the hacker news site")
                embed.add_field(name="attaque",value="!attaque [name] => begin fight with pokemon [name]")
                embed.add_field(name="rappel",value="!rappel name => end fight with pokemon [name]")
                embed.add_field(name="ko",value="!ko => pokemon [name] is ko")
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


# Say if something get ot get removed "exclus" role
@bot.event
async def on_member_update(before,after):
    was_excluded = False
    excluded = False
    for role in before.roles:
        if role.id == 629294305952923670:
            was_excluded = True

    for role in after.roles:
        if role.id == 629294305952923670:
            excluded = True
    if was_excluded and not excluded:
        await bot.get_channel(493180046073397249).send("<@"+str(after.id)+"> You are now Free to speak !")
    if not was_excluded and excluded:
        await bot.get_channel(493180046073397249).send("<@"+str(after.id)+"> You are now excluded, You are not able to speak anymore !")


# Adding and removing role Master 1 & 2 in adding/removing reaction on message in #Role
# Not using on_reaction_add and on_reaction_remove because only works on cached message
@bot.event
async def on_raw_reaction_add(payload):
    message_id = payload.message_id
    role = None
    guild = bot.get_guild(491530086319783938)
    if message_id == 619622989323042816:
        role = discord.utils.get(guild.roles,name="Master 1ère année")

    if message_id == 619623025557372951:
        role = discord.utils.get(guild.roles,name="Master 2ème année")
    if role is not None:
        member = guild.get_member(payload.user_id)
        member = payload.member
        if member is not None:
            await member.add_roles(role)
@bot.event
async def on_raw_reaction_remove(payload):
    message_id = payload.message_id
    role = None
    print(payload)  
    guild = bot.get_guild(491530086319783938)
    if message_id == 619622989323042816:
        role = discord.utils.get(guild.roles,name="Master 1ère année")

    if message_id == 619623025557372951:
        role = discord.utils.get(guild.roles,name="Master 2ème année")
    if role is not None:
        guild = bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member is not None:
            await member.remove_roles(role)

# Generate a random color
def randomColor():
    return int(hex(random.randrange(0,255))[2:]+hex(random.randrange(0,255))[2:]+hex(random.randrange(0,255))[2:],16)
# Check if the author of message got the [permission]
def check_permission(perm,msg):
    # print("author : "+msg.author)
    # print("permission : ")
    for i in msg.author.permissions_in(msg.channel):
        # print(i)
        # print("-----")
        if i[0] == perm:
            if i[1] == True:
                return True
    return False
# Return ID from a name of user
def getID(name):
    for i in bot.users:
        if i.name == name:
            return i.id
    return None
# Return None if no value is given
def correction(arg):
    if arg == "":
        return "None"
    return arg[:1024]

#Deamon to actualize Schedule
# Print time schedule for all class
# if changement in time schedule ( look the mentionned : "Derniere mise a jours" in website to know if there is a changement or not)
async def update_schedule():
    while True:
        try:
            if not epic_free.gameTook:
                # print('here')
                if epic_free.game != []:
                    # print('here 2')
                    for i in epic_free.game:
                        # print('here 3')
                        embed = discord.Embed(
                                                title=i[0],
                                                colour = 0x000000,
                                                url=i[2]
                        )
                        if i[1] != "" and i[1] != None:
                            embed.set_thumbnail(url=i[1])
                        await bot.get_channel(713703038518558742).send(embed=embed)
                    epic_free.gameTook = True
                    # print('here 4')
                if epic_free.error != "":
                    await Log("Error in Epic_Free 1 ",True,bot,info=epic_free.error)
                    epic_free.error = ""
        except Exception as e:
            await Log("Error in Epic_free 2 ",True,bot,info=e)
        try:
            today = datetime.today()
            today = today.strftime("%d/%m/%Y %H:%M:%S")
            update = await bot.get_channel(625675545061097472).fetch_message(625696053794177034)
            await update.edit(content="updated - "+str(today))
            edt_change = await bot.get_channel(625675545061097472).fetch_message(625696059179401246)
            await edt_change.edit(embed= edt1.Parsing())
            edt_change = await bot.get_channel(625675545061097472).fetch_message(631869467902738432)
            await edt_change.edit(embed= edt2.Parsing())
            edt_change = await bot.get_channel(625675545061097472).fetch_message(631869982178934784)
            await edt_change.edit(embed= edt4.Parsing())
            if edt1.bchange == True:
                await bot.get_channel(619594025917480960).send("M1 - FI There is a changements in your Schedule look <#625675545061097472>")
                edt1.bchange = False
            if edt2.bchange == True:
                await bot.get_channel(534805365968076801).send("M2 - FI There is a changements in your Schedule look <#625675545061097472> ")
                edt2.bchange = False
            if edt4.bchange == True:
                await bot.get_channel(534805365968076801).send("M2 - FA There is a changement in your Schedule look <#625675545061097472> ")
                edt4.bchange = False
        except Exception as e:
            await Log("Error in 'update_schedule'",True,bot,info=e)
        await asyncio.sleep(edt_reload)

if __name__ == "__main__":
    bot.run(ID['token'])
