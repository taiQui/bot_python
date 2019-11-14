import requests,re,discord,asyncio,time,datetime
from threading import Thread,RLock
from constant import *
lock = RLock()

class Time_Schedule(Thread):
    def __init__(self,username,password,classe,next = 0):
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
        self.change = ""
        self.bchange = False
        self.first = False
        self.dataToParsing = ""
        self.today = datetime.datetime.today().weekday()

    def run(self):
        while True:
            self.connection()
            time.sleep(edt_reload)
    def connection(self,url="https://cas.uphf.fr/cas/login?service=https%3A%2F%2Fvtmob.uphf.fr%2Fesup-vtclient-up4%2Fstylesheets%2Fdesktop%2Fwelcome.xhtml"):
        self.session = requests.Session()
        r = self.session.get(url)
        lt = re.findall(r'LT-[0-9]+-[a-zA-Z0-9]+-cas\.uphf\.fr',r.text)[0]
        execu = re.findall(r'execution\" value=\"[a-zA-Z0-9]+',r.text)[0].split("=")[1].replace('\"',"")
        evt = "submit"
        ipadress = re.findall(r'ipAddress" value="[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+',r.text)[0].split("=")[1].replace("\"","")
        useragent = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) \\ Gecko/20100101 Firefox/40.1"
        submit = "Connexion";
        sessionid = re.findall(r'jsessionid=[a-zA-Z0-9]+',r.text)[0].split("=")[1]
        payload = {"username": self.username,
                "password": self.password,
                "lt"      : lt,
                "execution": execu,
                "_eventId": 'submit',
                 }
        r = self.session.post(url,data=payload,allow_redirects=True)
        if self.next == 0:
            self.dataToParsing = r.text
            Rchange = re.findall(r'<span style=\'color:black; font-size:7pt; float: right;\'>Dernière mise à jour : ([0-9/ :]*)</span>',r.text)
            new_today = datetime.datetime.today().weekday()
            if self.today == 6 and new_today == 0:
                self.today = datetime.datetime.today().weekday()
            else :
                if self.change != "" and len(Rchange)>0:
                    if self.change != Rchange[0]:
                        self.bchange = True
                        self.change = Rchange[0]
                else:
                    if len(Rchange) > 0:
                        self.change = Rchange[0]
        else :
            payload = {
                        'org.apache.myfaces.trinidad.faces.FORM':'form_week',
                        '_noJavaScript':'false',
                        'javax.faces.ViewState':'!1',
                        'form_week:_idcl':'form_week:btn_next'
                      }
            r = self.session.post("https://vtmob.uphf.fr/esup-vtclient-up4/stylesheets/desktop/welcome.xhtml",data=payload,allow_redirects=True)
            self.dataToParsing = r.text
            self.first = True
        self.today = datetime.datetime.today().weekday()

    def Parsing(self):
        print(self.dataToParsing)

        time.sleep(5)
        jours = self.dataToParsing.split('<tr class="even_row"><td class="blank_column" colspan="58">')
        i = 1
        embed = discord.Embed(
                                title="Schedule : "+self.classe,
                                colour = self.color
                             )
        while i < len(jours)-2:
            day = re.findall(r'blank_column"><b>([a-zA-Z0-9. -]+)',jours[i])
            hour = re.findall(r'(TD|TP|CM|AUTRE|RES)"><tbody><tr><td><b>([0-9:-]+)',jours[i])
            type = re.findall(r'info_bulle"><br\/><br\/><b>([A-Z0-9 ]+)',jours[i])
            cour = re.findall(r'content_bulle"><u>([a-zA-Z0-9- ()]+)',jours[i])
            location = re.findall(r"rouge'>([A-Z0-9() -]+)",jours[i])
            prof = re.findall(r"vert'>([A-Za-z ]+)",jours[i])
            embed.add_field(name=day[0],value="--------------",inline=False)
            if (len(hour)==0):
                embed.add_field(name='? no class ',value="None")
            else:
                debug = 0
                for j in range(len(hour)):
                    hour[j] = hour[j][1]
                    auxcour,debug = correction(cour,j,debug,jours[i])
                    auxtype,debug = correction(type,j,debug,jours[i])
                    auxhour,debug = correction(hour,j,debug,jours[i])
                    auxlocation,debug = correction(location,j,debug,jours[i])
                    auxprof,debug = correction(prof,j,debug,jours[i])
                    if len(hour)>= 1:
                        #print(hour[j])
                        embed.add_field(name=auxcour + " "+auxtype,value=auxhour+" "+auxlocation+" with "+auxprof,inline=False)
                        # print('# '+cour[j]+'|'+type[j]+' : '+hour[j][1]+" : "+hour[j][1] +' with :'+prof[j])


            i+=1
        return embed

def correction(elem,i,debug,jour):
    aux = ""
    try:
        if elem[i]:
            pass
        aux = elem[i]
    except:
        aux = re.findall(r'style="color:red;"><br\/>([a-zA-Z0-9-+ ]*)<\/span>',jour)
        print(aux)
        try :
            print(aux)
            print(debug)
            print(aux[debug])
            aux = aux[debug]
            debug+=1
        except:
            aux = "Undefined"
    return aux,debug
