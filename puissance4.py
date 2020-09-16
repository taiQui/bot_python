import numpy as np
import discord
from threading import RLock
import random
verrou = RLock()
class Puissance4:
    def __init__(self):
        """
            Initiate all game first time
        """
        self.itemP1 = ":small_blue_diamond:"
        self.itemP2 = ":small_orange_diamond:"
        self.P4_inGame = False
        self.P4_GamePlayer1 = 0
        self.P4_tourjoueur1 = True
        self.P4_GamePlayer2 = 0
        self.P4_gameMessage = ""
        self.P4_gameServer = ""
        self.mod = 0
        # ligne , colonne
        self.GrilleJeux = []
        for i in range(6):
            self.GrilleJeux.append([])
            for j in range(7):
                self.GrilleJeux[i].append(":black_small_square:")
    def reset(self):
        """
            Reset the game to play again
        """
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
        """
            Control if someone is legit to play
        """
        return id == self.P4_GamePlayer1 or id == self.P4_GamePlayer2

    async def init(self,id,id2,server,message,gamemod):
        """
            Init the game to play
        """
        self.reset()
        self.P4_GamePlayer1 = id
        self.P4_GamePlayer2 = id2
        self.P4_gameServer = server
        self.P4_gameMessage = message
        self.P4_tourjoueur1 = True
        self.GrilleJeux = []
        self.mod = gamemod
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
        """
            Start the game
        """
        if not self.P4_inGame:
            return
        # verrou is used to not read in same time to user input
        with verrou:
            if id == self.P4_GamePlayer1 and self.P4_tourjoueur1 and message.channel.id == self.P4_gameServer:
                if not msg.isdigit():
                    return
                if int(msg) < 1 or int(msg) > 7:
                    return
                self.play(msg,self.itemP2)
                tw = self.testwin(self.GrilleJeux)
                if tw != -1 and tw != 3:
                    await self.print(None)
                    await message.channel.send("<@"+str(self.P4_GamePlayer1)+"> WIN this match !")
                    self.P4_inGame = False
                    return
                elif tw == 3:
                    await self.print(None)
                    await message.channel.send("DRAW!")
                    self.P4_inGame = False
                    return
                self.P4_tourjoueur1 = False
            elif id == self.P4_GamePlayer2 and not self.P4_tourjoueur1 and message.channel.id == self.P4_gameServer:
                if not msg.isdigit():
                    return
                if int(msg) < 1 or int(msg) > 7:
                    return
                self.play(msg,self.itemP1)
                if self.testwin(self.GrilleJeux) != -1:
                    await self.print(None)
                    self.P4_inGame = False
                    await message.channel.send("<@"+str(self.P4_GamePlayer2)+"> WIN this match !")
                    return
                self.P4_tourjoueur1 = True
            else:
                return
            await self.print(None)
            await message.delete()
            return

    async def start_bot(self,msg,id,message):
        """
            Start the game against a bot
        """
        if not self.P4_inGame:
            return
        with verrou:
            # The user plays
            if id == self.P4_GamePlayer1 and self.P4_tourjoueur1 and message.channel.id == self.P4_gameServer:
                if not msg.isdigit():
                    return
                if int(msg) < 1 or int(msg) > 7:
                    return
                self.play(msg,self.itemP2)
                tw = self.testwin(self.GrilleJeux)
                if tw != -1 and tw != 3:
                    await self.print(None)
                    await message.channel.send("<@"+str(self.P4_GamePlayer1)+"> WIN this match !")
                    self.P4_inGame = False
                    return
                elif tw == 3:
                    await self.print(None)
                    await message.channel.send("DRAW!")
                    self.P4_inGame = False
                    return
                self.P4_tourjoueur1 = False
                # BOT PLAYS NOW
                score_tours = [0,0,0,0,0,0,0]
                for i in range(7):
                    aux = self.copy(self.GrilleJeux)
                    if self.findIndex(i,aux) == -1:
                        score_tours[i] -= 5000
                    else:
                        #test if bot win after this move or map is full
                        aux[self.findIndex(i,aux)][i] = self.itemP1
                        tw = self.testwin(aux)
                        if  tw == 2:
                            score_tours[i] += 2000
                        elif tw == 3:
                            score_tours[i] += 5000
                        aux = self.copy(self.GrilleJeux)
                        # test if user win if plays here
                        aux[self.findIndex(i,aux)][i] = self.itemP2
                        tw = self.testwin(aux)
                        if tw == 1:
                            score_tours[i] += 1000
                        aux = self.copy(self.GrilleJeux)
                        #test if you get more aligned point after this move
                        before = self.test_align_plus(aux,2)
                        aux[self.findIndex(i,aux)][i] = self.itemP1
                        after = self.test_align_plus(aux,2)
                        if after > before and after == 2:
                            score_tours[i] += 200
                        elif after > before and after == 3:
                            score_tours[i] += 300
                        aux = self.copy(self.GrilleJeux)
                        #Test if user get more aligned point after this move
                        before = self.test_align_plus(aux,1)
                        aux[self.findIndex(i,aux)][i] = self.itemP2
                        after = self.test_align_plus(aux,1)
                        if after > before and after == 2:
                            score_tours[i] += 100
                        elif after > before and after == 3:
                            score_tours[i] += 200
                        aux = self.copy(self.GrilleJeux)
                        #test if bot points next to this move
                        aux[self.findIndex(i,aux)][i] = self.itemP1
                        if self.test_align_bot(i,aux) == 1:
                            score_tours[i] += 100
                        aux = self.copy(self.GrilleJeux)
                        #test if bot plays here, if user win if plays same case
                        aux[self.findIndex(i,aux)][i] = self.itemP1
                        if self.findIndex(i,aux) != -1:
                            aux[self.findIndex(i,aux)][i] = self.itemP2
                            if self.testwin(aux) == 2:
                                score_tours[i] -= 1000
                max = 0
                score_max = 0
                for i in range(7):
                    if score_tours[i] >= score_max:
                        if score_tours[i] > score_max:
                            score_max = score_tours[i]
                            max = i
                        else:
                            if random.randrange(0,2,1):
                                score_max = score_tours[i]
                                max = i
                self.GrilleJeux[self.findIndex(max,self.GrilleJeux)][max] = self.itemP1
                self.P4_tourjoueur1 = True
                tw =  self.testwin(self.GrilleJeux)
                if tw == 2:
                    await message.channel.send("BOT win this match noob !")

            else:
                return
            await self.print(None)
            await message.delete()
            return



    def play(self,index,item):
        """
            Use to apply the move of user/bot
        """
        if index == "1":
            tmp = self.findIndex(int(index)-1,self.GrilleJeux)
            if  tmp != -1:
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
            pass
    async def print(self,message):
        """
            Print the map game
        """
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
    def copy(self,grid):
        """
            Copy the map array in anoter map array ( copy module only work for deep copy)
        """
        aux = []
        for i in range(6):
            aux.append([])
            for j in range(7):
                aux[i].append(self.GrilleJeux[i][j])
        return aux
    def findIndex(self,index,grid):
        """
            Find index with column number
            ex :    |    |    |
                    |    |    |
                    |  c |    |
                       1    2
                if you play in collumn 1 the index will be 2 because index 1 is already played
        """
        i = 5
        continuer = True
        while i >= 0 and continuer:
            if grid[i][index] == self.itemP2 or grid[i][index] == self.itemP1:
                i-=1
            else:
                continuer = False
        if continuer == True:
            return -1
        else:
            return i
    def test_align_bot(self,index,grid):
        """
            check if the bot aligned square if he plays this move
        """
        i = 5
        continuer = True
        while i >= 0 and continuer:
            if grid[i][index] == self.itemP1:
                continuer = False
            else:
                i -= 1
        if index -1 > 0 and i -1 >= 0:
            if grid[i-1][index-1] == self.itemP1:
                return 1
        if index -1 >= 0:
            if grid[i][index-1] == self.itemP1:
                return 1
        if index -1 >=0 and  i+1 <= 5:
            if grid[i+1][index-1] == self.itemP1:
                return 1
        if i+1 <= 5:
            if grid[i+1][index] == self.itemP1:
                return 1
        if i+1 <= 5 and index +1 <= 6:
            if grid[i+1][index+1] == self.itemP1:
                return 1
        if index+1 <= 6:
            if grid[i][index+1] == self.itemP1:
                return 1
        if i-1 >= 0 and index+1 <= 6:
            if grid[i-1][index+1] == self.itemP1:
                return 1
        return 0

    def test_align_plus(self,grid,player):
        """
            check if the bot has aligned more square than previous hit
        """
        max = 0
        aux_max = 0
        enemie = ""
        ally = ""
        if player == 1:
            enemie = self.itemP1
            ally = self.itemP2
        else:
            enemie = self.itemP2
            ally = self.itemP1
        # test horizontale
        for i in range(6):
            for j in range(7):
                if grid[i][j] == enemie:
                    aux_max = 0
                elif grid[i][j] == ally:
                    aux_max += 1
                else:
                    aux_max = 0
        if aux_max > max :
            max = aux_max
        aux_max = 0
        #test verticale
        for i in range(7):
            for j in range(6):
                if grid[j][i] == enemie:
                    aux_max = 0
                elif grid[j][i] == ally:
                    aux_max += 1
                else :
                    aux_max = 0
        if aux_max > max :
            max = aux_max
        aux_max = 0
        #test diag montante
        for i in range(3,6):
            for j in range(4):
                if grid[i][j] == ally:
                     aux_max +=1
                else:
                    aux_max = 0
                if grid[i-1][j+1] == ally:
                    aux_max += 1
                else:
                    aux_max = 0
                if grid[i-2][j+2] == ally:
                    aux_max += 1
                else:
                    aux_max = 0
                if grid[i-3][j+3] == ally:
                    aux_max += 1
                else:
                    aux_max = 0
        if aux_max > max :
            max = aux_max
        aux_max = 0
        #test diag desc
        for i in range(3):
            for j in range(4):
                if grid[i][j] == ally:
                    aux_max += 1
                else:
                    aux_max = 0
                if grid[i+1][j+1] == ally:
                    aux_max += 1
                else:
                    aux_max = 0
                if grid[i+2][j+2] == ally:
                    aux_max += 1
                else:
                    aux_max = 0
                if grid[i+3][j+3] == ally:
                    aux_max += 1
                else:
                    aux_max = 0
        if aux_max > max :
            max = aux_max
        return max

    def testdiagmon(self,grid):
        """
            Check if win in upper diagonal
        """
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
        """
            Check if win in down diagonnal
        """
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
        """
            Check if win horizontally
        """
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
        """
            Check if win vertically
        """
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
        """
            Check if map is full
        """
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
        """
            check all win condition
        """
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
            return 3

        return -1

if __name__ == "__main__":
    pass
