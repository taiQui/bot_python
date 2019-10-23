import numpy as np
import discord
from threading import RLock
verrou = RLock()
class Puissance4:
    def __init__(self):
        self.itemP1 = ":small_blue_diamond:"
        self.itemP2 = ":small_orange_diamond:"
        self.P4_inGame = False
        self.P4_GamePlayer1 = 0
        self.P4_tourjoueur1 = True
        self.P4_GamePlayer2 = 0
        self.P4_gameMessage = ""
        self.P4_gameServer = ""
        # ligne , colonne
        self.GrilleJeux = []
        for i in range(6):
            self.GrilleJeux.append([])
            for j in range(7):
                self.GrilleJeux[i].append(":black_small_square:")
    def reset(self):
        self.P4_inGame = False;
        self.P4_GamePlayer1 = 0
        self.P4_tourjoueur1 = True
        self.P4_GamePlayer2 = 0
        self.P4_gameMessage = ""
        self.P4_gameServer = ""
        self.GrilleJeux = []
        for i in range(6):
            self.GrilleJeux.append([])
            for j in range(7):
                self.GrilleJeux[i].append(":black_small_square:")
    def controlPlaying(self,id):
        return id == self.P4_GamePlayer1 or id == self.P4_GamePlayer2

    async def init(self,id,id2,server,message,gamemod):
        self.reset()
        self.P4_GamePlayer1 = id
        self.P4_GamePlayer2 = id2
        self.P4_gameServer = server
        self.P4_gameMessage = message
        self.P4_tourjoueur1 = True
        self.GrilleJeux = []
        for i in range(6):
            self.GrilleJeux.append([])
            for j in range(7):
                self.GrilleJeux[i].append(":black_small_square:")
        #print(self.GrilleJeux)
        # self.P4_inGame = True
        # if gamemod == 0:
        #     self.P4_inGame = True
        #     await self.start()
        # else:
        #     self.start_against_bot()
    async def start(self,msg,id,message):
        with verrou:
            print("game")
            print("text : "+msg+";")
            print(type(msg))
            if id == self.P4_GamePlayer1 and self.P4_tourjoueur1:
                if not msg.isdigit():
                    return
                if int(msg) < 1 or int(msg) > 7:
                    return
                self.play(msg,self.itemP2)
                if self.testwin(self.GrilleJeux) != -1:
                    await self.print(None)
                    await message.channel.send("WIN J1")
                    self.P4_inGame = False
                    return
                self.P4_tourjoueur1 = False
            elif id == self.P4_GamePlayer2 and not self.P4_tourjoueur1:
                if not msg.isdigit():
                    return
                if int(msg) < 1 or int(msg) > 7:
                    return
                self.play(msg,self.itemP1)
                if self.testwin(self.GrilleJeux) != -1:
                    await self.print(None)
                    self.P4_inGame = False
                    await message.channel.send("WIN J2")
                    return
                self.P4_tourjoueur1 = True
            else:
                print("3 - ")
                return
            print("You play "+msg)
            await self.print(None)
            await message.delete()
            return
    def play(self,index,item):
        if index == "1":
            print("test 1")
            tmp = self.findIndex(int(index)-1,self.GrilleJeux)
            print("tmp : "+str(tmp))
            if  tmp != -1:
                print("test 2")
                self.GrilleJeux[tmp][1-1] = item
        elif index == "2":
            if self.findIndex(int(index)-1,self.GrilleJeux) != -1:
                self.GrilleJeux[self.findIndex(int(index)-1,self.GrilleJeux)][int(index)-1] = item
        elif index == "3":
            if self.findIndex(int(index)-1,self.GrilleJeux) != -1:
                self.GrilleJeux[self.findIndex(int(index)-1,self.GrilleJeux)][int(index)-1] = item
        elif index == "4":
            if self.findIndex(int(index)-1,self.GrilleJeux) != -1:
                self.GrilleJeux[self.findIndex(int(index)-1,self.GrilleJeux)][int(index)-1] = item
        elif index == "5":
            if self.findIndex(int(index)-1,self.GrilleJeux) != -1:
                self.GrilleJeux[self.findIndex(int(index)-1,self.GrilleJeux)][int(index)-1] = item
        elif index == "6":
            if self.findIndex(int(index)-1,self.GrilleJeux) != -1:
                self.GrilleJeux[self.findIndex(int(index)-1,self.GrilleJeux)][int(index)-1] = item
        elif index == "7":
            if self.findIndex(int(index)-1,self.GrilleJeux) != -1:
                self.GrilleJeux[self.findIndex(int(index)-1,self.GrilleJeux)][int(index)-1] = item
        else:
            print("yolo")
    async def print(self,message):
        tour = ""
        if self.P4_tourjoueur1:
            tour = "Player 1 turn  ::small_orange_diamond:"
        else:
            tour = "Player 2 turn  :small_blue_diamond:"
        if self.P4_inGame:
            await self.P4_gameMessage.edit(content="|" + self.GrilleJeux[0][0] + "|" + self.GrilleJeux[0][1] + "|" + self.GrilleJeux[0][2] + "|" + self.GrilleJeux[0][3] + "|" + self.GrilleJeux[0][4] + "|" + self.GrilleJeux[0][5]+ "|" +self.GrilleJeux[0][6]+ "|\n" +
        "|" + self.GrilleJeux[1][0] + "|" + self.GrilleJeux[1][1] + "|" + self.GrilleJeux[1][2] + "|" + self.GrilleJeux[1][3] + "|" + self.GrilleJeux[1][4] + "|" + self.GrilleJeux[1][5] + "|" +self.GrilleJeux[1][6]+  "|\n" +
        "|" + self.GrilleJeux[2][0] + "|" + self.GrilleJeux[2][1] + "|" + self.GrilleJeux[2][2] + "|" + self.GrilleJeux[2][3] + "|" + self.GrilleJeux[2][4] + "|" + self.GrilleJeux[2][5] + "|" +self.GrilleJeux[2][6]+ "|\n" +
        "|" + self.GrilleJeux[3][0] + "|" + self.GrilleJeux[3][1] + "|" + self.GrilleJeux[3][2] + "|" + self.GrilleJeux[3][3] + "|" + self.GrilleJeux[3][4] + "|" + self.GrilleJeux[3][5] + "|" +self.GrilleJeux[3][6]+  "|\n" +
        "|" + self.GrilleJeux[4][0] + "|" + self.GrilleJeux[4][1] + "|" + self.GrilleJeux[4][2] + "|" + self.GrilleJeux[4][3] + "|" + self.GrilleJeux[4][4] + "|" + self.GrilleJeux[4][5] + "|" +self.GrilleJeux[4][6]+  "|\n" +
        "|" + self.GrilleJeux[5][0] + "|" + self.GrilleJeux[5][1] + "|" + self.GrilleJeux[5][2] + "|" + self.GrilleJeux[5][3] + "|" + self.GrilleJeux[5][4] + "|" + self.GrilleJeux[5][5] + "|" +self.GrilleJeux[5][6]+  "|\n" +
        "   1" + "      2" + "     3" + "     4" + "     5" + "    6" + "     7" + "\n" + tour)
        else:
            await message.channel.send("|" + self.GrilleJeux[0][0] + "|" + self.GrilleJeux[0][1] + "|" + self.GrilleJeux[0][2] + "|" + self.GrilleJeux[0][3] + "|" + self.GrilleJeux[0][4] + "|" + self.GrilleJeux[0][5]  + "|" +self.GrilleJeux[0][6]+ "|\n" +
        "|" + self.GrilleJeux[1][0] + "|" + self.GrilleJeux[1][1] + "|" + self.GrilleJeux[1][2] + "|" + self.GrilleJeux[1][3] + "|" + self.GrilleJeux[1][4] + "|" + self.GrilleJeux[1][5] + "|" +self.GrilleJeux[1][6]+  "|\n" +
        "|" + self.GrilleJeux[2][0] + "|" + self.GrilleJeux[2][1] + "|" + self.GrilleJeux[2][2] + "|" + self.GrilleJeux[2][3] + "|" + self.GrilleJeux[2][4] + "|" + self.GrilleJeux[2][5] + "|" +self.GrilleJeux[2][6]+  "|\n" +
        "|" + self.GrilleJeux[3][0] + "|" + self.GrilleJeux[3][1] + "|" + self.GrilleJeux[3][2] + "|" + self.GrilleJeux[3][3] + "|" + self.GrilleJeux[3][4] + "|" + self.GrilleJeux[3][5] + "|" +self.GrilleJeux[3][6]+  "|\n" +
        "|" + self.GrilleJeux[4][0] + "|" + self.GrilleJeux[4][1] + "|" + self.GrilleJeux[4][2] + "|" + self.GrilleJeux[4][3] + "|" + self.GrilleJeux[4][4] + "|" + self.GrilleJeux[4][5] + "|" +self.GrilleJeux[4][6]+  "|\n" +
        "|" + self.GrilleJeux[5][0] + "|" + self.GrilleJeux[5][1] + "|" + self.GrilleJeux[5][2] + "|" + self.GrilleJeux[5][3] + "|" + self.GrilleJeux[5][4] + "|" + self.GrilleJeux[5][5] + "|" +self.GrilleJeux[5][6]+  "|\n" +
        "   1" + "      2" + "     3" + "     4" + "     5" + "    6" + "     7" + "\n" + tour);
            self.P4_gameMessage = message.channel.last_message
            self.P4_inGame = True
    def findIndex(self,index,grid):
        i = 5
        continuer = True
        while i >= 0 and continuer:
            if grid[i][index] == self.itemP2 or grid[i][index] == self.itemP1:
                i-=1
            else:
                continuer = False
        print("index : "+str(i)+"\ncontinuer : "+str(continuer))
        if continuer == True:
            return -1
        else:
            return i
    def testdiagmon(self,grid):
        for i in range(3,6):
            for j in range(4):
                if (grid[i][j] == self.itemP2 and grid[i - 1][j + 1] == self.itemP2 and grid[i - 2][j + 2] == self.itemP2 and grid[i - 3][j + 3] == self.itemP2):
                    grid[i][j] = ":small_red_triangle:";
                    grid[i - 1][j + 1] = ":small_red_triangle:";
                    grid[i - 2][j + 2] = ":small_red_triangle:";
                    grid[i - 3][j + 3] = ":small_red_triangle:";
                    return 1
                elif grid[i][j] == self.itemP1 and grid[i - 1][j + 1] == self.itemP1 and grid[i - 2][j + 2] == self.itemP1 and grid[i - 3][j + 3] == self.itemP1:
                    grid[i][j] = ":small_red_triangle:";
                    grid[i-1][j+1] =":small_red_triangle:";
                    grid[i-2][j+2] = ":small_red_triangle:";
                    grid[i-3][j+3] = ":small_red_triangle:";
                    return 2
        return -1
    def testdiagdes(self,grid):
        for i in range(3):
            for j in range(4):
                if (grid[i][j] == self.itemP2 and grid[i + 1][j + 1] == self.itemP2 and grid[i + 2][j + 2] == self.itemP2 and grid[i + 3][j + 3] == self.itemP2):
                      grid[i][j] = ":small_red_triangle:"
                      grid[i + 1][j + 1] = ":small_red_triangle:"
                      grid[i + 2][j + 2] = ":small_red_triangle:"
                      grid[i + 3][j + 3] = ":small_red_triangle:"
                      return 1;
                elif (grid[i][j] == self.itemP1 and grid[i + 1][j + 1] == self.itemP1 and grid[i + 2][j + 2] == self.itemP1 and grid[i + 3][j + 3] == self.itemP1):
                      grid[i][j] = "small_red_triangle:"
                      grid[i + 1][j + 1] = ":small_red_triangle:"
                      grid[i + 2][j + 2] = ":small_red_triangle:"
                      grid[i + 3][j + 3] = ":small_red_triangle:"
                      return 2;
        return -1;
    def testHorizontale(self,grid):
        countJ1 = 0
        countJ2 = 0
        for i in range(6):
            for j in range(7):
                if (grid[i][j] == self.itemP2):
                    countJ1+= 1
                    countJ2 = 0
                elif (grid[i][j] == self.itemP1):
                    countJ2+= 1
                    countJ1 = 0
                else:
                    countJ1 = 0
                    countJ2 = 0

                if (countJ1 == 4):
                    #console.log("gagner : " + grid[i][j] + " " + grid[i][j - 1] + " " + grid[i][j - 2] + " " + grid[i][j - 3]);
                    grid[i][j] = ":small_red_triangle:"
                    grid[i][j - 1] = ":small_red_triangle:"
                    grid[i][j - 2] = ":small_red_triangle:"
                    grid[i][j - 3] = ":small_red_triangle:"
                    return 1
                elif (countJ2 == 4):
                    #console.log("gagner : " + grid[i][j] + " " + grid[i][j - 1] + " " + grid[i][j - 2] + " " + grid[i][j - 3]);
                    grid[i][j] = ":small_red_triangle:"
                    grid[i][j - 1] = ":small_red_triangle:"
                    grid[i][j - 2] = ":small_red_triangle:"
                    grid[i][j - 3] = ":small_red_triangle:"
                    return 2

            countJ1 = 0
            countJ2 = 0
        return -1
    def testVertical(self,grid):
        countJ1 = 0
        countJ2 = 0
        i = 0
        continuer = True
        j = 0
        for i in range(7):
            for j in range(6):
                if (grid[j][i] == self.itemP2):
                    countJ1+= 1
                    countJ2 = 0
                elif (grid[j][i] == self.itemP1):
                    countJ2+= 1
                    countJ1 = 0
                else:
                    countJ1 = 0
                    countJ2 = 0

                if (countJ1 >= 4):
                    grid[j][i] = ":small_red_triangle:"
                    grid[j - 1][i] = ":small_red_triangle:"
                    grid[j - 2][i] = ":small_red_triangle:"
                    grid[j - 3][i] = ":small_red_triangle:"
                    return 1
                elif (countJ2 >= 4):
                    grid[j][i] = ":small_red_triangle:"
                    grid[j - 1][i] = ":small_red_triangle:"
                    grid[j - 2][i] = ":small_red_triangle:"
                    grid[j - 3][i] = ":small_red_triangle:"
                    return 2


            countJ1 = 0;
            countJ2 = 0;

        return -1;
    def Full(self,grid):
        continuer = True
        i = 0
        j = 0
        while ((i < 6) and continuer):
            while (j < 7 and continuer):
                if (grid[i][j] != self.itemP2 and grid[i][j] != self.itemP1):
                    continuer = False
                else:
                    j+= 1

            i+= 1

        return continuer
    def testwin(self,grid):
        aux = self.testdiagmon(grid)
        if aux != -1 :
            return aux
        aux = self.testdiagdes(grid)
        if aux != -1:
            return aux
        aux = self.testHorizontale(grid)
        if aux != -1:
            return aux
        aux = self.testVertical(grid)
        if aux != -1:
            return aux
        aux = self.Full(grid)
        if aux != False:
            return 1

        return -1

def check(self,msg):
    return msg.channel == smsg.P4_gameServer and self.controlPlaying(msg.id)
if __name__ == "__main__":
    print("a")
