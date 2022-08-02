import requests,re,discord,asyncio,time,datetime
from threading import Thread,RLock
from constant import *
lock = RLock()


class Time_Schedule(Thread):
    def __init__(self,username,password,classe,next = "0"):
        """
            Initiate Time schedule variable
                username and password are ez to understand
                class is the class of student
                    1 => Master 1 - FI
                    2 => Master 2 - FI
                    3 => Master 1 - FA
                    4 => Master 2 - FA
                next is default 0, if set to 1, print the next week time schedule
                if next == 0 : open text file to write last changement in schedule, if bot is turned off, read this file to know last changement and notify it

        """
        Thread.__init__(self)
        self.username = username
        self.password = password
        self.classe = ""
        if classe == 1 :
            self.classe = "M1 - FI"
            self.color = 0xFD2D00
        elif classe == 2:
            self.classe = "M2 - FI"
            self.color = 0xFFFFFF
        elif classe == 3:
            self.classe = "M1 - FA"
            self.color = 0x46FE00
        elif classe == 4:
            self.classe = "M2 - FA"
            self.color = 0x01F2FF
        self.next = next
        self.daemon = True
        self.change = []
        if next == "0":
            try:
                with open('.changement'+self.classe.replace(' ','')+'.txt') as f:
                    try:
                        self.change = [f.read()]
                    except:
                        self.change = []
            except:
                self.change = []
        self.bchange = False
        self.first = False
        self.dataToParsing = ""
        self.today = datetime.datetime.today().weekday()

    def run(self):
        """
            Use to run the thread
        """
        while True:
            self.connection()
            time.sleep(edt_reload)
    def connection(self,url="https://cas.uphf.fr/cas/login?service=https%3A%2F%2Fvtmob.uphf.fr%2Fesup-vtclient-up4%2Fstylesheets%2Fdesktop%2Fwelcome.xhtml"):
        """
            Use to connecte through the ENT
            Requests the time schedule and set it in local variable
                parse the last update of time schedule
        """
        self.session = requests.Session()
        r = self.session.get(url)
        execu = re.findall(r'execution\" value=\"[a-zA-Z0-9]+',r.text)[0].split("=")[1].replace('\"',"")
        evt = "submit"
        useragent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) \\ Gecko/20100101 Firefox/40.1"
        submit = "Connexion";
        payload = {"username": self.username,
                "password": self.password,
                "execution": execu,
                "_eventId": 'submit',
                 }
        r = self.session.post(url,data=payload,allow_redirects=True)
        if self.next == "0":
            self.dataToParsing = r.text
            Rchange = re.findall(r'<span style=\'color:black; font-size:7pt; float: right;\'>Dernière mise à jour : ([0-9/ :]*)</span>',r.text)
            new_today = datetime.datetime.today().weekday()
            # print("test ")
            # print(Rchange)
            if self.today == 6 and new_today == 0:
                self.today = datetime.datetime.today().weekday()
                self.change= []
                self.bchange = False
            else :
                try:
                    if self.change != [] and len(Rchange)>0 and Rchange != ['']:
                        if self.change != [Rchange[0]]:
                            self.bchange = True
                            self.change = [Rchange[0]]
                            with open('.changement'+self.classe.replace(' ','')+'.txt','w') as f:
                                f.write(Rchange[0])
                    else:
                        try:
                            if len(Rchange) > 0 and Rchance != ['']:
                                self.change = [Rchange[0]]
                                with open('.changement'+self.classe.replace(' ','')+'.txt','w') as f:
                                    f.write(Rchange[0])
                            else:
                                self.bchange = False
                                self.change = []
                        except:
                            self.change = []
                            self.bchange = False
                except:
                    self.change = []
                    self.bchange = False
        else :
            for i in range(1,int(self.next)+1):
                payload = {
                            'org.apache.myfaces.trinidad.faces.FORM':'form_week',
                            '_noJavaScript':'false',
                            'javax.faces.ViewState':'!'+str(i),
                            'form_week:_idcl':'form_week:btn_next'
                          }
                r = self.session.post("https://vtmob.uphf.fr/esup-vtclient-up4/stylesheets/desktop/welcome.xhtml",data=payload,allow_redirects=True)
                self.dataToParsing = r.text
                self.first = True
        self.today = datetime.datetime.today().weekday()
        print("test 2 : "+str(self.change))
    def Parsing(self):
        """
            Use to parse the time schedule and return Embbed
        """
        #print(self.dataToParsing)

        time.sleep(5)
        jours = self.dataToParsing.split('<tr class="even_row"><td class="blank_column" colspan="58">')
        i = 1
        embed = discord.Embed(
                                title="Schedule : "+self.classe,
                                colour = self.color
                             )
        while i < len(jours)-1:
            # day = re.findall(r'blank_column"><b>([a-zA-Z0-9. -]+)',jours[i])
            # hour = re.findall(r'(TD|TP|CM|AUTRE|RES)"><tbody><tr><td><b>([0-9:-]+)',jours[i])
            # type = re.findall(r'info_bulle"><br\/><br\/><b>([A-Z0-9 ]+)',jours[i])
            # cour = re.findall(r'content_bulle"><u>([a-zA-Z0-9- ()]+)',jours[i])
            # location = re.findall(r"rouge'>([A-Z0-9() -]+)",jours[i])
            # prof = re.findall(r"vert'>([A-Za-z ]+)",jours[i])
            # embed.add_field(name=day[0],value="--------------",inline=False)
            # if (len(hour)==0):
            #     embed.add_field(name='? no class ',value="None")
            # else:
            #     debug = 0
            #     for j in range(len(hour)):
            #         hour[j] = hour[j][1]
            #         auxcour,debug = correction(cour,j,debug,jours[i])
            #         auxtype,debug = correction(type,j,debug,jours[i])
            #         auxhour,debug = correction(hour,j,debug,jours[i])
            #         auxlocation,debug = correction(location,j,debug,jours[i])
            #         auxprof,debug = correction(prof,j,debug,jours[i])
            #         if len(hour)>= 1:
            #             #print(hour[j])
            #             embed.add_field(name=auxcour + " "+auxtype,value=auxhour+" "+auxlocation+" with "+auxprof,inline=False)
            #             # print('# '+cour[j]+'|'+type[j]+' : '+hour[j][1]+" : "+hour[j][1] +' with :'+prof[j])
            day = re.findall(r'blank_column"><b>([a-zA-Z0-9. -]+)',jours[i])
            classe = re.findall(r'<table class=".{1,5}">.*',jours[i])
            embed.add_field(name=day[0],value="--------------",inline=False)
            for j in classe:
                hour = re.findall(r'(TD|TP|CM|AUTRE|RES)"><tbody><tr><td><b>([0-9:-]+)',j)
                if len(hour) == 0:
                    hour.append("Undefined")
                type = re.findall(r'info_bulle"><br\/><br\/><b>([A-Z0-9 ]+)',j)
                if len(type) == 0:
                    type.append("Undefined")
                cour = re.findall(r'content_bulle"><u>([a-zA-Z0-9- ()]+)',j)
                if len(cour) == 0:
                    cour.append("Undefined")
                location = re.findall(r"rouge'>([A-Z0-9() -]+)",j)
                if len(location) == 0:
                    location.append("Undefined")
                prof = re.findall(r"vert'>([A-Za-z -]+)<",j)
                if len(prof) == 0:
                    prof.append("Undefined")
                mp = re.findall(r'style="color:red;"><br\/>([a-zA-Z0-9-+ ]*)<\/span>',j)
                # print(hour)
                # print(type)
                # print(cour)
                # print(location)
                # print(prof)
                if len(mp) == 0:
                    embed.add_field(name=cour[0] + " "+type[0],value=hour[0][1]+" "+location[0]+" with "+prof[0],inline=False)
                else:
                    embed.add_field(name=cour[0] + " "+type[0],value=hour[0][1]+" "+location[0]+" with "+prof[0]+"\nSpecial : "+mp[0],inline=False)

            i+=1
        return embed

def correction(elem,i,debug,jour):
    """
        Currently not used
    """
    aux = ""
    try:
        if elem[i]:
            pass
        aux = elem[i]
    except:
        aux = re.findall(r'style="color:red;"><br\/>([a-zA-Z0-9-+ ]*)<\/span>',jour)
        #print(aux)
        try :
            #print(aux)
            #print(debug)
            #print(aux[debug])
            aux = aux[debug]
            debug+=1
        except:
            aux = "Undefined"
    return aux,debug
