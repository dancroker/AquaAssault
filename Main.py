#Battleships
#single player
#------------------------------------------
import pygame
import random
import requests
import os
import threading
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

class BattleshipGrid:
  def __init__(self): #Creates a Board with 10 rows and 10 columns
    self.BattleshipBoard= []
    self.BattleshipHealth= []
    self.BattleshipShots= []
    self.BattleshipHits= []
    for _ in range(10):
      self.BattleshipBoard.append(["+"] * 10)
  def RandomRow(self):
    return random.randint(0, len(self.BattleshipBoard) - 1)
  def RandomCol(self):
    return random.randint(0, len(self.BattleshipBoard[0]) - 1)

class Boats:
  def PlaceBoat(self, Row=None, Col=None, Orien=None, Size=None, Auto=True):
    unplaced = True
    if Size is None:
      Size = self.ships[0]
    print(Size)
    if Size < 5 or Size > 2:
      self.ships.pop(0)
    if Size == 2:
      boatshape = "2"
    if Size == 3:
      boatshape = "3"
    if Size == 4:
      boatshape = "4"
    if Size == 5:
      boatshape = "5"
    while unplaced:
      if Row is None or Row > 9: #for test only (remove and add renter value)
        Row = random.randint(0, len(self.BattleshipBoard) - 1)
      if Col is None or Col > 9: #for test only (remove and add renter value)
        Col = random.randint(0, len(self.BattleshipBoard[0]) - 1)
      if Orien is None or Orien > 1: #for test only (remove and add renter value)
        Orien = random.randint(0, 1)  # 0 = horizontal, 1 = vertical
      valid_placement = True
      if Orien == 0 and Col + Size <= len(self.BattleshipBoard[0]):  # horizontal
        for i in range(Size):
          if [Row, Col + i] in self.BattleshipHealth:
            valid_placement = False
            break
        if valid_placement:
          for i in range(Size):
            self.BattleshipBoard[Row][Col + i] = boatshape
            self.BattleshipHealth.append([Row, Col + i])  # Adds boat locations to list
            if Size == 2:
              self.Cruiser.append([Row, Col + i])
            if Size == 3:
              if len(self.Submarine) < 3:
                self.Submarine.append([Row, Col + i])
              else:
                self.Battleship.append([Row, Col + i])
            if Size == 4:
              self.Destroyer.append([Row, Col + i])
            if Size == 5:
              self.AircraftCarrier.append([Row, Col + i])
          unplaced = False

      elif Orien == 1 and Row + Size <= len(self.BattleshipBoard):  # vertical
        for i in range(Size):
          if [Row + i, Col] in self.BattleshipHealth:
            valid_placement = False
            break
        if valid_placement:
          for i in range(Size):
            self.BattleshipBoard[Row + i][Col] = boatshape
            self.BattleshipHealth.append([Row + i, Col])  # Adds boat locations to list
            if Size == 2:
              self.Cruiser.append([Row + i, Col])
            if Size == 3:
              if len(self.Submarine) < 3:
                self.Submarine.append([Row + i, Col])
              else:
                self.Battleship.append([Row + i, Col])
            if Size == 4:
              self.Destroyer.append([Row + i, Col])
            if Size == 5:
              self.AircraftCarrier.append([Row + i, Col])
          unplaced = False

      if unplaced:
        if Auto:# If the placement is not valid, choose new random coordinates and orientation
          Row = random.randint(0, len(self.BattleshipBoard) - 1)
          Col = random.randint(0, len(self.BattleshipBoard[0]) - 1)
        else:
          print("No...bad!...")
          self.ships.insert(0,Size)
          break
#-------------------------------------------
matrix = [[0 for col in range(10)] for row in range(10)]
for x in range(10):
  print(matrix[x])
def shotDefeatDisplayColourction(matrix):
    matrix_size = len(matrix)
   
    # Initialize matrix with zeros where there are no ships or misses
    for x in range(matrix_size):
        for y in range(matrix_size):
            if matrix[x][y] != "#" and matrix[x][y] != "=":
                matrix[x][y] = 0

    # Helper function to update distances from a ship
    def update_distances(center_x, center_y):
        for i in range(matrix_size):
            for j in range(matrix_size):
                if matrix[i][j] not in ["#", "="]:
                    distance = abs(center_x - i) + abs(center_y - j)
                    if distance > 0:
                        matrix[i][j] += matrix_size // distance

    # Assign values based on distance to the nearest ship
    for x in range(matrix_size):
        for y in range(matrix_size):
            if matrix[x][y] == "#":
                update_distances(x, y)

    # Helper function to check ship orientation and apply biases
    def apply_bias(x, y, orientation):
        bias = matrix_size * 10  # Heavy bias for detected ship
        if orientation == 'H':
            # Increase priority in the row of the hit only
            for ny in range(matrix_size):
                if ny != y and matrix[x][ny] == ["="]:
                   break
                elif ny != y and matrix[x][ny] not in ["#", "="]:
                    matrix[x][ny] += bias
        elif orientation == 'V':
            # Increase priority in the column of the hit only
            for nx in range(matrix_size):
                if nx != x and matrix[nx][y] == ["="]:
                   break
                elif nx != x and matrix[nx][y] not in ["#", "="]:
                    matrix[nx][y] += bias

    # Helper function to check ship orientation
    def check_orientation(x, y):
        vertical = (x > 0 and matrix[x - 1][y] == "HIT") or (x < matrix_size - 1 and matrix[x + 1][y] == "HIT")
        horizontal = (y > 0 and matrix[x][y - 1] == "HIT") or (y < matrix_size - 1 and matrix[x][y + 1] == "HIT")
        if vertical:
            return 'V'
        if horizontal:
            return 'H'
        return None

    # Increase scores based on hit orientations and apply bias
    for x in range(matrix_size):
        for y in range(matrix_size):
            if matrix[x][y] == "HIT":
                orientation = check_orientation(x, y)
                if orientation:
                    apply_bias(x, y, orientation)

    # Handle cells around connected hits or found ships
    for x in range(matrix_size):
        for y in range(matrix_size):
            if matrix[x][y] == "#":
                # Apply a bias to cells in the same row and column
                for dy in range(matrix_size):
                    if dy != y and matrix[x][dy] not in ["#", "="]:
                        matrix[x][dy] += 10#1
                for dx in range(matrix_size):
                    if dx != x and matrix[dx][y] not in ["#", "="]:
                        matrix[dx][y] += 10#1

    # Ensure non-negative values
    for x in range(matrix_size):
        for y in range(matrix_size):
            if isinstance(matrix[x][y], int) and matrix[x][y] < 0:
                matrix[x][y] = 0

    return matrix

#-------------------------------------------
class Player(BattleshipGrid, Boats):
  def __init__(self):
    super().__init__()
    self.ships = [2,3,3,4,5]
    self.Cruiser = []
    self.Submarine = []
    self.Battleship = []
    self.Destroyer = []
    self.AircraftCarrier = []
    self.CruiserDamage = []
    self.SubmarineDamage = []
    self.BattleshipDamage = []
    self.DestroyerDamage = []
    self.AircraftCarrierDamage = []
    self.EmptySpace = 0
    self.Ammo = 0
    #--------------------------- GameOverScreenVairables: Need to code to track!
    self.FirstStrike = 0 #set by gamehits+gamemiss when gamehits == 1
    self.MaxShotStreak = 0 #when current > max, set max to current else, well dont! :)
    self.CurrentShotStreak = 0
    self.GameHits = 0
    self.GameMiss = 0

  def reset(self,username=None):
        # Manually re-run the __init__ method
        self.__init__(username)
   
  def auto_board_set_up(self,BoatCount = None):
    if BoatCount == None:
      BoatCount = 5
    for i in range(BoatCount):
      self.PlaceBoat(None,None,None,None)
  def manual_board_set_up(self):
    x = int(input("x: "))
    y = int(input("y: "))
    o = int(input("o: "))
    s = int(input("s: "))
    self.PlaceBoat(x,y,o,s)
  def taking_attack(self, row, col):
    if [row, col] in self.BattleshipHealth:
      self.BattleshipBoard[row][col] = "#"  # shot hit location is marked '#'
      self.BattleshipHits.append([row,col])
      music_manager.play_soundEffect("SE_Hit")
      if self == Human:
        matrix[row][col] = "#"
        shotDefeatDisplayColourction(matrix)
      if [row,col] in self.Cruiser:
        self.Cruiser.remove([row,col])
        self.CruiserDamage.append([row,col])
      if [row,col] in self.Submarine:
        self.Submarine.remove([row,col])
        self.SubmarineDamage.append([row,col])
      elif [row,col] in self.Battleship:
        self.Battleship.remove([row,col])
        self.BattleshipDamage.append([row,col])
      elif [row,col] in self.Destroyer:
        self.Destroyer.remove([row,col])
        self.DestroyerDamage.append([row,col])
      elif [row,col] in self.AircraftCarrier:
        self.AircraftCarrier.remove([row,col])
        self.AircraftCarrierDamage.append([row,col])
      if len(self.Cruiser) == 0:
        print("Cruiser Sunk")
        self.Cruiser.append("Sunk")
        self.PrintFullBoard()
        return(col,row,"SINK")
      if len(self.Submarine) == 0:
        print("Submarine Sunk")
        self.Submarine.append("Sunk")
        self.PrintFullBoard()
        return(col,row,"SINK")
      if len(self.Battleship) == 0:
        print("Battleship Sunk")
        self.Battleship.append("Sunk")
        self.PrintFullBoard()
        return(col,row,"SINK")
      if len(self.Destroyer) == 0:
        print("Destroyer Sunk")
        self.Destroyer.append("Sunk")
        self.PrintFullBoard()
        return(col,row,"SINK")
      if len(self.AircraftCarrier) == 0:
        print("Aircraft Carrier Sunk")
        self.AircraftCarrier.append("Sunk")
        self.PrintFullBoard()
        return(col,row,"SINK")
      shotDefeatDisplayColourction(matrix)
      col = chr(65+col)
      row += 1
      return(col,row,"HIT")
    else:
      self.BattleshipBoard[row][col] = "="  # shot miss location is marked '='
      self.BattleshipShots.append([row,col])
      music_manager.play_soundEffect("SE_Miss")
      if self == Human:
        matrix[row][col] = "="
        shotDefeatDisplayColourction(matrix)
      col = chr(65+col)
      row += 1
      return(col,row,"Miss")
  def printeachboattype(self):
    print(f"""Cruiser: {self.Cruiser}
Submarine: {self.Submarine}
Battleship: {self.Battleship}
Destroyer: {self.Destroyer}
Aircraft Carrier: {self.AircraftCarrier}""")
  def fetch_username(self):
    try:
      validusername = False
      while validusername == False:
        data = requests.get(url='https://randomuser.me/api/', params={'login': 'username'},verify = False).json() #,verify = False (maybe-more to write about)
        self.username = data['results'][0]['login']['username']
        if len(self.username) <= 14:
           validusername = True
    except (requests.RequestException, ValueError, KeyError):
      self.username = "API Request Fail"
  def lastGames(self,games=None):
    if games == None:
      return [random.randint(0,1),random.randint(0,1),random.randint(0,1),random.randint(0,1),random.randint(0,1)]
    else:
      return games
   
class RealPlayer(Player):
  def __init__(self,username=None):
    super().__init__()  # Call the constructor of the parent class (Player)
    self.FogCentreLocation = None
    self.username = "Player 1"
    self.SignedIn = False
    self.password = "None"
  def reset(self):
    super().__init__()  # Call the constructor of the parent class (Player)
    self.FogCentreLocation = None
    #self.username = "Player 1"
    #self.SignedIn = False
    #self.password = "None"
  def PrintFullBoard(self):
    print(f"{self.username}'s Board:")
    print("   A B C D E F G H I J")
    countrow = 1
    for row in self.BattleshipBoard:
      if countrow == 10:
        print(str(countrow) + " " +" ".join(row))
      else:
        print(str(countrow) + "  " +" ".join(row))
      countrow = countrow + 1
    print("----------------------")
  def boatPresent(self):
    for row in self.BattleshipHealth:
      x = 68+ (row[1]*15)
      y = 422.5 + (row[0]*15)
      pygame.draw.circle(SCREEN,GREEN,(x,y),3)
  def shotPresent(self):
    SemiDarkColour = max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)
    def miss():
      x = 60+ (row[1]*15)
      y = 416+ (row[0]*15)
      pygame.draw.rect(SCREEN, SemiDarkColour, (x,y, 14, 13),0,0,0)
      pygame.draw.rect(SCREEN, DARKGREEN, (x,y+3,14,7), 0)
      pygame.draw.rect(SCREEN, DARKGREEN, (x+4,y,7,14), 0)
    def hit():
      x = 60 + (row[1]*15)
      y = 416+ (row[0]*15)
      pygame.draw.rect(SCREEN, SemiDarkColour, (x,y, 14, 13),0,0,0)
      pygame.draw.rect(SCREEN, DARKGREEN, (x,y+3,14,7), 0)
      pygame.draw.rect(SCREEN, DARKGREEN, (x+4,y,7,14), 0)
      pygame.draw.circle(SCREEN,GREEN,(68+ (row[1]*15),422.5 + (row[0]*15)),3)
    def destroy(ship):
      for row in (ship):
        x = 60 + (row[1]*15)
        y = 416+ (row[0]*15)
        pygame.draw.rect(SCREEN, DARKGREEN, (x,y, 14, 13),0,0,0)
        pygame.draw.rect(SCREEN, GREEN, (x,y+3,14,7), 0)
        pygame.draw.rect(SCREEN, GREEN, (x+4,y,7,14), 0)
        pygame.draw.circle(SCREEN,GREEN,(68+ (row[1]*15),422 + (row[0]*15)),3)
    for row in self.BattleshipShots:
      miss()
    for row in self.BattleshipHits:
     hit()
    if len(self.CruiserDamage) == 2:
      destroy(self.CruiserDamage)
      for x, y in self.CruiserDamage:
        matrix[x][y] = "="
    if len(self.SubmarineDamage) == 3:
      destroy(self.SubmarineDamage)
      for x, y in self.SubmarineDamage:
        matrix[x][y] = "="
    if len(self.BattleshipDamage) == 3:
      destroy(self.BattleshipDamage)
      for x, y in self.BattleshipDamage:
        matrix[x][y] = "="
    if len(self.DestroyerDamage) == 4:
      destroy(self.DestroyerDamage)
      for x, y in self.DestroyerDamage:
        matrix[x][y] = "="
    if len(self.AircraftCarrierDamage) == 5:
      destroy(self.AircraftCarrierDamage)
      for x, y in self.AircraftCarrierDamage:
        matrix[x][y] = "="


class AIPlayer(Player):
  def __init__(self,username=None):
    super().__init__()  # Call the constructor of the parent class (Player)
    self.shot = [0,0]
    if username == None:
      self.fetch_username()  # Fetch AI username from an API
    else:
      self.username = username
  def PrintFullBoard(self):
    print(f"{self.username}'s Board:")
    print("   A B C D E F G H I J")
    countrow = 1
    for row in self.BattleshipBoard:
      if countrow == 10:
        print(str(countrow) + " " +" ".join(row))
      else:
        print(str(countrow) + "  " +" ".join(row))
      countrow = countrow + 1
    print("----------------------")
   
  def boatPresent(self):
    for row in self.BattleshipHealth:
      x = 81 + (row[0]*33)
      y = 76 + (row[1]*33)
      pygame.draw.circle(SCREEN,GREEN,(y,x),6)
  def shotPresent(self):
    SemiDarkColour = max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)
    VeryBrightColour = [0,0,0]
    for rgbValue in range(0,3):
      if GREEN[rgbValue] != 0:
        VeryBrightColour[rgbValue] = 255
    def miss():
      pygame.draw.rect(SCREEN, SemiDarkColour, (60 + (row[1]*33),65+(row[0]*33), 33, 33),0,0,0)
      pygame.draw.rect(SCREEN, DARKGREEN, (61+(row[1]*33),77+(row[0]*33),31,10), 0)
      pygame.draw.rect(SCREEN, DARKGREEN, (71+(row[1]*33),66+(row[0]*33),10,31), 0)
      pygame.draw.circle(SCREEN,DARKGREEN,(76.8+(row[1]*33),82+(row[0]*33)),12)
    def hit():
      pygame.draw.rect(SCREEN, SemiDarkColour, (60 + (row[1]*33),65+(row[0]*33), 33, 33),0,0,0)
      pygame.draw.rect(SCREEN, DARKGREEN, (61+(row[1]*33),77+(row[0]*33),31,10), 0)
      pygame.draw.rect(SCREEN, DARKGREEN, (71+(row[1]*33),66+(row[0]*33),10,31), 0)
      pygame.draw.circle(SCREEN,DARKGREEN,(76.8+(row[1]*33),82+(row[0]*33)),12)
      pygame.draw.circle(SCREEN,VeryBrightColour,(76+(row[1]*33),82+(row[0]*33)),6)
    def destroy(ship):
      for row in (ship):
        pygame.draw.rect(SCREEN, SemiDarkColour, (60 + (row[1]*33),65+(row[0]*33), 33, 33),0,0,0)
        pygame.draw.rect(SCREEN, GREEN, (61+(row[1]*33),77+(row[0]*33),31,10), 0)
        pygame.draw.rect(SCREEN, GREEN, (71+(row[1]*33),66+(row[0]*33),10,31), 0)
        pygame.draw.circle(SCREEN,GREEN,(76.8+(row[1]*33),82+(row[0]*33)),12)
        pygame.draw.circle(SCREEN,VeryBrightColour,(76+(row[1]*33),82+(row[0]*33)),6)

    for row in self.BattleshipShots:
      miss()
    for row in self.BattleshipHits:
      hit()
    if len(self.CruiserDamage) == 2:
      destroy(self.CruiserDamage)
    if len(self.SubmarineDamage) == 3:
      destroy(self.SubmarineDamage)
    if len(self.BattleshipDamage) == 3:
      destroy(self.BattleshipDamage)
    if len(self.DestroyerDamage) == 4:
      destroy(self.DestroyerDamage)
    if len(self.AircraftCarrierDamage) == 5:
      destroy(self.AircraftCarrierDamage)
#-------------------

#-------------------
Human = RealPlayer()
Human.PrintFullBoard()
Enemy = AIPlayer()
Enemy.auto_board_set_up()
Enemy.PrintFullBoard()
Enemy.printeachboattype()
#------------------------------
def Shot(x,y):
    #global opponentround
    if len(Enemy.BattleshipHits) != len(Enemy.BattleshipHealth):
      coord1 = x-1
      coord2 = y-1
      if [coord1, coord2] in Enemy.BattleshipShots or [coord1, coord2] in Enemy.BattleshipHits:
        print("Invalid Shot")
        return False
      playerround = Enemy.taking_attack(coord1,coord2)
      if playerround[2] == "Miss":
         Human.GameMiss +=1
         Human.CurrentShotStreak = 0
      elif playerround[2] == "HIT" or playerround[2] == "SINK":
        Human.GameHits += 1
        Human.CurrentShotStreak += 1
        if Human.GameHits == 1:
          Human.FirstStrike = Human.GameHits + Human.GameMiss
        if Human.CurrentShotStreak > Human.MaxShotStreak:
           Human.MaxShotStreak = Human.CurrentShotStreak
       
      if len(GameVairables.loggedplayer) >= 4:
        GameVairables.loggedplayer.pop()
      GameVairables.loggedplayer.insert(0,playerround)
      print(f"Player:{GameVairables.loggedplayer}")
      return True
   
    #----------------------------------------------------------------------------------------------------------------------------------
def ComputerPlayerShot(DefeatDisplayColourct=True):
    #pygame.time.wait(random.randint(1,4000)) IDK if this is actually a good idea? Needs testing and feedback!
    coord1 = 0
    coord2 = 0
    if len(Human.BattleshipHits) != len(Human.BattleshipHealth) or [coord1, coord2] in Enemy.BattleshipShots:
        valid_shot = False
        while not valid_shot:
                possableshots = []
                highest = [0, 0, 0]  # [value, x, y]
                for x in range(10):
                  for y in range(10):
                    if matrix[x][y] != '#' and matrix[x][y] != '=':
                      possableshots.append([int(matrix[x][y]), x, y])
                if possableshots:
                    if DefeatDisplayColourct:
                      possableshots.sort(key=lambda item: item[0], reverse=True)
                    else:
                       possableshots.sort(key=lambda item: item[0], reverse=False)
                    if possableshots[0][0] == 0:
                      random.shuffle(possableshots)
                    highest = possableshots[0]  # Get the first item
                    # Extract x and y from the highest value shot
                    z, x, y = highest  # Unpack the sublist
                    # Set the highest shot coordinates to Enemy.shot
                    Enemy.shot = [x, y]  # [x, y]
                    coord1 = x
                    coord2 = y
                print(possableshots)
                # Call the taking_attack method with the DefeatDisplayColourcted coordinates as arguments
                opponentround = Human.taking_attack(coord1, coord2)
                GameVairables.loggedOpponent.insert(0,opponentround)
                if opponentround[2] == "Miss":
                  Enemy.GameMiss +=1
                  Enemy.CurrentShotStreak = 0
                elif opponentround[2] == "HIT" or opponentround[2] == "SINK":
                  Enemy.GameHits += 1
                  Enemy.CurrentShotStreak += 1
                  if Enemy.GameHits == 1:
                    Enemy.FirstStrike = Enemy.GameHits + Enemy.GameMiss
                  if Enemy.CurrentShotStreak > Enemy.MaxShotStreak:
                    Enemy.MaxShotStreak = Enemy.CurrentShotStreak
                Human.BattleshipShots.insert(0,Enemy.shot)
                #if DefeatDisplayColourct == True:
                shotDefeatDisplayColourction(matrix)
                #-----------------------------------------------------------------------------------------------------------------------
                valid_shot = True  # Exit the loop if the shot is valid
                Human.printeachboattype()
                Enemy.printeachboattype()


#--------------------------------------------------------
pygame.init()
pygame.font.init()
pygame.display.set_caption(' Battleship')
 
#GREEN = (0,0,0)
GRAY = (128,128,128)
DARKGRAY = (100,100,100)
WHITE = (200, 200, 200)
GREEN = (0, 200, 0)
DARKGREEN = (0,50,0)
WINDOW_HEIGHT = 300
WINDOW_WIDTH = 300
SCREEN = pygame.display.set_mode((WINDOW_WIDTH*2, WINDOW_HEIGHT*2))#pygame.NOFRAME - removes top bar
clock = pygame.time.Clock()
#GameVairables.running = True

def pygametext(letter,x,y,size,colour):
  my_font = pygame.font.SysFont('Sixtyfour', size)
  text_SCREEN = my_font.render(letter, False, (colour))
  SCREEN.blit(text_SCREEN, (x,y))

#---------------------------------------------------------
def drawText():
  letters = [chr(i) for i in range(ord('A'), ord('J')+1)]
  numbers = [chr(i) for i in range(ord('1'), ord('9')+2)]
  for char in range(0,len(letters)): #Big board letters
    if letters[char] == "I":
      pygametext(letters[char],(73+(33*char)),45,30,GREEN)
    else:  
      pygametext(letters[char],(69+(33*char)),45,30,GREEN)
  for num in range(0,len(numbers)): #Big board numbers
    if numbers[num] == ":":
      pygametext("10",34,71+(33*num),30,GREEN)
    else:  
      pygametext(numbers[num],40,71+(33*num),30,GREEN)
  for char in range(0,len(letters)): #Small board letters
    if letters[char] == "I":
      pygametext("I",(65+(15*char)),400,20,GREEN)
    else:  
      pygametext(letters[char],(62+(15*char)),400,20,GREEN)
  for num in range(0,len(numbers)): #Small board numbers
    if numbers[num] == ":":
      pygametext("10",42,415+(15*num),21,GREEN)
    else:  
      pygametext(numbers[num],45,415+(15*num),21,GREEN)
#--------------------------------------------------------
def drawGrid(size,xadd,yadd,window):
  blockSize = size #Set the size of the grid block
  for x in range(0, WINDOW_WIDTH//window, blockSize):
      for y in range(0, WINDOW_HEIGHT//window, blockSize):
          rect = pygame.Rect(x+xadd, y+yadd, blockSize, blockSize)
          pygame.draw.rect(SCREEN, GREEN, rect, 1)

def drawTargets():
  pygame.draw.rect(SCREEN, DARKGREEN, (395, 231, 160, 4),0,0,0)
  pygame.draw.rect(SCREEN, DARKGREEN, (465, 231, 100, 30),0,0,0)
  SemiDarkColour = max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)
  if Enemy.Cruiser[0] != "Sunk":
    pygame.draw.rect(SCREEN, GREEN, (400, 235, 64, 32),0,0,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417,251),12,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417+29,251),12,0) #2
  else:
    pygame.draw.rect(SCREEN, SemiDarkColour, (400, 235, 64, 32),4,0,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417,251),12,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417+29,251),12,0) #2
  if Enemy.Submarine[0] != "Sunk":
    pygame.draw.rect(SCREEN, GREEN, (400, 270, 96, 32),0,0,0) #3
    pygame.draw.circle(SCREEN,DARKGREEN,(417,286),12,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417+29,286),12,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417+58,286),12,0)
  else:
    pygame.draw.rect(SCREEN, SemiDarkColour, (400, 270, 96, 32),4,0,0) #3
    pygame.draw.circle(SCREEN,SemiDarkColour,(417,286),12,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417+29,286),12,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417+58,286),12,0)
  if Enemy.Battleship[0] != "Sunk":
    pygame.draw.rect(SCREEN, GREEN, (400, 305, 96, 32),0,0,0) #3
    pygame.draw.circle(SCREEN,DARKGREEN,(417,321),12,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417+29,321),12,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417+58,321),12,0)
  else:
    pygame.draw.rect(SCREEN, SemiDarkColour, (400, 305, 96, 32),4,0,0) #3
    pygame.draw.circle(SCREEN,SemiDarkColour,(417,321),12,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417+29,321),12,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417+58,321),12,0)
  if Enemy.Destroyer[0] != "Sunk":
    pygame.draw.rect(SCREEN, GREEN, (400, 340, 125, 32),0,0,0) #4
    pygame.draw.circle(SCREEN,DARKGREEN,(417,356),12,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417+29,356),12,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417+58,356),12,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417+87,356),12,0)
  else:
    pygame.draw.rect(SCREEN, SemiDarkColour, (400, 340, 125, 32),4,0,0) #4
    pygame.draw.circle(SCREEN,SemiDarkColour,(417,356),12,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417+29,356),12,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417+58,356),12,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417+87,356),12,0)
  if Enemy.AircraftCarrier[0] != "Sunk":
    pygame.draw.rect(SCREEN, GREEN, (400, 375, 155, 32),0,0,0) #5
    pygame.draw.circle(SCREEN,DARKGREEN,(417,375+16),12,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417+29,375+16),12,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417+58,375+16),12,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417+87,375+16),12,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(417+116,375+16),12,0)
  else:
    pygame.draw.rect(SCREEN, SemiDarkColour, (400, 375, 155, 32),4,0,0) #5
    pygame.draw.circle(SCREEN,SemiDarkColour,(417,375+16),12,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417+29,375+16),12,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417+58,375+16),12,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417+87,375+16),12,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(417+116,375+16),12,0)
def drawFleet():
  SemiDarkColour = max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)
  if Human.Cruiser[0] != "Sunk":
    pygame.draw.rect(SCREEN, GREEN, (214, 470, 32, 16),0,0,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222,478),6,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222+15,478),6,0) #2
  else:
    pygame.draw.rect(SCREEN, SemiDarkColour, (214, 470, 32, 16),4,0,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223,478),4,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223+14,478),4,0) #2
  if Human.Submarine[0] != "Sunk":
    pygame.draw.rect(SCREEN, GREEN, (214, 490, 48, 16),0,0,0) #3
    pygame.draw.circle(SCREEN,DARKGREEN,(222,498),6,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222+15,498),6,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222+30,498),6,0)
  else:
    pygame.draw.rect(SCREEN, SemiDarkColour, (214, 490, 48, 16),4,0,0) #3
    pygame.draw.circle(SCREEN,SemiDarkColour,(223,498),4,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223+15,498),4,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223+30,498),4,0)
  if Human.Battleship[0] != "Sunk":
    pygame.draw.rect(SCREEN, GREEN, (214, 510, 48, 16),0,0,0) #3
    pygame.draw.circle(SCREEN,DARKGREEN,(222,518),6,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222+15,518),6,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222+30,518),6,0)
  else:
    pygame.draw.rect(SCREEN, SemiDarkColour, (214, 510, 48, 16),4,0,0) #3
    pygame.draw.circle(SCREEN,SemiDarkColour,(223,518),4,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223+15,518),4,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223+30,518),4,0)
  if Human.Destroyer[0] != "Sunk":
    pygame.draw.rect(SCREEN, GREEN, (214, 530, 62.5, 16),0,0,0) #4
    pygame.draw.circle(SCREEN,DARKGREEN,(222,538),6,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222+15,538),6,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222+30,538),6,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222+45,538),6,0)
  else:
    pygame.draw.rect(SCREEN, SemiDarkColour, (214, 530, 62.5, 16),4,0,0) #4
    pygame.draw.circle(SCREEN,SemiDarkColour,(223,538),4,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223+15,538),4,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223+30,538),4,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223+45,538),4,0)
  if Human.AircraftCarrier[0] != "Sunk":
    pygame.draw.rect(SCREEN, GREEN, (214, 550, 77.5, 16),0,0,0) #5
    pygame.draw.circle(SCREEN,DARKGREEN,(222,558),6,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222+15,558),6,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222+30,558),6,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222+45,558),6,0)
    pygame.draw.circle(SCREEN,DARKGREEN,(222+60,558),6,0)
  else:
    pygame.draw.rect(SCREEN, SemiDarkColour, (214, 550, 77.5, 16),4,0,0) #5
    pygame.draw.circle(SCREEN,SemiDarkColour,(223,558),4,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223+15,558),4,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223+30,558),4,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223+45,558),4,0)
    pygame.draw.circle(SCREEN,SemiDarkColour,(223+60,558),4,0)

def battlelog(fade,Delay=True):
  pygame.draw.rect(SCREEN, GREEN, (395, 65, 160, 166),5,0,0)
  pygame.draw.rect(SCREEN, DARKGREEN, (400, 70, 150, 156),0,0,0)
  try:
    if len(GameVairables.loggedplayer) > 3:
      pygametext(f"You ({GameVairables.loggedplayer[3][0]},{GameVairables.loggedplayer[3][1]})-{GameVairables.loggedplayer[3][2]}",411-10,199,30,GREEN)
      pygametext(f"Cpu ({GameVairables.loggedOpponent[3][0]},{GameVairables.loggedOpponent[3][1]})-{GameVairables.loggedOpponent[3][2]}",411-10,219,30,GREEN)
      drawTargets()
    if len(GameVairables.loggedplayer) > 2:
      pygametext(f"You ({GameVairables.loggedplayer[2][0]},{GameVairables.loggedplayer[2][1]})-{GameVairables.loggedplayer[2][2]}",411-10,157,30,GREEN)
      pygametext(f"Cpu ({GameVairables.loggedOpponent[2][0]},{GameVairables.loggedOpponent[2][1]})-{GameVairables.loggedOpponent[2][2]}",411-10,177,30,GREEN)
      pygametext(f"----------------------",400,187,30,GREEN)
    if len(GameVairables.loggedplayer) > 1:
      pygametext(f"You ({GameVairables.loggedplayer[1][0]},{GameVairables.loggedplayer[1][1]})-{GameVairables.loggedplayer[1][2]}",411-10,115,30,GREEN)
      pygametext(f"Cpu ({GameVairables.loggedOpponent[1][0]},{GameVairables.loggedOpponent[1][1]})-{GameVairables.loggedOpponent[1][2]}",411-10,135,30,GREEN)
      pygametext(f"----------------------",400,145,30,GREEN)
    if len(GameVairables.loggedplayer) > 0:
      if Delay == False:
         fade = 0
      if fade < 240:
        while fade < 240:
          pygametext(f"You ({GameVairables.loggedplayer[0][0]},{GameVairables.loggedplayer[0][1]})-{GameVairables.loggedplayer[0][2]}",411-10,70,30,GREEN) #add fade back?? (0,fade,0)
          pygametext(f"Cpu ({GameVairables.loggedOpponent[0][0]},{GameVairables.loggedOpponent[0][1]})-{GameVairables.loggedOpponent[0][2]}",411-10,90,30,GREEN)#(0,fade,0)
          pygametext(f"----------------------",400,103,30,GREEN)
          fade += 20
          pygame.display.update()
          pygame.time.wait(50)
      else:
        pygametext(f"You ({GameVairables.loggedplayer[0][0]},{GameVairables.loggedplayer[0][1]})-{GameVairables.loggedplayer[0][2]}",411-10,70,30,GREEN)#(0,fade,0)
        pygametext(f"Cpu ({GameVairables.loggedOpponent[0][0]},{GameVairables.loggedOpponent[0][1]})-{GameVairables.loggedOpponent[0][2]}",411-10,90,30,GREEN)#(0,fade,0)
        pygametext(f"----------------------",400,103,30,GREEN)#(0,fade,0)
  except IndexError:
     pass

def Clearscreen(colour):
  screenH = (WINDOW_HEIGHT-40) / 26
  pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
  pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
  #print(screenH)
  xlist = [i for i in range(0, 21)]
  ylist = [i for i in range(0, 21)]
  random.shuffle(xlist)
  random.shuffle(ylist)
  for xpos in xlist:
    for ypos in ylist:
      pygame.draw.rect(SCREEN, colour, (30 + 26*xpos, 30 + 26*ypos , 26 , 26))
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
      pygame.display.update()
      pygame.time.wait(5)
  pygame.time.wait(500)
  #print("done")

def Loadscreen(colour=DARKGREEN):
  screenH = (WINDOW_HEIGHT-40) / 26
  pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
  pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
  #print(screenH)
  xlist = [i for i in range(0, 21)]*21
  ylist = [i for i in range(0, 21)]
  random.shuffle(xlist)
  random.shuffle(ylist)
  for xpos in xlist:
    for ypos in ylist:
      pygame.draw.rect(SCREEN, colour, (30 + 26*xpos, 30 + 26*ypos , 26 , 26))
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
      pygame.display.update()
      pygame.time.wait(5)
  pygame.time.wait(500)
  #print("done")

def Selector(size,xadd,yadd,yboxmove,xboxmove,colour):
  blockSize = size
  y = 0 #+ blockSize moves squares
  x = 0
  for z in range(yboxmove):
    y = y + blockSize
  for w in range(xboxmove):
    x = x + blockSize
  rect = pygame.Rect(x+xadd, y+yadd, blockSize, blockSize)
  pygame.draw.rect(SCREEN, colour, rect, 4)


def Heatmap(matrix):
  z = 14
  coords = []
  for x in range(10):
    for y in range(10):
      if matrix[x][y] != 0 and matrix[x][y] != "=" and matrix[x][y] != "#":
        coords.append([matrix[x][y], x, y])
  if coords:
    max_value = max(coords, key=lambda item: item[0])[0]
  else:
    max_value = 0
   
    # Now draw the rectangles using pygame
  for value, x, y in coords:
        # Scale the green value based on the value
      if max_value > 0:
          BrightnessLevel = int(255 * (value / max_value))
      else:
          BrightnessLevel = 0
      ColourChangingColour = [0,0,0]
      for rgbValue in range(0,3):
        if GREEN[rgbValue] != 0:
          ColourChangingColour[rgbValue] = BrightnessLevel
      pygame.draw.rect(SCREEN, ColourChangingColour, (402 + (y * 15), 415 + (x * 15), 14, 14), 0, 0, 0)
 
#---------------------------------------------

counter = 0
seconds = 0
prevsecond = 0
cood = []
cood2 = []
cood3 = []

def Menurender():
  global cood, cood2, cood3
  cood = []
  xb = [i-1 for i in range(0, 16)]
  yb = [i for i in range(1, 16)]
  random.shuffle(xb)
  random.shuffle(yb)
  while len(cood) < 25:
    for xco in xb:
      for yco in yb:
        if random.random() < 0.2:
          yb.remove(yco)
        cood.append([xco,yco])
  cood2 = []
  xb2 = [i-1 for i in range(0, 16)]
  yb2 = [i-1 for i in range(1, 16)]
  random.shuffle(xb2)
  random.shuffle(yb2)
  while len(cood2) < 20:
    for xco2 in xb2:
      for yco2 in yb2:
        if random.random() < 0.4:
          yb2.remove(yco2)
        cood2.append([xco2,yco2])

  cood3 = []
  xb3 = [i-1 for i in range(0, 16)]
  yb3 = [i for i in range(0, 16)]
  random.shuffle(xb3)
  random.shuffle(yb3)
  while len(cood3) < 2:
    for xco3 in xb3:
      if random.random() < 0.1:
        for yco3 in yb3:
          if random.random() < 0.5:
            link = 0
            for link in range(random.randint(2, 2)):
              if xco3 + link < 15:  # Ensure x-coordinate doesn't exceed 15
                cood3.append([xco3 + link, yco3])
          else:
            link = 0
            for link in range(random.randint(2, 2)):
              if yco3 + link < 15:  # Ensure y-coordinate doesn't exceed 15
                cood3.append([xco3, yco3 + link])
#--------------------------------
xxx = 0
yyy = 0
orentation = 1
def FleetSetup():
  global xxx,yyy,orentation
  SemiDarkColour = max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)
  VeryBrightColour = [0,0,0]
  for rgbValue in range(0,3):
      if GREEN[rgbValue] != 0:
        VeryBrightColour[rgbValue] = 255
  pygame.draw.rect(SCREEN,GREEN,(38,40,525,80),0,5,5)
  pygametext("Fleet Arrangement",60,65,50,DARKGREEN)
  Human.printeachboattype
  for ship in Human.BattleshipHealth:
    pygame.draw.rect(SCREEN,SemiDarkColour,(125+(33*ship[1]),125+(33*ship[0]),33,33),0,0,0)
  drawGrid(33,125,125,1)
  x=85
  pygame.draw.rect(SCREEN,GREEN,(38,40+x,4,525-x),0,10,10)
  pygame.draw.rect(SCREEN,GREEN,(557,40+x,4,525-x),0,10,10)
  try:
    if orentation == 1:
      for length in range(1,Human.ships[0]+1):
        pygame.draw.rect(SCREEN,VeryBrightColour,(125+(33*yyy),125+(33*xxx),33,33*length),0,0,0)
      drawGrid(33,125,125,1)
    else:
      for length in range(1,Human.ships[0]+1):
        pygame.draw.rect(SCREEN,VeryBrightColour,(125+(33*yyy),125+(33*xxx),33*length,33),0,0,0)
      drawGrid(33,125,125,1)
  except IndexError:
    return True
  keys = pygame.key.get_pressed()
  if keys[ord('s')] or keys[pygame.K_DOWN]:
      if (xxx < 10 - length and orentation == 1) or (xxx < 9 and orentation == 0):
        xxx += 1
        pygame.time.wait(100)
  if keys[ord('d')] or keys[pygame.K_RIGHT]:
      if (yyy < 10 - length and orentation == 0) or (yyy < 9 and orentation == 1):
        yyy += 1
        pygame.time.wait(100)
  if keys[ord('w')] or keys[pygame.K_UP]:
      if xxx >= 1:
        xxx -= 1
        pygame.time.wait(100)
  if keys[ord('a')] or keys[pygame.K_LEFT]:
      if yyy >= 1:
        yyy -= 1
        pygame.time.wait(100)
  if keys[pygame.K_RETURN]:
    Human.PlaceBoat(xxx,yyy,orentation,Human.ships[0],False)
    print(Human.ships)
    print(Human.BattleshipHealth)
    Human.PrintFullBoard()
    xxx= 0
    yyy = 0
    pygame.time.wait(100)
  if keys[pygame.K_RSHIFT] or keys[pygame.K_LSHIFT]:
      if orentation == 1:
        orentation = 0
        if yyy > 6:
          yyy = 5
      else:
        orentation = 1
        if xxx > 6:
          xxx = 5
      Human.PrintFullBoard()
      pygame.time.wait(100)

class IntelMenu():
  def __init__(self):
    self.page = 0

  def Render(self):
    VeryBrightColour = [0,0,0]
    for rgbValue in range(0,3):
      if GREEN[rgbValue] != 0:
        VeryBrightColour[rgbValue] = 255
    pygame.draw.rect(SCREEN,GREEN,(38,40,200,70),0,5,5)
    pygametext("Intel",50,53,70,DARKGREEN)
    pygame.draw.rect(SCREEN,GREEN,(38,285,200,65),5,5,5)
    IntelPages = ["Overview","Controls", "Gamemodes","Adv. Modes","Fleet Setup","Gameplay","End Screen"]#max 10 char ["Classic","Salvo","Fog Of War","Rules Reversed","Capture The Flag"]
    for x in range(0,5):
      try:
        if x == 0:
          pygametext(IntelPages[self.page+x],50,305+((x)*75),40,GREEN)
          pygame.draw.rect(SCREEN,GREEN,(38,285+((x)*75),200,65),5,5,5)
        else:
          pygametext(IntelPages[self.page+x],50,305+((x)*75),40,(max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)))
          pygame.draw.rect(SCREEN,(max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)),(38,285+((x)*75),200,65),5,5,5)
      except IndexError:
        pass
    for x in range(1,3):
      try:
        if self.page-x >= 0:
          pygametext(IntelPages[self.page-x],50,305+(((x)*-1)*75),40,(max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)))
          pygame.draw.rect(SCREEN,(max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)),(38,285+((x*-1)*75),200,65),5,5,5)
      except IndexError:
        pass
    if self.page == 0:
      pagetext = ["Each player secretly","sets up their fleet","-----------------------------------",
                     "The primary objective","is to locate and sink","your opponent's fleet","before they sink yours","-----------------------------------",
                     "Players will choose a","set of coordinates to","aim and fire at",
                     "Recieveing a Hit, Sink","or Miss once the shot", "is taken","-----------------------------------"]
 
    elif self.page == 1:
      pagetext = ["            -> Move Up","",
                  "            -> Move Down","",
                  "            -> Move Left","",
                  "            -> Move Right",
                  "-----------------------------------",
                  "            -> Select","",
                  "            -> Back","",
                  "            -> Rotate",
                  "-----------------------------------",]
      for x in range(0,4):
        pygame.draw.rect(SCREEN,GREEN,(240,40+(x*57),45,45),5,5,5)
        pygame.draw.rect(SCREEN,GREEN,(240+50,40+(x*57),45,45),5,5,5)
        pygametext("Arrow",246+45+2,48+(x*57),20,GREEN)
      for x in range (0,3):
        pygame.draw.rect(SCREEN,GREEN,(240+25,40+((x+4)*58),45,45),5,5,5)
      pygametext("W",246,48,50,GREEN)
      #pygametext("Arrow",246+45+2,48,20,GREEN)
      pygametext("Up",246+45+12,48+11,20,GREEN)
      pygametext("Down",246+45+3,48+11+57,20,GREEN)
      pygametext("Left",246+45+9,48+11+57+57,20,GREEN)
      pygametext("Right",246+45+5,48+11+57+57+57,20,GREEN)
      pygametext("S",246+3,48+57,50,GREEN)
      pygametext("A",246+3,48+57+57,50,GREEN)
      pygametext("D",246+3,48+57+57+57,50,GREEN)
      pygametext("ENTR",246+22,48+57+57+57+57+10,20,GREEN)
      pygametext("ESC",246+22,48+57+57+57+57+10+58,27,GREEN)
      pygametext("SHFT",246+22,48+57+57+57+57+10+58+58,22,GREEN)
    elif self.page == 2:
      pagetext = ["Classic:",
                  "This is the standard","game mode","Players try to destroy", "opponents fleet to win",
                  "-----------------------------------",
                  "Fog Of War",
                  "This plays the same", "as classic", "Fog will cover the grid","hiding past shot info",
                  "-----------------------------------",
                  "Capture The Flag",
                  "This is the quickest","game mode to play","Players try to destroy","a specifc ship type",]
    elif self.page == 3:
      pagetext = ["Salvo",
                  "A advanatge is given","to the loosing player", "As players ships are","destroyed, they are","given more shots to","fire against the","opponent",
                  "-----------------------------------",
                  "Rules Reversed",
                  "This contrasts the win", "goal for the players","Players aim to fire in all","empty spaces on the", "grid, to get all possible","misses",]
    elif self.page == 4:
      pagetext = ["Players will set up","their fleet to how they","would like too","The only limitations is", "the grid's size and no","ship can overlap with","other ships in the grid",
                  "-----------------------------------",
                  "It may be advised to","seperate ships from","other ships","As they can be more","difficult to locate","and destroy",]
    elif self.page == 5:
      pagetext = ["Game play is split into","both players rounds","Each player will select","a specific coordiante to","fire at",
                  "-----------------------------------",
                  "           Displays a Miss", "",
                  "           Displays a Hit", "",
                  "           Displays a Sink",
                  "-----------------------------------",
                  "Game play continues","players until the win","condition of the game","mode is met",]
      for x in range (0,3):
        pygame.draw.rect(SCREEN,GREEN,(240+25,37+((x+3)*58),45,45),0,5,5)
        if x == 2:
          pygame.draw.rect(SCREEN,VeryBrightColour,(240+25,37+16+((x+3)*58),45,12),0,0,0)
          pygame.draw.rect(SCREEN,VeryBrightColour,(240+25+16.5,37+((x+3)*58),12,45),0,0,0)
          pygame.draw.circle(SCREEN, VeryBrightColour, (240+25+22, 37+22+((x+3)*58)), 14)
        else:
          pygame.draw.rect(SCREEN,DARKGREEN,(240+25,37+16+((x+3)*58),45,12),0,0,0)
          pygame.draw.rect(SCREEN,DARKGREEN,(240+25+16.5,37+((x+3)*58),12,45),0,0,0)
          pygame.draw.circle(SCREEN, DARKGREEN, (240+25+22, 37+22+((x+3)*58)), 14)
        if x == 1:
          pygame.draw.circle(SCREEN,VeryBrightColour, (240+25+22, 37+22+((x+3)*58)), 8)
    elif self.page == 6:
      pagetext = ["A player wins when the","end screen is shown",
                  "-----------------------------------",
                  "            -> First Strike","",
                  "            -> Shot Streak","",
                  "            -> Accuracy",
                  "-----------------------------------",
                  "First Strike is the round", "when each player got","their first Hit",
                  "Shot Streak is how","many Hits in a row that","the player got",
                  "Accuracy is the % of","Hits each player had",]
      for x in range (0,3):
        pygame.draw.rect(SCREEN,GREEN,(240+25,7+((x+2)*58),45,45),5,5,5)
      pygame.draw.circle(SCREEN, GREEN, (240+25+22, 28.5+(2*58)), 12,5)
      pygame.draw.rect(SCREEN,GREEN,(240+25+20,32+((0+2)*58),5,12))
      pygame.draw.rect(SCREEN,GREEN,(240+25+20,12+((0+2)*58),5,12))
      pygame.draw.rect(SCREEN,GREEN,(240+25+5,25+((0+2)*58),12,5))
      pygame.draw.rect(SCREEN,GREEN,(240+25+27,25+((0+2)*58),12,5))
      pygame.draw.circle(SCREEN, GREEN, (240+25+15, 22+(3*58)), 8,3)
      pygame.draw.circle(SCREEN, GREEN, (240+25+15, 37+(3*58)), 8,3)
      pygame.draw.circle(SCREEN, GREEN, (240+25+30, 29+(3*58)), 8,3)
      pygame.draw.circle(SCREEN, GREEN, (240+25+15, 22+(3*58)), 2)
      pygame.draw.circle(SCREEN, GREEN, (240+25+15, 37+(3*58)), 2)
      pygame.draw.circle(SCREEN, GREEN, (240+25+30, 29+(3*58)), 2)
      pygame.draw.circle(SCREEN, GREEN, (240+25+22, 28.5+(4*58)), 12,5)
      pygame.draw.circle(SCREEN, GREEN, (240+25+22, 28.5+(4*58)), 4)
     
    for index in range(len(pagetext)):
      line = pagetext[index]
      pygametext(line,242,40+(index*30),40,GREEN)
    pygame.draw.rect(SCREEN,GREEN,(38,40+75,4,525-75),0,0,0)
    pygame.draw.rect(SCREEN,GREEN,(38+196,40+75,4,525-75),0,0,0)
    pygame.draw.rect(SCREEN,DARKGREEN,(0,40+75,38,525-75),0,0,0)
    pygame.draw.rect(SCREEN,GREEN,(557,40,4,525),0,0,0)
    pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
    pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
    keys = pygame.key.get_pressed()
    if keys[ord('w')] or keys[pygame.K_UP]:
      if self.page > 0:
        self.page -= 1
        #print(self.page)
      pygame.time.wait(200)
    if keys[ord('s')] or keys[pygame.K_DOWN]:
      if self.page < len(IntelPages)-1:
        self.page += 1
        #print(self.page)
        pygame.time.wait(200)
    if keys[pygame.K_ESCAPE]:
      GameVairables.menu = 0
      Clearscreen(DARKGREEN)
#----------------------------------------------------------------
class AccountManagement():
  def __init__(self):
    self.base_url = 'http://localhost:5000'
 
  def signup(self,username, password):
    url = f'{self.base_url}/signup'
    data = {'username': username, 'password': password}
    response = requests.post(url, json=data)
    return response.json()

  # Function to sign in an existing user
  def signin(self,username, password):
      url = f'{self.base_url}/signin'
      data = {'username': username, 'password': password}
      response = requests.post(url, json=data)
    # Check if the sign-in was successful
      if response.status_code == 200:
        print('Signed in successfully')
        return True
      else:
        print('Sign in failed:', response.json().get('message'))
        return False

  def update_user(self,username, password, new_username=None, new_password=None,
                longest_hit_streak=None,
                Classic_Wins=None, Classic_Loss=None, Classic_accuracy=None,
                Classic_last_five_results=None, Salvo_Wins=None, Salvo_Loss=None,
                Salvo_accuracy=None, Salvo_last_five_results=None, FOW_Wins=None,
                FOW_Loss=None, FOW_accuracy=None, FOW_last_five_results=None,
                RR_Wins=None, RR_Loss=None, RR_accuracy=None, RR_last_five_results=None,
                CTF_Wins=None, CTF_Loss=None, CTF_accuracy=None, CTF_last_five_results=None):

    url = f'{self.base_url}/update_user'
    data = {
        'username': username,  # Used for authentication
        'password': password,  # Used for authentication
        'new_username': new_username,
        'new_password': new_password,
        #'accuracy': accuracy,
        'longest_hit_streak': longest_hit_streak,
        #'total_games_played': total_games_played,
        'Classic_Wins': Classic_Wins,
        'Classic_Loss': Classic_Loss,
        'Classic_accuracy': Classic_accuracy,
        'Classic_last_five_results': Classic_last_five_results,
        'Salvo_Wins': Salvo_Wins,
        'Salvo_Loss': Salvo_Loss,
        'Salvo_accuracy': Salvo_accuracy,
        'Salvo_last_five_results': Salvo_last_five_results,
        'FOW_Wins': FOW_Wins,
        'FOW_Loss': FOW_Loss,
        'FOW_accuracy': FOW_accuracy,
        'FOW_last_five_results': FOW_last_five_results,
        'RR_Wins': RR_Wins,
        'RR_Loss': RR_Loss,
        'RR_accuracy': RR_accuracy,
        'RR_last_five_results': RR_last_five_results,
        'CTF_Wins': CTF_Wins,
        'CTF_Loss': CTF_Loss,
        'CTF_accuracy': CTF_accuracy,
        'CTF_last_five_results': CTF_last_five_results,
    }

    response = requests.put(url, json=data)
    return response.json()
  def get_user_data(self,username, password):
    url = f'{self.base_url}/get_user'  # This URL should match your Flask route for fetching user data
    data = {'username': username, 'password': password}  # Authentication details
    response = requests.post(url, json=data)  # Assuming you're using POST for authentication
    return response.json()  # Return the user's data as a JSON response
 
  def delete_user(self,username, password):
    url = f'{self.base_url}/delete_user'  # Adjust if Flask is running on another host/port
    data = {'username': username, 'password': password}
   
    response = requests.delete(url, json=data)
   
    if response.status_code == 200:
        print('User account deleted successfully')
    else:
        print(f'Error: {response.json()["message"]}')

PlayerAccount = AccountManagement()
#----------------------------------------------------------------

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    #last_five_results = db.Column(db.String(10), default='0,0,0,0,0') #1,2,3,4,5
    longest_hit_streak = db.Column(db.Integer, default=0)
    #total_games_played = db.Column(db.Integer, default=0)
    #
    Classic_Wins = db.Column(db.Integer, default=0)
    Classic_Loss = db.Column(db.Integer, default=0)
    Classic_accuracy = db.Column(db.Integer, default=0)
    Classic_last_five_results = db.Column(db.String(10), default='0,0,0,0,0') #last_five_results_list = last_five_results_str.split(',')
     #
    Salvo_Wins = db.Column(db.Integer, default=0)
    Salvo_Loss = db.Column(db.Integer, default=0)
    Salvo_accuracy = db.Column(db.Integer, default=0)
    Salvo_last_five_results = db.Column(db.String(10), default='0,0,0,0,0') #last_five_results_list = last_five_results_str.split(',')
 #
    FOW_Wins = db.Column(db.Integer, default=0)
    FOW_Loss = db.Column(db.Integer, default=0)
    FOW_accuracy = db.Column(db.Integer, default=0)
    FOW_last_five_results = db.Column(db.String(10), default='0,0,0,0,0') #last_five_results_list = last_five_results_str.split(',')
 #
    RR_Wins = db.Column(db.Integer, default=0)
    RR_Loss = db.Column(db.Integer, default=0)
    RR_accuracy = db.Column(db.Integer, default=0)
    RR_last_five_results = db.Column(db.String(10), default='0,0,0,0,0') #last_five_results_list = last_five_results_str.split(',')
 #
    CTF_Wins = db.Column(db.Integer, default=0)
    CTF_Loss = db.Column(db.Integer, default=0)
    CTF_accuracy = db.Column(db.Integer, default=0)
    CTF_last_five_results = db.Column(db.String(10), default='0,0,0,0,0') #last_five_results_list = last_five_results_str.split(',')



@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    print("Signup route hit")  
   
    with app.app_context():
        if User.query.filter_by(username=username).first():
            return jsonify({'message': 'Username already exists. Please choose a different username'}), 400
       
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
       
        return jsonify({'message': 'Account created successfully'})

@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    username = data.get('username')
    password = data.get('password')
   
    with app.app_context():
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return jsonify({'message': 'Invalid username or password. Please try again'}), 401
       
        return jsonify({'message': 'Signed in successfully'})

@app.route('/users', methods=['GET'])
def get_users():
    with app.app_context():
        users = User.query.all()
        user_list = [{
            'username': user.username,
            'password': user.password,
            'Classic_Wins': user.Classic_Wins,
            'Classic_Loss': user.Classic_Loss,
            'Classic_accuracy': user.Classic_accuracy,
            'Classic_last_five_results': user.Classic_last_five_results,
            'Salvo_Wins': user.Salvo_Wins,
            'Salvo_Loss': user.Salvo_Loss,
            'Salvo_accuracy': user.Salvo_accuracy,
            'Salvo_last_five_results': user.Salvo_last_five_results,
            'FOW_Wins': user.FOW_Wins,
            'FOW_Loss': user.FOW_Loss,
            'FOW_accuracy': user.FOW_accuracy,
            'FOW_last_five_results': user.FOW_last_five_results,
            'RR_Wins': user.RR_Wins,
            'RR_Loss': user.RR_Loss,
            'RR_accuracy': user.RR_accuracy,
            'RR_last_five_results': user.RR_last_five_results,
            'CTF_Wins': user.CTF_Wins,
            'CTF_Loss': user.CTF_Loss,
            'CTF_accuracy': user.CTF_accuracy,
            'CTF_last_five_results': user.CTF_last_five_results,
            'longest_hit_streak': user.longest_hit_streak,
            #'total_games_played': user.total_games_played
        } for user in users]
        return jsonify(user_list)
   
@app.route('/get_user', methods=['POST'])
def get_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    with app.app_context():
        # Verify the user exists and the password is correct
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return jsonify({'message': 'Invalid username or password'}), 401

        # Return user data including all new fields
        user_data = {
            'username': user.username,
            #'accuracy': user.accuracy,
            'longest_hit_streak': user.longest_hit_streak,
            #'total_games_played': user.total_games_played,
            'Classic_Wins': user.Classic_Wins,
            'Classic_Loss': user.Classic_Loss,
            'Classic_accuracy': user.Classic_accuracy,
            'Classic_last_five_results': user.Classic_last_five_results,
            'Salvo_Wins': user.Salvo_Wins,
            'Salvo_Loss': user.Salvo_Loss,
            'Salvo_accuracy': user.Salvo_accuracy,
            'Salvo_last_five_results': user.Salvo_last_five_results,
            'FOW_Wins': user.FOW_Wins,
            'FOW_Loss': user.FOW_Loss,
            'FOW_accuracy': user.FOW_accuracy,
            'FOW_last_five_results': user.FOW_last_five_results,
            'RR_Wins': user.RR_Wins,
            'RR_Loss': user.RR_Loss,
            'RR_accuracy': user.RR_accuracy,
            'RR_last_five_results': user.RR_last_five_results,
            'CTF_Wins': user.CTF_Wins,
            'CTF_Loss': user.CTF_Loss,
            'CTF_accuracy': user.CTF_accuracy,
            'CTF_last_five_results': user.CTF_last_five_results
        }
        return jsonify(user_data)

   
@app.route('/update_user', methods=['PUT'])
def update_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')  # The current password for authentication

    # New optional fields
    new_username = data.get('new_username')
    new_password = data.get('new_password')
    #new_accuracy = data.get('accuracy')
    new_longest_hit_streak = data.get('longest_hit_streak')
    #new_total_games_played = data.get('total_games_played')
    new_last_five_results = data.get('last_five_results')

    # New game mode-specific fields
    new_classic_wins = data.get('Classic_Wins')
    new_classic_loss = data.get('Classic_Loss')
    new_classic_accuracy = data.get('Classic_accuracy')
    new_classic_last_five_results = data.get('Classic_last_five_results')

    new_salvo_wins = data.get('Salvo_Wins')
    new_salvo_loss = data.get('Salvo_Loss')
    new_salvo_accuracy = data.get('Salvo_accuracy')
    new_salvo_last_five_results = data.get('Salvo_last_five_results')

    new_fow_wins = data.get('FOW_Wins')
    new_fow_loss = data.get('FOW_Loss')
    new_fow_accuracy = data.get('FOW_accuracy')
    new_fow_last_five_results = data.get('FOW_last_five_results')

    new_rr_wins = data.get('RR_Wins')
    new_rr_loss = data.get('RR_Loss')
    new_rr_accuracy = data.get('RR_accuracy')
    new_rr_last_five_results = data.get('RR_last_five_results')

    new_ctf_wins = data.get('CTF_Wins')
    new_ctf_loss = data.get('CTF_Loss')
    new_ctf_accuracy = data.get('CTF_accuracy')
    new_ctf_last_five_results = data.get('CTF_last_five_results')

    with app.app_context():
        # Verify the user exists and the password is correct
        user = User.query.filter_by(username=username, password=password).first()
        if not user:
            return jsonify({'message': 'Invalid username or password. Please try again'}), 401

        # Update fields if provided in the request
        if new_username:
            if User.query.filter_by(username=new_username).first():
                return jsonify({'message': 'Username already exists. Please choose a different one'}), 400
            user.username = new_username

        if new_password:
            user.password = new_password

        #if new_accuracy is not None:
        #    user.accuracy = new_accuracy

        if new_longest_hit_streak is not None:
            user.longest_hit_streak = new_longest_hit_streak

        #if new_total_games_played is not None:
        #    user.total_games_played = new_total_games_played

        if new_last_five_results:
            user.last_five_results = new_last_five_results

        # Update game mode-specific fields
        if new_classic_wins is not None:
            user.Classic_Wins = new_classic_wins

        if new_classic_loss is not None:
            user.Classic_Loss = new_classic_loss

        if new_classic_accuracy is not None:
            user.Classic_accuracy = new_classic_accuracy

        if new_classic_last_five_results:
            user.Classic_last_five_results = new_classic_last_five_results

        if new_salvo_wins is not None:
            user.Salvo_Wins = new_salvo_wins

        if new_salvo_loss is not None:
            user.Salvo_Loss = new_salvo_loss

        if new_salvo_accuracy is not None:
            user.Salvo_accuracy = new_salvo_accuracy

        if new_salvo_last_five_results:
            user.Salvo_last_five_results = new_salvo_last_five_results

        if new_fow_wins is not None:
            user.FOW_Wins = new_fow_wins

        if new_fow_loss is not None:
            user.FOW_Loss = new_fow_loss

        if new_fow_accuracy is not None:
            user.FOW_accuracy = new_fow_accuracy

        if new_fow_last_five_results:
            user.FOW_last_five_results = new_fow_last_five_results

        if new_rr_wins is not None:
            user.RR_Wins = new_rr_wins

        if new_rr_loss is not None:
            user.RR_Loss = new_rr_loss

        if new_rr_accuracy is not None:
            user.RR_accuracy = new_rr_accuracy

        if new_rr_last_five_results:
            user.RR_last_five_results = new_rr_last_five_results

        if new_ctf_wins is not None:
            user.CTF_Wins = new_ctf_wins

        if new_ctf_loss is not None:
            user.CTF_Loss = new_ctf_loss

        if new_ctf_accuracy is not None:
            user.CTF_accuracy = new_ctf_accuracy

        if new_ctf_last_five_results:
            user.CTF_last_five_results = new_ctf_last_five_results

        # Commit the changes to the database
        db.session.commit()

        return jsonify({'message': 'User information updated successfully'})

@app.route('/delete_user', methods=['DELETE'])
def delete_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
   
    with app.app_context():
        # Find the user by username and password
        user = User.query.filter_by(username=username, password=password).first()
       
        if not user:
            return jsonify({'message': 'Invalid username or password'}), 401
       
        # Delete the user
        db.session.delete(user)
        db.session.commit()
       
        return jsonify({'message': 'User account deleted successfully'}), 200
@app.route('/reset_database')
def reset_database():
    with app.app_context():
        db.drop_all()  # This will drop all tables
        db.create_all()  # This will recreate the tables
    return "Database reset successfully!"

def run_flask():
  app.run(debug=True, use_reloader=False)



#----------------------------------------------------------------
class AccountMenu():
  def __init__(self,Human):
    self.Level = 0
    self.username = ""
    self.Password = ""
    self.Human = Human
    self.dataFetched = False
    self.timer= 0
    self.GamemodeInfo= 0
    self.trail = False
    self.AccountPageOption = 0
    self.edit = False
    #----------------------
    self.SignOption = 0
    self.TextSlide = 0
    #--------------------------- (The Fetched Data Of Their Account:)
    #self.accuracy = None
    self.longest_hit_streak = None
    self.total_games_played = None
    self.Classic_Wins = None
    self.Classic_Loss = None
    self.Classic_accuracy = None
    self.Classic_last_five_results = None
    self.Salvo_Wins = None
    self.Salvo_Loss = None
    self.Salvo_accuracy = None
    self.Salvo_last_five_results = None
    self.FOW_Wins = None
    self.FOW_Loss = None
    self.FOW_accuracy = None
    self.FOW_last_five_results = None
    self.RR_Wins = None
    self.RR_Loss = None
    self.RR_accuracy = None
    self.RR_last_five_results = None
    self.CTF_Wins = None
    self.CTF_Loss = None
    self.CTF_accuracy = None
    self.CTF_last_five_results = None
  def controls(self):
    CurrentField = self.username if self.Level == 0+1 else self.Password
    keys = pygame.key.get_pressed()
    for index, pressed in enumerate(keys):
        if pressed:
          if index+37+24+32 == 135:
            CurrentField = CurrentField[:-1]  # Remove last character
          if len(CurrentField) >= 14:
             break
          if index+93 == 138:
            CurrentField += ("_" if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else "-")
          if index+93 <= 122:
            CurrentField += chr(index+93-(32 if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT] else 0))
          if index+93 >= 123 and index+93 <= 132:
            if index+93 == 132:
               CurrentField += "0"
            else:
              CurrentField += chr(index+93-74)
          #print(index+37+24+32-74)
          if self.Level != 0:
            pygame.time.delay(100)
          if self.Level == 0+1:
            self.username = CurrentField  
          else:
            self.Password = CurrentField
 
  def SignInrender(self):
    x = 70
    #print(self.Level)
    if self.Level == 0:
       SignOptionBox = GREEN
       SignOptionText = DARKGREEN
       UsernameBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
       UsernameBoxText = DARKGREEN
       PasswordBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
       PasswordBoxText = DARKGREEN
       SignInBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
    elif self.Level == 0+1:
       SignOptionBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
       SignOptionText = DARKGREEN
       UsernameBox = GREEN
       UsernameBoxText = DARKGREEN
       PasswordBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
       PasswordBoxText = DARKGREEN
       SignInBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
    elif self.Level == 1+1:
       SignOptionBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
       SignOptionText = DARKGREEN
       UsernameBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
       UsernameBoxText = DARKGREEN
       PasswordBox = GREEN
       PasswordBoxText = DARKGREEN
       SignInBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
    elif self.Level == 1+1+1:
       SignOptionBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
       SignOptionText = DARKGREEN
       UsernameBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
       UsernameBoxText = DARKGREEN
       PasswordBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
       PasswordBoxText = DARKGREEN
       SignInBox = GREEN

    SignOptions = ["Account Sign In","Account Sign Up"]
    pygame.draw.rect(SCREEN,SignOptionBox,(95,x,412,60),0,5,5)
    if self.TextSlide == -1:
      pygametext(SignOptions[self.SignOption],max(((137+137+137+100)-self.timer),137),80,60,SignOptionText) #start from
      pygametext(SignOptions[self.SignOption-1],max((137-self.timer),(137+100)*-1),80,60,SignOptionText)
      if (137+137+100)-self.timer <= 0:
         self.TextSlide = 0
         self.timer = 0
      else:
        self.timer += 3
    elif self.TextSlide == 1:  # Sliding right
      # Move the current option out and the next option in from the left
      pygametext(SignOptions[self.SignOption], min((((137+100)*-1) + self.timer), 137), 80, 60, SignOptionText)
      pygametext(SignOptions[self.SignOption-1], min((137 + self.timer), 137+137+137+100), 80, 60, SignOptionText)
      if ((137+100)*-1) + self.timer >= 137:
        self.TextSlide = 0
        self.timer = 0
      else:
        self.timer += 3

    else:  # No slide, just render the text
        pygametext(SignOptions[self.SignOption], 137, 80, 60, SignOptionText)
 
    pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
    pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
    #pygametext(SignOptions[self.SignOption],(137+100)*-1,80,60,"RED") #need to go
    #pygametext(SignOptions[self.SignOption],137+137+137+100,80,60,"RED") #start from

    pygame.draw.rect(SCREEN,UsernameBox,(95,115+x,412,60),0,50,50)
    if self.username == "":
      pygametext("Enter Username",140,198,60,UsernameBoxText)
    else:
       pygametext(self.username,(140),198,60,UsernameBoxText) #-(len(self.username)*11)
    pygame.draw.rect(SCREEN,PasswordBox,(95,115+150+x,412,60),0,50,50)
    if self.Password == "":
      pygametext("Enter Password",140,198+x+x+10,60,PasswordBoxText)
    else:
      keys = pygame.key.get_pressed()
      hiddenpassword = ""
      for letter in self.Password:
        hiddenpassword += "*"
      pygametext((self.Password if keys[pygame.K_LEFT] and self.Level == 1+1 or keys[pygame.K_RIGHT] and self.Level == 1+1 else hiddenpassword),(140),198+x+x+10,60,PasswordBoxText)
    pygame.draw.rect(SCREEN,SignInBox,(109*1.5,115+150+x+x+40,412/1.5,60),0,5,5)
    SignInBoxText = ["Sign In", "Sign Up"]
    pygametext(SignInBoxText[self.SignOption],232,198+x+x+50+x,60,DARKGREEN)
    pygame.draw.rect(SCREEN,GREEN,(38,40,4,525),0,0,0)
    pygame.draw.rect(SCREEN,GREEN,(557,40,4,525),0,0,0)
   
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
      if self.Level == 0 and self.TextSlide == 0:
        if self.SignOption < len(SignOptions) - 1:
          self.SignOption += 1
          self.TextSlide = -1
          #self.timer = 0
        #print("Yes")
    if keys[pygame.K_RIGHT]:
      if self.Level == 0 and self.TextSlide == 0:
        if self.SignOption > 0:
          self.SignOption -= 1
          self.TextSlide = 1
    if keys[pygame.K_UP]:
              if self.Level > 0:
                  self.Level -= 1
    if keys[pygame.K_DOWN]:
              if self.Level < 3:
                  self.Level += 1
    if keys[pygame.K_ESCAPE]:
       Clearscreen(DARKGREEN)
       GameVairables.menu = 0
       self.timer = 0
    if keys[pygame.K_RETURN]:
              if self.Level == 2+1 and self.SignOption == 0:
                 if self.username != "" and  self.Password != "":
                  Human.SignedIn = PlayerAccount.signin(self.username,self.Password)#self.
                 if Human.SignedIn == True:
                    self.timer = 0
                    Human.username = self.username
                    Human.password = self.Password
                    user_data_response = PlayerAccount.get_user_data(self.username,self.Password)
                    #print('User data response:', user_data_response)
                    #self.accuracy = user_data_response.get('accuracy')
                    self.longest_hit_streak = user_data_response.get('longest_hit_streak')
                    #self.total_games_played = user_data_response.get('total_games_played')
                    self.Classic_Wins = user_data_response.get('Classic_Wins')
                    self.Classic_Loss = user_data_response.get('Classic_Loss')
                    self.Classic_accuracy = user_data_response.get('Classic_accuracy')
                    self.Classic_last_five_results = user_data_response.get('Classic_last_five_results')
                    self.Salvo_Wins = user_data_response.get('Salvo_Wins')
                    self.Salvo_Loss = user_data_response.get('Salvo_Loss')
                    self.Salvo_accuracy = user_data_response.get('Salvo_accuracy')
                    self.Salvo_last_five_results = user_data_response.get('Salvo_last_five_results')
                    self.FOW_Wins = user_data_response.get('FOW_Wins')
                    self.FOW_Loss = user_data_response.get('FOW_Loss')
                    self.FOW_accuracy = user_data_response.get('FOW_accuracy')
                    self.FOW_last_five_results = user_data_response.get('FOW_last_five_results')
                    self.RR_Wins = user_data_response.get('RR_Wins')
                    self.RR_Loss = user_data_response.get('RR_Loss')
                    self.RR_accuracy = user_data_response.get('RR_accuracy')
                    self.RR_last_five_results = user_data_response.get('RR_last_five_results')
                    self.CTF_Wins = user_data_response.get('CTF_Wins')
                    self.CTF_Loss = user_data_response.get('CTF_Loss')
                    self.CTF_accuracy = user_data_response.get('CTF_accuracy')
                    self.CTF_last_five_results = user_data_response.get('CTF_last_five_results')
              if self.Level == 2+1 and self.SignOption == 1:
                if self.username != "" and  self.Password != "":
                  Human.SignedIn = PlayerAccount.signup(self.username,self.Password)
                  Human.SignedIn = PlayerAccount.signin(self.username,self.Password)
                if Human.SignedIn == True:
                    self.timer = 0
                    Human.username = self.username
                    Human.password = self.Password
                    user_data_response = PlayerAccount.get_user_data(self.username,self.Password)
                    #print('User data response:', user_data_response)
                    #self.accuracy = user_data_response.get('accuracy')
                    print(user_data_response)
                    self.longest_hit_streak = user_data_response.get('longest_hit_streak')
                    #self.total_games_played = user_data_response.get('total_games_played')
                    self.Classic_Wins = user_data_response.get('Classic_Wins')
                    self.Classic_Loss = user_data_response.get('Classic_Loss')
                    self.Classic_accuracy = user_data_response.get('Classic_accuracy')
                    self.Classic_last_five_results = user_data_response.get('Classic_last_five_results')
                    self.Salvo_Wins = user_data_response.get('Salvo_Wins')
                    self.Salvo_Loss = user_data_response.get('Salvo_Loss')
                    self.Salvo_accuracy = user_data_response.get('Salvo_accuracy')
                    self.Salvo_last_five_results = user_data_response.get('Salvo_last_five_results')
                    self.FOW_Wins = user_data_response.get('FOW_Wins')
                    self.FOW_Loss = user_data_response.get('FOW_Loss')
                    self.FOW_accuracy = user_data_response.get('FOW_accuracy')
                    self.FOW_last_five_results = user_data_response.get('FOW_last_five_results')
                    self.RR_Wins = user_data_response.get('RR_Wins')
                    self.RR_Loss = user_data_response.get('RR_Loss')
                    self.RR_accuracy = user_data_response.get('RR_accuracy')
                    self.RR_last_five_results = user_data_response.get('RR_last_five_results')
                    self.CTF_Wins = user_data_response.get('CTF_Wins')
                    self.CTF_Loss = user_data_response.get('CTF_Loss')
                    self.CTF_accuracy = user_data_response.get('CTF_accuracy')
                    self.CTF_last_five_results = user_data_response.get('CTF_last_five_results')
                 


    if self.Level < 3 and self.Level > 0:
      self.controls()
  def EditAccount(self):
    x = 70
    if self.Level == 0:
        SignOptionBox = GREEN
        SignOptionText = DARKGREEN
        UsernameBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
        UsernameBoxText = DARKGREEN
        PasswordBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
        PasswordBoxText = DARKGREEN
        SignInBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
    elif self.Level == 0+1:
        SignOptionBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
        SignOptionText = DARKGREEN
        UsernameBox = GREEN
        UsernameBoxText = DARKGREEN
        PasswordBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
        PasswordBoxText = DARKGREEN
        SignInBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
    elif self.Level == 1+1:
        SignOptionBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
        SignOptionText = DARKGREEN
        UsernameBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
        UsernameBoxText = DARKGREEN
        PasswordBox = GREEN
        PasswordBoxText = DARKGREEN
        SignInBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
    elif self.Level == 1+1+1:
        SignOptionBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
        SignOptionText = DARKGREEN
        UsernameBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
        UsernameBoxText = DARKGREEN
        PasswordBox = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
        PasswordBoxText = DARKGREEN
        SignInBox = GREEN
    pygame.draw.rect(SCREEN,SignOptionBox,(95,x,412,60),0,5,5)
    pygametext("Account Edit", 137, 80, 60, SignOptionText)
 
    #pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
    #pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)

    pygame.draw.rect(SCREEN,UsernameBox,(95,115+x,412,60),0,50,50)
    if self.username == "":
      pygametext("Edit Username?",140,198,60,UsernameBoxText)
    else:
       pygametext(self.username,(140),198,60,UsernameBoxText) #-(len(self.username)*11)
    pygame.draw.rect(SCREEN,PasswordBox,(95,115+150+x,412,60),0,50,50)
    if self.Password == "":
      pygametext("Edit Password?",140,198+x+x+10,60,PasswordBoxText)
    else:
      keys = pygame.key.get_pressed()
      hiddenpassword = ""
      for letter in self.Password:
        hiddenpassword += "*"
      pygametext((self.Password if keys[pygame.K_LEFT] and self.Level == 1+1 or keys[pygame.K_RIGHT] and self.Level == 1+1 else hiddenpassword),(140),198+x+x+10,60,PasswordBoxText)
    pygame.draw.rect(SCREEN,SignInBox,(109*1.5,115+150+x+x+40,412/1.5,60),0,5,5)
    pygametext("Save Edits",200,198+x+x+50+x,60,DARKGREEN)
    pygame.draw.rect(SCREEN,GREEN,(38,40,4,525),0,0,0)
    pygame.draw.rect(SCREEN,GREEN,(557,40,4,525),0,0,0)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP]:
              if self.Level > 0:
                  self.Level -= 1
                  pygame.time.wait(200)
    if keys[pygame.K_DOWN]:
              if self.Level < 3:
                  self.Level += 1 #GameVairables.menu == 2:
                  pygame.time.wait(200)
    if keys[pygame.K_ESCAPE]:
       Clearscreen(DARKGREEN)
       GameVairables.menu = 0
       self.timer = 0
    if keys[pygame.K_RETURN]:
              if self.Level == 2+1 and self.SignOption == 0:
                 if self.username != Human.username:
                    UsernameUpdate = self.username
                 else:
                    UsernameUpdate = None
                 #self.username = "MynansFlipFlop" #----------------------------------------------------------------------------------------
                 #self.Password= 'Password11' #----------------------------------------------------------------------------------------
                 editdata_response = PlayerAccount.update_user(Human.username,Human.password,UsernameUpdate,self.Password)
                 print(editdata_response)
                 self.edit = False
                 #Human.SignedIn = PlayerAccount.signin(self.username,self.Password)#self.
                 
    if self.Level < 3 and self.Level > 0:
      self.controls()
  def AccountMenurender(self):
    SemiDarkColour = max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)
    pygame.draw.rect(SCREEN,(max(GREEN[0] - 50, 0),max(GREEN[1] - 50, 0), max(GREEN[2] - 50, 0)),(380,40,170,80),0,0,0)
    pygame.draw.rect(SCREEN,GREEN,(40,110,350,10),0,0,0)
    pygametext(Human.username,60,60,50,GREEN)
    pygame.draw.rect(SCREEN,GREEN,(380,40,170,520),10,0,0)
    game_modes = ['Classic', 'Salvo', 'FOW', 'RR', 'CTF']
    attr_name = f"{game_modes[self.GamemodeInfo]}_last_five_results"
    last_five_results_list = getattr(self, attr_name).split(',')
    for x in range(len(last_five_results_list)):
      y=99
      y1 = 423
      pygame.draw.circle(SCREEN,GREEN,(500,280+(44*x)),20,5)
      if last_five_results_list[x] == "0":
        y = 100
        pygame.draw.line(SCREEN, GREEN, (66+y1, 170+(44*x)+y), (86+y1, 190+(44*x)+y), 8)
        pygame.draw.line(SCREEN, GREEN, (86+y1, 170+(44*x)+y), (66+y1, 190+(44*x)+y), 8)
        #print("test")
      else:
        y=99
        y1 = 423
        pygame.draw.line(SCREEN, GREEN, (87+y1, 170+(44*x)+y), (73+y1, 190+(44*x)+y), 6)
        pygame.draw.line(SCREEN, GREEN, (75+y1, 190+(44*x)+y), (60+y1, 180+(44*x)+y), 6)
    pygametext("W",425,290,50,GREEN)
    pygametext("I",438,290+40,50,GREEN)
    pygametext("N",431,290+40+40,50,GREEN)
    pygametext("S",432,290+40+40+42,50,GREEN)
    for x in range(0,5):
      pygame.draw.circle(SCREEN,SemiDarkColour,(405+(x*30),530),10,5)
   
    if self.timer == 500:
      if self.GamemodeInfo == 4:
        self.GamemodeInfo = 0
        self.timer = 0
      else:
         self.GamemodeInfo += 1
         self.timer = 0
         self.trail = True
      #self.GamemodeInfo= 0
    else:
      self.timer += 1
      #print(self.timer)
    VeryBrightColour = [0,0,0]
    for rgbValue in range(0,3):
      if GREEN[rgbValue] != 0:
        VeryBrightColour[rgbValue] = 255
    TimedChangeColour = max(GREEN[0] - (100-(self.timer//5)), 0),max(GREEN[1] - (100-(self.timer//5)), 0), max(GREEN[2] - (100-(self.timer//5)), 0)
    InverseTimedChangeColour = max(GREEN[0] - (self.timer//5), 0),max(GREEN[1] - (self.timer//5), 0), max(GREEN[2] - (self.timer//5), 0)
    pygame.draw.circle(SCREEN,VeryBrightColour,(405+(self.GamemodeInfo*30),530),10,0)
    pygame.draw.circle(SCREEN,TimedChangeColour,(405+((self.GamemodeInfo+1)*30 if self.GamemodeInfo+1 < 5 else 0*30),530),((self.timer//50)),0)
    if self.trail == True:
      pygame.draw.circle(SCREEN,InverseTimedChangeColour,(405+((self.GamemodeInfo-1)*30 if self.GamemodeInfo-1 >= 0 else 4*30),530),(10-(self.timer//50)),0)
    GamemodeListLineOne = ["Classic","Salvo","Fog Of","Rules","Capture"]
    GamemodeListLineTwo = ["","","War","Reversed","The Flag"]
    pygametext(GamemodeListLineOne[self.GamemodeInfo],398,60,40,DARKGREEN)
    pygametext(GamemodeListLineTwo[self.GamemodeInfo],398,60+30,40,DARKGREEN)
    attr_name = f"{game_modes[self.GamemodeInfo]}_Wins"
    pygametext("Won:",398,130,40,GREEN)
    pygametext(str(getattr(self, attr_name)),398+70,130,40,GREEN)
    attr_name = f"{game_modes[self.GamemodeInfo]}_Loss"
    pygametext("Lost:",398,130+30,40,GREEN)
    pygametext(str(getattr(self, attr_name)),398+70,130+30,40,GREEN)
    attr_name = f"{game_modes[self.GamemodeInfo]}_accuracy"
    pygametext("Hits:", 398, 130 + 30 + 30, 40, GREEN)
    accuracy_value = int(getattr(self, attr_name))  # Truncate the accuracy value
    pygametext(f"{accuracy_value}%", 398 + 70, 130 + 30 + 30, 40, GREEN)
    pygametext("Lifetime:",40,140,50,GREEN)
    pygametext("Games:",40,140+30+30,40,GREEN)
    TotalGames = 0
    for mode in game_modes:
      TotalGames += int(getattr(self, f"{mode}_Wins"))
      TotalGames += int(getattr(self, f"{mode}_Loss"))
    pygametext(str(TotalGames),145,140+30+30,40,GREEN)
    TotalWins = 0
    for mode in game_modes:
      TotalWins += int(getattr(self, f"{mode}_Wins"))
    pygametext("Wins:",40,140+30+30+30,40,GREEN)
    pygametext(str(TotalWins),120,140+30+30+30,40,GREEN)
    TotalLoss = 0
    for mode in game_modes:
      TotalLoss += int(getattr(self, f"{mode}_Loss"))
    pygametext("Loss:",40,140+30+30+30+30,40,GREEN)
    pygametext(str(TotalLoss),120,140+30+30+30+30,40,GREEN)
    TotalAccuracy = 0
    GamemodesAccuracyCounted = 0
    for mode in game_modes:
      if int(getattr(self, f"{mode}_accuracy")) != 0:
        TotalAccuracy += int(getattr(self, f"{mode}_accuracy"))
        GamemodesAccuracyCounted += 1
    try:
      TotalAccuracy = TotalAccuracy // GamemodesAccuracyCounted
    except ZeroDivisionError:
      TotalAccuracy = 0
    pygametext("Accuracy:",40,140+30+30+30+30+30,40,GREEN)
    pygametext(str(TotalAccuracy) +"%",180,140+30+30+30+30+30,40,GREEN)
    pygametext("Shot Streak:",40,140+30+30+30+30+30+30,40,GREEN)
    pygametext(str(self.longest_hit_streak),210,140+30+30+30+30+30+30,40,GREEN)
    pygame.draw.rect(SCREEN,(max(GREEN[0] - 50, 0),max(GREEN[1] - 50, 0), max(GREEN[2] - 50, 0)),(52+(self.AccountPageOption*100),420,100,65),0,0,0)
    for x in range(3):
      text = ["Logout","   Edit"," Delete"]
      pygame.draw.rect(SCREEN,GREEN,(52+(x*100),420,100,65),7,5,5)
      pygametext(text[x],60+(x*100),440,35,DARKGREEN)
   


    keys = pygame.key.get_pressed()
    if keys[pygame.K_RETURN]:
      if  self.AccountPageOption == 0:
        Clearscreen(DARKGREEN)
        GameVairables.menu = 0
        self.dataFetched = False
        self.trail = False
        self.GamemodeInfo = 0
        self.timer = 0
        Human.SignedIn = False
        Human.username = "Player 1"
        Human.password = ""
        self.username = ""
        self.Password = ""
      if  self.AccountPageOption == 1:
        Clearscreen(DARKGREEN)
        self.edit = True
      if self.AccountPageOption == 2:
        Clearscreen(DARKGREEN)
        GameVairables.menu = 0
        self.dataFetched = False
        self.trail = False
        self.GamemodeInfo = 0
        self.timer = 0
        Human.SignedIn = False
        PlayerAccount.delete_user(Human.username,Human.password)
        Human.username = "Player 1"
        Human.password = ""
        self.username = ""
        self.Password = ""

    if keys[ord('d')] or keys[pygame.K_RIGHT]:
      if self.AccountPageOption +1 > 2:
        pass
      else:
         self.AccountPageOption += 1
         pygame.time.wait(200)

    if keys[ord('a')] or keys[pygame.K_LEFT]:
      if self.AccountPageOption -1 < 0:
        pass
      else:
         self.AccountPageOption -= 1
         pygame.time.wait(200)
    if keys[pygame.K_ESCAPE]:
      Clearscreen(DARKGREEN)
      GameVairables.menu = 0
      self.dataFetched = False
      self.trail = False
      self.GamemodeInfo = 0
      self.timer = 0

  def render(self):
    if Human.SignedIn == False:
      self.SignInrender()
    elif self.edit == True:
      self.EditAccount()
    else:
      self.AccountMenurender()


class OptionsMenu:
    def __init__(self):
        self.Level = 1
        self.ColourSelected = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[ord('d')] or keys[pygame.K_RIGHT]:
              if self.Level == 1:
                for track_name in music_manager.music_tracks:
                  if track_name.startswith("M_"):
                    music_manager.set_volume(track_name,(music_manager.get_volume("M_Menu")+0.01))
              elif self.Level == 2:
                for track_name in music_manager.music_tracks:
                  if track_name.startswith("SE_"):
                    music_manager.set_volume(track_name,(music_manager.get_volume("SE_Radar")+0.01))
              elif self.Level == 3:
                if self.ColourSelected < 4:
                  self.ColourSelected += 1
                else:
                  self.ColourSelected = 4
                pygame.time.wait(175)
              pygame.time.wait(25)
        if keys[ord('a')] or keys[pygame.K_LEFT]:
            if self.Level == 1:
                for track_name in music_manager.music_tracks:
                  if track_name.startswith("M_"):
                    music_manager.set_volume(track_name,(music_manager.get_volume("M_Menu")-0.01))
            elif self.Level == 2:
                for track_name in music_manager.music_tracks:
                  if track_name.startswith("SE_"):
                    music_manager.set_volume(track_name,(music_manager.get_volume("SE_Radar")-0.01))
            elif self.Level == 3:
              if self.ColourSelected > 0:
                self.ColourSelected -= 1
                pygame.time.wait(175)
            pygame.time.wait(25)
        if keys[pygame.K_w] or keys[pygame.K_UP]:
              if self.Level > 1:
                  self.Level -= 1
              pygame.time.wait(200)
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
              if self.Level < 3:
                  self.Level += 1
              pygame.time.wait(200)
        if keys[pygame.K_ESCAPE]:
          GameVairables.menu = 0
          global GREEN,DARKGREEN
          Clearscreen(DARKGREEN)
        if self.ColourSelected == 0: #G","R","B","Y","P"
          GREEN = (0,200,0)
          DARKGREEN = (0,50,0)
        elif self.ColourSelected == 1:
          GREEN = (200,0,0)
          DARKGREEN = (70,0,0)
        elif self.ColourSelected == 2:
          GREEN = (0,0,255)
          DARKGREEN = (0,0,100)
        elif self.ColourSelected == 3:
          GREEN = (200,200,0)
          DARKGREEN = (50,50,0)
        elif self.ColourSelected == 4:
          GREEN = (200,0,200)
          DARKGREEN = (50,0,50)
        #print(self.Level)

    def render(self):
        pygame.draw.rect(SCREEN,GREEN,(38,38,80,525),0,5,5) #38,40,525,70
        m = 18
        pygametext("O",52,55+m,95,DARKGREEN)
        pygametext("P",52,120+m,95,DARKGREEN)
        pygametext("T",52,120+65+m,95,DARKGREEN)
        pygametext("I",63,120+65+65+m,95,DARKGREEN)
        pygametext("O",52,120+65+65+65+m,95,DARKGREEN)
        pygametext("N",52,120+65+65+65+65+m,95,DARKGREEN)
        pygametext("S",52,120+65+65+65+65+65+m,95,DARKGREEN)
        #---------------------------------------------------------
        try:
          if self.Level == 1:
             MenuMusicColour = GREEN
          else:
             MenuMusicColour = (max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0))
          pygame.draw.rect(SCREEN,MenuMusicColour,(140,115,412,20),0,50,50)
          pygame.draw.circle(SCREEN,DARKGREEN,(150+(388*(music_manager.get_volume("M_Menu"))),125),12)#388 /100 = 3.88
          pygame.draw.polygon(SCREEN, MenuMusicColour, [((150+(388*(music_manager.get_volume("M_Menu")))), 125-12+15), ((150+(388*(music_manager.get_volume("M_Menu"))))-12*1, 125+6+15), ((150+(388*(music_manager.get_volume("M_Menu"))))+12*1, 125+6+15)])
          pygame.draw.rect(SCREEN,MenuMusicColour,(130+(388*(music_manager.get_volume("M_Menu"))),145,40,40),0,10,10) #518
          VolumeLabel = (music_manager.get_volume("M_Menu") * 100) // 1
          if len(f"{VolumeLabel:.0f}") == 1:
            TextXValue = 145
          elif len(f"{VolumeLabel:.0f}") == 2:
            TextXValue = 138
          else:
            TextXValue = 131
          pygametext(f"{VolumeLabel:.0f}",(TextXValue+(388*(music_manager.get_volume("M_Menu")))),155,33,DARKGREEN)
        except TypeError:
          pass
        pygametext("Music Volume:",230,70,50,MenuMusicColour)
        #-----------------------------------------------------------------------------
        y=115
       
        if self.Level == 2:
             SoundEffectColour = GREEN
        else:
             SoundEffectColour = (max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0))
        try:
          pygame.draw.rect(SCREEN,SoundEffectColour,(140,115+y,412,20),0,50,50)
          pygame.draw.circle(SCREEN,DARKGREEN,(150+(388*(music_manager.get_volume("SE_Radar"))),125+y),12)#388 /100 = 3.88
          pygame.draw.polygon(SCREEN, SoundEffectColour, [((150+(388*(music_manager.get_volume("SE_Radar")))), 125-12+15+y), ((150+(388*(music_manager.get_volume("SE_Radar"))))-12*1, 125+6+15+y), ((150+(388*(music_manager.get_volume("SE_Radar"))))+12*1, 125+6+15+y)])
          pygame.draw.rect(SCREEN,SoundEffectColour,(130+(388*(music_manager.get_volume("SE_Radar"))),145+y,40,40),0,10,10) #518
          VolumeLabel = (music_manager.get_volume("SE_Radar") * 100) // 1
          if len(f"{VolumeLabel:.0f}") == 1:
            TextXValue = 145
          elif len(f"{VolumeLabel:.0f}") == 2:
            TextXValue = 138
          else:
            TextXValue = 131
          pygametext(f"{VolumeLabel:.0f}",(TextXValue+(388*(music_manager.get_volume("SE_Radar")))),155+y,33,DARKGREEN)
        except TypeError:
          pass
        pygametext("Sound Effect Volume:",180,70+y,50,SoundEffectColour)
        #--------------------------------------------------------------------------------
        ColourOptions = ["G","R","B","Y","P"]
        if self.Level == 3:
             GameColoursColour = GREEN
        else:
             GameColoursColour = (max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0))
        for ColourScheme in range(5):
          pygame.draw.rect(SCREEN,GameColoursColour,(145+(ColourScheme*80),320,70,240),10,0,0)
          pygametext(ColourOptions[ColourScheme],157+(ColourScheme*80),420,90,GameColoursColour)
        pygame.draw.rect(SCREEN,GameColoursColour,(145+(self.ColourSelected*80),320,70,240),0,0,0)
        pygametext(ColourOptions[self.ColourSelected],157+(self.ColourSelected*80),420,90,DARKGREEN)
        return self.update()
options_menu = OptionsMenu()

xarrow = 212
yarrow = 88
menuoption = 1
def Mainmenu():
  global seconds, prevsecond, counter,xarrow,yarrow,menuoption
  if seconds != prevsecond or counter == 1:
    Menurender()
    prevsecond = seconds
  drawGrid(33,35,35,1)
  drawGrid(33,233,35,1)
  drawGrid(33,233,35+(33*6),1)
  drawGrid(33,35,35+(33*6),1) #16x16 grid
  z = 25
  w = -3
  for crd in cood:
    row = [crd[0],crd[1]]
    SemiDarkColour = max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)
    VeryBrightColour = [0,0,0]
    for rgbValue in range(0,3):
      if GREEN[rgbValue] != 0:
        VeryBrightColour[rgbValue] = 255
    pygame.draw.rect(SCREEN, SemiDarkColour, (60-z + (row[1]*33),65-w+(row[0]*33), 33, 33),0,0,0)
    pygame.draw.rect(SCREEN, DARKGREEN, (61-z+(row[1]*33),77-w+(row[0]*33),31,10), 0)
    pygame.draw.rect(SCREEN, DARKGREEN, (71-z+(row[1]*33),66-w+(row[0]*33),10,31), 0)
    pygame.draw.circle(SCREEN,DARKGREEN,(76.8-z+(row[1]*33),82-w+(row[0]*33)),12)
  for crd in cood2:
    row = [crd[0],crd[1]]
    pygame.draw.rect(SCREEN, SemiDarkColour, (60-z + (row[1]*33),65-w+(row[0]*33), 33, 33),0,0,0)
    pygame.draw.rect(SCREEN, DARKGREEN, (61-z+(row[1]*33),77-w+(row[0]*33),31,10), 0)
    pygame.draw.rect(SCREEN, DARKGREEN, (71-z+(row[1]*33),66-w+(row[0]*33),10,31), 0)
    pygame.draw.circle(SCREEN,DARKGREEN,(76.8-z+(row[1]*33),82-w+(row[0]*33)),12)
    pygame.draw.circle(SCREEN,VeryBrightColour,(76-z+(row[1]*33),82-w+(row[0]*33)),6)
  for crd in cood3:
    row = [crd[0],crd[1]]
    pygame.draw.rect(SCREEN, SemiDarkColour, (60-z + (row[1]*33),65-w+(row[0]*33), 33, 33),0,0,0)
    pygame.draw.rect(SCREEN, GREEN, (61-z+(row[1]*33),77-w+(row[0]*33),31,10), 0)
    pygame.draw.rect(SCREEN, GREEN, (71-z+(row[1]*33),66-w+(row[0]*33),10,31), 0)
    pygame.draw.circle(SCREEN,GREEN,(76.8-z+(row[1]*33),82-w+(row[0]*33)),12)
    pygame.draw.circle(SCREEN,GREEN,(76-z+(row[1]*33),82-w+(row[0]*33)),6)
     
  pygame.draw.rect(SCREEN, DARKGREEN, (200-33, 35, 33*8, 33*16),0,0,0)
  pygame.draw.rect(SCREEN, GREEN, (200-33, 35, 33*8, 33*16),12,0,0)
  pygametext("Aqua Assault",(300- (len("aqua assault")*8.2)),165,46,GREEN)
  pygame.draw.rect(SCREEN, GREEN, (210,100,180,50), 7,10)
  pygame.draw.rect(SCREEN, DARKGREEN, (330,100,60,50), 0,0)
  u = 1
  ui = 3.5
  pygame.draw.polygon(SCREEN, GREEN, [(325+ui, 102+u), (375+ui, 123+u), (325+ui, 145+u)],7)
  pygame.draw.rect(SCREEN, DARKGREEN, (315,109,20,33), 0,5)
  pygame.draw.rect(SCREEN, GREEN, (250,100,60,50), 7,15)
  u = 33
  pygame.draw.rect(SCREEN, GREEN, (250+u/2,100+u/2,60-u,50-u), 4,3)
  pygame.draw.rect(SCREEN, GREEN, (250+u/0.6,100+u/2,53-u,50-u), 4,3)
  pygame.draw.rect(SCREEN, GREEN, (250-u+20,100+u/2,53-u,50-u), 4,3)
  pygame.draw.rect(SCREEN, GREEN, (250-u+10,102+u/2,53-u-5,50-u-12), 0,3)
  pygame.draw.rect(SCREEN, GREEN, (250-u+10,110+u/2,53-u-5,50-u-12), 0,3)
  pygame.draw.rect(SCREEN, GREEN, (250+u+38,102+u/2,53-u-5,50-u-12), 0,3)
  pygame.draw.rect(SCREEN, GREEN, (250+u+38,110+u/2,53-u-5,50-u-12), 0,3)
  MenuOptions = ["Play Game","Account","Intel","Options","Quit"]
  for x in range(0,5):
    if x == menuoption-1:
      pygame.draw.rect(SCREEN,GREEN , (220, 290+(x*42), 158, 40),5,0,0)
      pygametext(MenuOptions[x],(300- (len(MenuOptions[x])*8.2)),300+(x*42),40,GREEN)
    else:
      pygame.draw.rect(SCREEN,(max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 30, 0)) , (220, 290+(x*42), 158, 40),5,0,0)
      pygametext(MenuOptions[x],(300- (len(MenuOptions[x])*8.2)),300+(x*42),40,(max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 30, 0)))
  keys = pygame.key.get_pressed()
  if keys[ord('s')] or keys[pygame.K_DOWN]:
    if menuoption < 5:
      menuoption += 1
    pygame.time.wait(200)
  if keys[ord('w')] or keys[pygame.K_UP]:#212,252,292,332,372
    if menuoption > 1:
      menuoption -= 1
      pygame.time.wait(200)
  if keys[pygame.K_RETURN]:
    GameVairables.menu = menuoption
    keys = None
    Clearscreen(DARKGREEN)
    pygame.time.wait(300)
 
def ClassicGameplay(DefeatDisplayColourct=True):
  drawText()
  Human.boatPresent()
  Enemy.shotPresent()
  Human.shotPresent()
  drawGrid(33,60,65,1) #big board
  drawGrid(15,60,415,2) #small left board
  Heatmap(matrix)
  drawGrid(15,402,415,2) #small right board
  #pygametext("Opponent's HeatMap",397,398,23)
  Selector(33,60,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
  fade = 255
  battlelog(fade)
  drawTargets()
  pygame.draw.rect(SCREEN, GREEN, (395, 65, 160, 166),5,0,0)
  drawFleet()
  if DefeatDisplayColourct == False:
    #two tone - shift to one that has lead
    pygame.draw.rect(SCREEN, GREEN, (291, 400, 100, 167),4,0,0)
    if Enemy.EmptySpace > Human.EmptySpace:  
      pygame.draw.rect(SCREEN, GREEN, (291, 400, 100, 82),0,0,0)
      EnemyDisplayColour = DARKGREEN
      HumanDisplayColour = GREEN
    elif Enemy.EmptySpace < Human.EmptySpace:  
      pygame.draw.rect(SCREEN, GREEN, (291, 400+82, 100, 82),0,0,0)
      EnemyDisplayColour = GREEN
      HumanDisplayColour = DARKGREEN
    else:
      EnemyDisplayColour = GREEN
      HumanDisplayColour = GREEN
    pygametext(str(Human.EmptySpace),325,422,40,EnemyDisplayColour)
    pygametext(str("Enemy"),307,451,30,EnemyDisplayColour)
    pygametext(str(Enemy.EmptySpace),325,519,40,HumanDisplayColour)
    pygametext(str("You"),321,490,30,HumanDisplayColour)
  keys = pygame.key.get_pressed()
  if keys[ord('s')] or keys[pygame.K_DOWN]:
      if GameVairables.xx < 10:
        GameVairables.xx += 1
        pygame.time.wait(100)
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
  if keys[ord('d')] or keys[pygame.K_RIGHT]:
      if GameVairables.yy < 10:
        GameVairables.yy += 1
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
        pygame.time.wait(100)
      #Selector(33,60,65,1,GameVairables.xx-1,GameVairables.yy-1)
  if keys[ord('w')] or keys[pygame.K_UP]:
      if GameVairables.xx > 1:
        GameVairables.xx -= 1
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
        pygame.time.wait(100)
      #Selector(33,60,65,1,GameVairables.xx-1,GameVairables.yy-1)
  if keys[ord('a')] or keys[pygame.K_LEFT]:
      if GameVairables.yy > 1:
        GameVairables.yy -= 1
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
        pygame.time.wait(100)
      #Selector(33,60,65,1,GameVairables.xx-1,GameVairables.yy-1)
  if keys[pygame.K_RETURN]:
        #print("Enter key is pressed")
      result = Shot(GameVairables.xx,GameVairables.yy) #result =
      if result == True:
        ComputerPlayerShot(DefeatDisplayColourct)
      Enemy.shotPresent()
      drawGrid(33,60,65,1)
      Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
      fade = 40
      battlelog(fade)
      pygame.display.update()
      pygame.time.wait(100)
  if DefeatDisplayColourct == False:
    Enemy.EmptySpace = 0
    Human.EmptySpace = 0
    for row in range(len(Enemy.BattleshipBoard)):
      for coloumn in range(len(Enemy.BattleshipBoard)):
        if Enemy.BattleshipBoard[row][coloumn] == "+":
          Enemy.EmptySpace += 1
    for row in range(len(Human.BattleshipBoard)):
      for coloumn in range(len(Human.BattleshipBoard)):
        if Human.BattleshipBoard[row][coloumn] == "+":
          Human.EmptySpace += 1
    #pygame.draw.rect(SCREEN, DARKGREEN, (395, 65, 160, 166),5,0,0)
    #two tone - shift to one that has lead
    pygame.display.update()
    if Enemy.EmptySpace == 0:
      Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
      pygame.display.update()
      pygame.time.wait(2000)
      Clearscreen(DARKGREEN)
      pygame.time.wait(2000)
      return "Win"
    if Human.EmptySpace == 0:
      Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
      pygame.display.update()
      pygame.time.wait(3000) #previously used time.sleep() - caused crash as its a blocking call
      Clearscreen(DARKGREEN)
      pygame.time.wait(2000)
      return "Lose"
  if len(Enemy.BattleshipHits) == len(Enemy.BattleshipHealth):
    Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
    pygame.display.update()
    pygame.time.wait(2000)
    Clearscreen(DARKGREEN)
    pygame.time.wait(2000)
    #print("you won... yay?")
    return "Win"
    GameVairables.menu = 0
    GameVairables.gamemode = None
  if len(Human.BattleshipHits) == len(Human.BattleshipHealth):
    Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
    pygame.display.update()
    pygame.time.wait(3000) #previously used time.sleep() - caused crash as its a blocking call
    Clearscreen(DARKGREEN)
    pygame.time.wait(2000)
    #print("Ai won... yay!")
    return "Lose"
    GameVairables.menu = 0
    GameVairables.gamemode = None

def Draw_Fog(FogCentreLocation):
    # Define the 10x10 board dimensions
    board_size = 10
    # Loop through the entire 10x10 board
    cell_size = 33
    SemiDarkColour = max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)
    # Loop through the entire 10x10 board
    for i in range(board_size):
        for j in range(board_size):
            # Calculate the offset from the FogCentreLocation
            dx = i - FogCentreLocation[0] +1
            dy = j - FogCentreLocation[1] +1
           
            # Check if the current square (i, j) is not within the 3x3 foggy area around the center
            if not (-1 <= dx <= 1 and -1 <= dy <= 1):
                # Calculate the position for drawing, making sure it's within the board
                x = 60 + (j * cell_size)
                y = 65 + (i * cell_size)
                pygame.draw.rect(SCREEN, SemiDarkColour, (x, y, cell_size, cell_size), 0, 0, 0)
    drawGrid(33,60,65,1)


def FogOfWarGameplay():
  drawText()
  Human.boatPresent()
  Enemy.shotPresent()
  Human.shotPresent()
  drawGrid(33,60,65,1) #big board
  drawGrid(15,60,415,2) #small left board
  Heatmap(matrix)
  drawGrid(15,402,415,2) #small right board
  #pygametext("Opponent's HeatMap",397,398,23)
  fade = 255
  battlelog(fade)
  drawTargets()
  pygame.draw.rect(SCREEN, GREEN, (395, 65, 160, 166),5,0,0)
  drawFleet()
  #pygame.draw.rect(SCREEN, GREEN, (291, 400, 100, 167),4,0,0)
  if Human.FogCentreLocation != None:
    Draw_Fog(Human.FogCentreLocation)
  else:
     pass
  #pygame.draw.rect(SCREEN, DARKGREEN, (50, 50, 100, 100),0,0,0)
  Selector(33,60,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
  keys = pygame.key.get_pressed()
  if keys[ord('s')] or keys[pygame.K_DOWN]:
      if GameVairables.xx < 10:
        GameVairables.xx += 1
        pygame.time.wait(100)
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
  if keys[ord('d')] or keys[pygame.K_RIGHT]:
      if GameVairables.yy < 10:
        GameVairables.yy += 1
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
        pygame.time.wait(100)
      #Selector(33,60,65,1,GameVairables.xx-1,GameVairables.yy-1)
  if keys[ord('w')] or keys[pygame.K_UP]:
      if GameVairables.xx > 1:
        GameVairables.xx -= 1
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
        pygame.time.wait(100)
      #Selector(33,60,65,1,GameVairables.xx-1,GameVairables.yy-1)
  if keys[ord('a')] or keys[pygame.K_LEFT]:
      if GameVairables.yy > 1:
        GameVairables.yy -= 1
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
        pygame.time.wait(100)
      #Selector(33,60,65,1,GameVairables.xx-1,GameVairables.yy-1)
  if keys[pygame.K_RETURN]:
      Human.FogCentreLocation = (GameVairables.xx,GameVairables.yy)
      result = Shot(GameVairables.xx,GameVairables.yy) #result =
      if result == True:
        ComputerPlayerShot()
      #Enemy.shotPresent()
      drawGrid(33,60,65,1)
      Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
      fade = 40
      #Draw_Fog(Human.FogCentreLocation)
      battlelog(fade)
      pygame.display.update()
      pygame.time.wait(100)
  if len(Enemy.BattleshipHits) == len(Enemy.BattleshipHealth):
    Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
    pygame.display.update()
    pygame.time.wait(2000)
    Clearscreen(DARKGREEN)
    pygame.time.wait(2000)
    #print("you won... yay?")
    return "Win"
  if len(Human.BattleshipHits) == len(Human.BattleshipHealth):
    Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
    pygame.display.update()
    pygame.time.wait(3000) #previously used time.sleep() - caused crash as its a blocking call
    Clearscreen(DARKGREEN)
    pygame.time.wait(2000)
    #print("Ai won... yay!")
    return "Lose"
 

def CaptureTheFlagGameplay(FlagShip,FlagShipSize):
  drawText()
  Human.boatPresent()
  Enemy.shotPresent()
  Human.shotPresent()
  drawGrid(33,60,65,1) #big board
  drawGrid(15,60,415,2) #small left board
  Heatmap(matrix)
  drawGrid(15,402,415,2) #small right board
  #pygametext("Opponent's HeatMap",397,398,23)
  Selector(33,60,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
  fade = 255
  battlelog(fade)
  drawTargets()
  pygame.draw.rect(SCREEN, GREEN, (395, 65, 160, 166),5,0,0)
  pygame.draw.rect(SCREEN, GREEN, (291, 400, 100, 50),0,0,0)
  pygame.draw.rect(SCREEN, GREEN, (291, 400, 100, 167),4,0,0)
  pygametext("Flag-Ship",295,412,30,DARKGREEN)
  if FlagShip != "AircraftCarrier":
    pygametext(FlagShip,296,460,25,GREEN)
  else:
     pygametext("Aircraft",296,460,25,GREEN)
     pygametext("Carrier",296,480,25,GREEN)
  pygame.draw.rect(SCREEN, GREEN, (300, 516, 60, 30),0,0,0)
  pygame.draw.rect(SCREEN, GREEN, (300, 503, 10, 60),0,0,0)
  pygame.draw.circle(SCREEN,GREEN,(305,510),10)
  pygametext(str(FlagShipSize),325,523,30,DARKGREEN)
  drawFleet()
  keys = pygame.key.get_pressed()
  if keys[ord('s')] or keys[pygame.K_DOWN]:
      if GameVairables.xx < 10:
        GameVairables.xx += 1
        pygame.time.wait(100)
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
  if keys[ord('d')] or keys[pygame.K_RIGHT]:
      if GameVairables.yy < 10:
        GameVairables.yy += 1
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
        pygame.time.wait(100)
      #Selector(33,60,65,1,GameVairables.xx-1,GameVairables.yy-1)
  if keys[ord('w')] or keys[pygame.K_UP]:
      if GameVairables.xx > 1:
        GameVairables.xx -= 1
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
        pygame.time.wait(100)
      #Selector(33,60,65,1,GameVairables.xx-1,GameVairables.yy-1)
  if keys[ord('a')] or keys[pygame.K_LEFT]:
      if GameVairables.yy > 1:
        GameVairables.yy -= 1
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
        pygame.time.wait(100)
      #Selector(33,60,65,1,GameVairables.xx-1,GameVairables.yy-1)
  if keys[pygame.K_RETURN]:
        #print("Enter key is pressed")
      result = Shot(GameVairables.xx,GameVairables.yy) #result =
      if result == True:
        ComputerPlayerShot()
      Enemy.shotPresent()
      drawGrid(33,60,65,1)
      Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
      fade = 40
      battlelog(fade)
      pygame.display.update()
      #pygame.time.wait(100)
  if getattr(Enemy, FlagShip, [])[0] == "Sunk":
    Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
    pygame.display.update()
    pygame.time.wait(2000)
    Clearscreen(DARKGREEN)
    pygame.time.wait(2000)
    #print("you won... yay?")
    return "Win"
    GameVairables.menu = 0
    GameVairables.gamemode = None
  elif getattr(Human, FlagShip, [])[0] == "Sunk":
    Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
    pygame.display.update()
    pygame.time.wait(3000) #previously used time.sleep() - caused crash as its a blocking call
    Clearscreen(DARKGREEN)
    pygame.time.wait(2000)
    #print("Ai won... yay!")
    return "Lose"
    GameVairables.menu = 0
    GameVairables.gamemode = None

def SalvoGameplay():
  if Human.Ammo == 0 and Enemy.Ammo == 0:
    Human.Ammo = 1
    if Human.Cruiser[0] == "Sunk":
        Human.Ammo += 1
    if Human.Submarine[0] == "Sunk":
        Human.Ammo += 1
    if Human.Battleship[0] == "Sunk":
        Human.Ammo += 1
    if Human.Destroyer[0] == "Sunk":
        Human.Ammo += 1
    if Human.AircraftCarrier[0] == "Sunk":
        Human.Ammo += 1
    Enemy.Ammo= 1
    if Enemy.Cruiser[0] == "Sunk":
        Enemy.Ammo += 1
    if Enemy.Submarine[0] == "Sunk":
        Enemy.Ammo += 1
    if Enemy.Battleship[0] == "Sunk":
        Enemy.Ammo += 1
    if Enemy.Destroyer[0] == "Sunk":
        Enemy.Ammo += 1
    if Enemy.AircraftCarrier[0] == "Sunk":
        Enemy.Ammo += 1
  drawText()
  Human.boatPresent()
  Enemy.shotPresent()
  Human.shotPresent()
  drawGrid(33,60,65,1) #big board
  drawGrid(15,60,415,2) #small left board
  Heatmap(matrix)
  drawGrid(15,402,415,2) #small right board
  #pygametext("Opponent's HeatMap",397,398,23)
  Selector(33,60,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
  fade = 255
  battlelog(fade)
  drawTargets()
  pygame.draw.rect(SCREEN, GREEN, (395, 65, 160, 166),5,0,0)
  drawFleet()
    #two tone - shift to one that has lead
  pygame.draw.rect(SCREEN, GREEN, (291, 400, 100, 167),4,0,0)
  if Enemy.Ammo > 0:  
      pygame.draw.rect(SCREEN, GREEN, (291, 400, 100, 82),0,0,0)
      EnemyDisplayColour = DARKGREEN
      HumanDisplayColour = GREEN
  elif 0 < Human.Ammo:  
      pygame.draw.rect(SCREEN, GREEN, (291, 400+82, 100, 82),0,0,0)
      EnemyDisplayColour = GREEN
      HumanDisplayColour = DARKGREEN
  else:
      EnemyDisplayColour = GREEN
      HumanDisplayColour = GREEN
  pygametext(str(Enemy.Ammo),325,422,40,EnemyDisplayColour)
  pygametext(str("Enemy"),307,451,30,EnemyDisplayColour)
  pygametext(str(Human.Ammo),325,519,40,HumanDisplayColour)
  pygametext(str("You"),321,490,30,HumanDisplayColour)
  keys = pygame.key.get_pressed()
  if keys[ord('s')] or keys[pygame.K_DOWN]:
      if GameVairables.xx < 10:
        GameVairables.xx += 1
        pygame.time.wait(100)
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
  if keys[ord('d')] or keys[pygame.K_RIGHT]:
      if GameVairables.yy < 10:
        GameVairables.yy += 1
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
        pygame.time.wait(100)
      #Selector(33,60,65,1,GameVairables.xx-1,GameVairables.yy-1)
  if keys[ord('w')] or keys[pygame.K_UP]:
      if GameVairables.xx > 1:
        GameVairables.xx -= 1
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
        pygame.time.wait(100)
      #Selector(33,60,65,1,GameVairables.xx-1,GameVairables.yy-1)
  if keys[ord('a')] or keys[pygame.K_LEFT]:
      if GameVairables.yy > 1:
        GameVairables.yy -= 1
          #print("(",GameVairables.xx,",",GameVairables.yy,")")
        pygame.time.wait(100)
      #Selector(33,60,65,1,GameVairables.xx-1,GameVairables.yy-1)
  if keys[pygame.K_RETURN]:
      if Human.Ammo > 0:
        result = Shot(GameVairables.xx,GameVairables.yy) #result =
        if result == True:
          Human.Ammo -= 1
          print("P SHOT")
          Enemy.shotPresent()
          Human.shotPresent()
          pygame.display.update()
      if Human.Ammo == 0:
        while Enemy.Ammo > 0:
          ComputerPlayerShot()
          Enemy.Ammo -= 1
          print("E SHOT")
          Enemy.shotPresent()
          Human.shotPresent()
      drawGrid(33,60,65,1)
      Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
      fade = 40
      battlelog(fade)
      pygame.display.update()
      pygame.time.wait(100)
    #pygame.draw.rect(SCREEN, DARKGREEN, (395, 65, 160, 166),5,0,0)
    #two tone - shift to one that has lead
  if len(Enemy.BattleshipHits) == len(Enemy.BattleshipHealth):
    Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
    pygame.display.update()
    pygame.time.wait(2000)
    Clearscreen(DARKGREEN)
    pygame.time.wait(2000)
    #print("you won... yay?")
    return "Win"
  if len(Human.BattleshipHits) == len(Human.BattleshipHealth):
    Selector(33,600,65,GameVairables.xx-1,GameVairables.yy-1,GREEN)
    pygame.display.update()
    pygame.time.wait(3000) #previously used time.sleep() - caused crash as its a blocking call
    Clearscreen(DARKGREEN)
    pygame.time.wait(2000)
    #print("Ai won... yay!")
    return "Lose"
#----------------------------------------------------------------------------------------------------------------
#vgames = Human.lastGames()
#vgamescomp = [random.randint(0,1),random.randint(0,1),random.randint(0,1),random.randint(0,1),random.randint(0,1)]
#vgamescomp = [0,0,0,0,0]
class VSScreen():
  def __init__(self):
    self.PlayerVGames = None
    self.ComputerVGames = None
  def Reset(self):
    self.PlayerVGames = None
    self.ComputerVGames = None
  def Render(self):
    if self.PlayerVGames == None:
      if Human.SignedIn == True: #need to do this just one!
        user_data_response = PlayerAccount.get_user_data(Human.username,Human.password) #getattr(self,
        if GameVairables.gamemode == 0:
          gamemode = "Classic"
        elif GameVairables.gamemode == 1:
          gamemode = "Salvo"
        elif GameVairables.gamemode == 2:
          gamemode = "FOW"
        elif GameVairables.gamemode == 3:
          gamemode = "RR"
        elif GameVairables.gamemode == 4:
          gamemode = "CTF"
        five_results = user_data_response.get(f"{gamemode}_last_five_results")
        last_five_results_list = [int(result) for result in five_results.split(',')]
        self.PlayerVGames = Human.lastGames(last_five_results_list)
      else:
        self.PlayerVGames = Human.lastGames()
      if self.ComputerVGames == None:
        self.ComputerVGames = [random.randint(0,1),random.randint(0,1),random.randint(0,1),random.randint(0,1),random.randint(0,1)]
    x = 30
    pygame.draw.polygon(SCREEN, GREEN, [(40, 40), (417+x, 40), (139+x, 80+477), (40, 80+477)], 0)
    pygame.draw.line(SCREEN,DARKGREEN,(50,50),(400+x,50),4)
    pygame.draw.line(SCREEN,GREEN,(420+x,50),(530+x,50),4)
    pygame.draw.line(SCREEN,DARKGREEN,(50,70+477),(195-x,70+477),4)
    pygame.draw.line(SCREEN,GREEN,(213-x,70+477),(530+x,70+477),4)
    pygametext(Human.username,60,100,50,DARKGREEN)
    pygametext("V",270,260,100,DARKGREEN)
    pygametext("S",300,300,100,GREEN)
    pygametext(Enemy.username,225,500,50,GREEN)
    for x in range(len(self.PlayerVGames)):
      pygame.draw.circle(SCREEN,DARKGREEN,(76,180+(44*x)),20,5)
      if self.PlayerVGames[x] == 0:
        pygame.draw.line(SCREEN, DARKGREEN, (66, 170+(44*x)), (86, 190+(44*x)), 8)
        pygame.draw.line(SCREEN, DARKGREEN, (86, 170+(44*x)), (66, 190+(44*x)), 8)
      else:
        pygame.draw.line(SCREEN, DARKGREEN, (87, 170+(44*x)), (73, 190+(44*x)), 6)
        pygame.draw.line(SCREEN, DARKGREEN, (75, 190+(44*x)), (60, 180+(44*x)), 6)
    for x in range(len(self.ComputerVGames)):
      y=99
      y1 = 423
      pygame.draw.circle(SCREEN,GREEN,(500,280+(44*x)),20,5)
      if self.ComputerVGames[x] == 0:
        y = 100
        pygame.draw.line(SCREEN, GREEN, (66+y1, 170+(44*x)+y), (86+y1, 190+(44*x)+y), 8)
        pygame.draw.line(SCREEN, GREEN, (86+y1, 170+(44*x)+y), (66+y1, 190+(44*x)+y), 8)
      else:
        y=99
        y1 = 423
        pygame.draw.line(SCREEN, GREEN, (87+y1, 170+(44*x)+y), (73+y1, 190+(44*x)+y), 6)
        pygame.draw.line(SCREEN, GREEN, (75+y1, 190+(44*x)+y), (60+y1, 180+(44*x)+y), 6)
 

def Draw_Classic(MainColour=None,XChange=0):
  if MainColour == None:
     MainColour=(max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0))
  x = XChange*270
  pygame.draw.circle(SCREEN,MainColour,(219.9+x,430),50)
  pygame.draw.circle(SCREEN,MainColour,(219.9+x,430-80),35)
  pygame.draw.circle(SCREEN,MainColour,(369+x,430),50)
  pygame.draw.rect(SCREEN, DARKGREEN, (169+x, 180+40+250, 250, 250),0,0,0)
  pygame.draw.rect(SCREEN, MainColour, (319+x, 180+150, 88, 50),0,5,5)
  pygame.draw.rect(SCREEN, MainColour, (349+x, 180+130, 30, 60),0,0,0)
def Draw_Salvo(MainColour=None,XChange=0):
  if MainColour == None:
     MainColour=(max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 30, 0))
  x = XChange*270
  y=1
  pygame.draw.circle(SCREEN,MainColour,(298+x-y,350),90,15)
  pygame.draw.rect(SCREEN, MainColour, (284+x-y, 180+210, 30, 70),0,0,0)
  pygame.draw.rect(SCREEN, MainColour, (284+x-y, 180+50, 30, 80),0,0,0)
  pygame.draw.rect(SCREEN, MainColour, (179+x, 180+155, 70, 30),0,0,0)
  pygame.draw.rect(SCREEN, MainColour, (340+x, 180+155, 70, 30),0,0,0)
def Draw_FogOfWar(MainColour=None,XChange=0):
  x = (XChange*270) -6
  if MainColour == None:
     MainColour=(max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 30, 0))
  y = 55
  pygame.draw.circle(SCREEN, MainColour, (300+x, 280+y), 50)   # Center top
  pygame.draw.circle(SCREEN, MainColour, (350+x, 290+y), 40)   # Top-right
  pygame.draw.circle(SCREEN, MainColour, (250+x, 290+y), 40)   # Top-left
  pygame.draw.circle(SCREEN, MainColour, (320+x, 250+y), 35)   # Upper-right
  pygame.draw.circle(SCREEN, MainColour, (280+x, 250+y), 35)   # Upper-left

  # Bottom part of the cloud (flatter)
  pygame.draw.circle(SCREEN, MainColour, (270+x, 330+y), 30)   # Bottom-left
  pygame.draw.circle(SCREEN, MainColour, (330+x, 330+y), 30)   # Bottom-right

  # Add a horizontal ellipse to flatten the bottom
  pygame.draw.ellipse(SCREEN, MainColour, (250+x, 320+y, 100, 40))




def Draw_RulesReversed(MainColour=None,XChange=0):
    if MainColour == None:
     MainColour=(max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0))
    xx = XChange*270
    pygame.draw.circle(SCREEN,MainColour,(295+xx,350),90,15)
    x, y = 373, 370
    size = 30
    half_size = size // 1

    # Define points for the lines
    top_point = (x+xx, y - size)  # Top point of the arrowhead
    left_point = (x+xx - half_size, y + half_size)  # Bottom-left point
    right_point = (x+xx + half_size, y + half_size)  # Bottom-right point

    # Draw the two lines forming the arrowhead
    pygame.draw.line(SCREEN, MainColour, top_point, left_point, 15)
    pygame.draw.line(SCREEN, MainColour, top_point, right_point, 15)
    pygame.draw.rect(SCREEN, DARKGREEN, (359+xx, 308, 30, 40),0,0,10)

def Draw_CaptureTheFlag(MainColour=None,XChange=0):
  if MainColour == None:
     MainColour=(max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0))
  x = XChange*270
  pygame.draw.rect(SCREEN, MainColour, (215+x, 270, 20, 200),0,0,0)
  pygame.draw.rect(SCREEN, MainColour, (215+x, 280, 150, 80),0,0,0)
  pygame.draw.circle(SCREEN,MainColour,(225+x,270),20,0)
def Gamesetup():
  global yyarrow
  pygame.draw.rect(SCREEN,GREEN,(38,40,525,70),0,5,5)
  pygametext("Select Game Mode:",57,55,77,DARKGREEN)
  GamemodeList = ["Classic","Salvo","Fog Of War","Rules Reversed","Capture The Flag"]
  pygametext(GamemodeList[yyarrow],172,190,40,GREEN)
  pygame.draw.rect(SCREEN, GREEN, (169, 180+40, 250, 250),10,0,0)
  if yyarrow > 0:
    pygame.draw.rect(SCREEN, (max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)), (-100, 180+40, 250, 250),10,0,0)
  try:
    pygametext(GamemodeList[yyarrow+1],172+250+19,190,40,(max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)))
    pygame.draw.rect(SCREEN, (max(GREEN[0] - 100, 0),max(GREEN[1] - 100, 0), max(GREEN[2] - 100, 0)), (169+250+19, 180+40, 250, 250),10,0,0)
  except IndexError:
    pass
  if yyarrow == 0:
    Draw_Classic(GREEN)
    Draw_Salvo(None,1)
  elif yyarrow == 1:
    Draw_Classic(None,-1)
    Draw_Salvo(GREEN)
    Draw_FogOfWar(None,1)
  elif yyarrow == 2:
    Draw_Salvo(None,-1)
    Draw_FogOfWar(GREEN)
    Draw_RulesReversed(None,1)
  elif yyarrow == 3:
    Draw_FogOfWar(None,-1)
    Draw_RulesReversed(GREEN)
    Draw_CaptureTheFlag(None,+1)
  elif yyarrow == 4:
    Draw_RulesReversed(None,-1)
    Draw_CaptureTheFlag(GREEN)

  pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
  pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
  keys = pygame.key.get_pressed()
  if keys[ord('d')] or keys[pygame.K_RIGHT]:
      if yyarrow < 4:
        yyarrow += 1
        pygame.time.wait(200)
  if keys[ord('a')] or keys[pygame.K_LEFT]:
      if yyarrow > 0:
        yyarrow -= 1
        pygame.time.wait(200)
  if keys[pygame.K_RETURN]:
    Clearscreen(DARKGREEN)
    return yyarrow
  if keys[pygame.K_ESCAPE]:
    GameVairables.menu = 0
    Clearscreen(DARKGREEN)
#Level = 1
yyarrow = 0
def Draw_FinalBoards(SCREEN, xmove, ymove, ShipClass, SemiDarkColour, VeryBrightColour):
    # Missed shots
    for row in ShipClass.BattleshipShots:
        x = 60 + xmove + (row[1] * 15)
        y = 416 + ymove + (row[0] * 15)
        pygame.draw.rect(SCREEN, SemiDarkColour, (x, y, 14, 13), 0, 0, 0)
        pygame.draw.rect(SCREEN, DARKGREEN, (x, y + 3, 14, 7), 0)
        pygame.draw.rect(SCREEN, DARKGREEN, (x + 4, y, 7, 14), 0)

    # Successful hits
    for row in ShipClass.BattleshipHits:
        x = 60 + xmove + (row[1] * 15)
        y = 416 + ymove + (row[0] * 15)
        pygame.draw.rect(SCREEN, SemiDarkColour, (x, y, 14, 13), 0, 0, 0)
        pygame.draw.rect(SCREEN, DARKGREEN, (x, y + 3, 14, 7), 0)
        pygame.draw.rect(SCREEN, DARKGREEN, (x + 4, y, 7, 14), 0)
        pygame.draw.circle(SCREEN, GREEN, (x + 8, y + 6.5), 3)

    # Remaining health
    for row in ShipClass.BattleshipHealth:
        x = 60 + xmove + (row[1] * 15)
        y = 416 + ymove + (row[0] * 15)
        pygame.draw.circle(SCREEN, VeryBrightColour, (x + 8, y + 6.5), 3)

    # Cruiser damage
    if len(ShipClass.CruiserDamage) == 2:
        for row in ShipClass.CruiserDamage:
            x = 60 + xmove + (row[1] * 15)
            y = 416 + ymove + (row[0] * 15)
            pygame.draw.rect(SCREEN, SemiDarkColour, (x, y, 14, 13), 0, 0, 0)
            pygame.draw.rect(SCREEN, GREEN, (x, y + 3, 14, 7), 0)
            pygame.draw.rect(SCREEN, GREEN, (x + 4, y, 7, 14), 0)
            pygame.draw.circle(SCREEN, GREEN, (x + 8, y + 6.5), 3)
            pygame.draw.circle(SCREEN, VeryBrightColour, (x + 8, y + 6.5), 3)

    # Submarine damage
    if len(ShipClass.SubmarineDamage) == 3:
        for row in ShipClass.SubmarineDamage:
            x = 60 + xmove + (row[1] * 15)
            y = 416 + ymove + (row[0] * 15)
            pygame.draw.rect(SCREEN, SemiDarkColour, (x, y, 14, 13), 0, 0, 0)
            pygame.draw.rect(SCREEN, GREEN, (x, y + 3, 14, 7), 0)
            pygame.draw.rect(SCREEN, GREEN, (x + 4, y, 7, 14), 0)
            pygame.draw.circle(SCREEN, GREEN, (x + 8, y + 6.5), 3)
            pygame.draw.circle(SCREEN, VeryBrightColour, (x + 8, y + 6.5), 3)

    # Battleship damage
    if len(ShipClass.BattleshipDamage) == 3:
        for row in ShipClass.BattleshipDamage:
            x = 60 + xmove + (row[1] * 15)
            y = 416 + ymove + (row[0] * 15)
            pygame.draw.rect(SCREEN, SemiDarkColour, (x, y, 14, 13), 0, 0, 0)
            pygame.draw.rect(SCREEN, GREEN, (x, y + 3, 14, 7), 0)
            pygame.draw.rect(SCREEN, GREEN, (x + 4, y, 7, 14), 0)
            pygame.draw.circle(SCREEN, GREEN, (x + 8, y + 6.5), 3)
            pygame.draw.circle(SCREEN, VeryBrightColour, (x + 8, y + 6.5), 3)

    # Destroyer damage
    if len(ShipClass.DestroyerDamage) == 4:
        for row in ShipClass.DestroyerDamage:
            x = 60 + xmove + (row[1] * 15)
            y = 416 + ymove + (row[0] * 15)
            pygame.draw.rect(SCREEN, SemiDarkColour, (x, y, 14, 13), 0, 0, 0)
            pygame.draw.rect(SCREEN, GREEN, (x, y + 3, 14, 7), 0)
            pygame.draw.rect(SCREEN, GREEN, (x + 4, y, 7, 14), 0)
            pygame.draw.circle(SCREEN, GREEN, (x + 8, y + 6.5), 3)
            pygame.draw.circle(SCREEN, VeryBrightColour, (x + 8, y + 6.5), 3)

    # Aircraft carrier damage
    if len(ShipClass.AircraftCarrierDamage) == 5:
        for row in ShipClass.AircraftCarrierDamage:
            x = 60 + xmove + (row[1] * 15)
            y = 416 + ymove + (row[0] * 15)
            pygame.draw.rect(SCREEN, SemiDarkColour, (x, y, 14, 13), 0, 0, 0)
            pygame.draw.rect(SCREEN, GREEN, (x, y + 3, 14, 7), 0)
            pygame.draw.rect(SCREEN, GREEN, (x + 4, y, 7, 14), 0)
            pygame.draw.circle(SCREEN, GREEN, (x + 8, y + 6.5), 3)
            pygame.draw.circle(SCREEN, VeryBrightColour, (x + 8, y + 6.5), 3)
    drawGrid(15,60,392,2) #small left board
class GameResults():
  def __init__(self):
      self.OptionSelect = 1
      self.AccountNeedsUpdate = True
  def GameResultsControls(self):
      if self.OptionSelect == 1:
        pygame.draw.rect(SCREEN,GREEN, (215,214.9, 175, 175.1/3), 5, 0, 0)#middle Box!
        pygametext("Continue",224,224,50,GREEN)
        pygametext("Rematch",224,224+59,50,DARKGREEN)
        pygametext("Quit",224,224+59+59,50,DARKGREEN)
        pygame.draw.rect(SCREEN,DARKGREEN , (215,214.9+59, 175, 175.1/3), 5, 0, 0)#middle Box!
        pygame.draw.rect(SCREEN,DARKGREEN , (215,214.9+59+59, 175, 175.1/3), 5, 0, 0)#middle Box!
      if self.OptionSelect == 2:
        pygame.draw.rect(SCREEN,DARKGREEN, (215,214.9, 175, 175.1/3), 5, 0, 0)#middle Box!
        pygametext("Continue",224,224,50,DARKGREEN)
        pygametext("Rematch",224,224+59,50,GREEN)
        pygametext("Quit",224,224+59+59,50,DARKGREEN)
        pygame.draw.rect(SCREEN,GREEN , (215,214.9+59, 175, 175.1/3), 5, 0, 0)#middle Box!
        pygame.draw.rect(SCREEN,DARKGREEN , (215,214.9+59+59, 175, 175.1/3), 5, 0, 0)#middle Box!
      if self.OptionSelect == 3:
        pygame.draw.rect(SCREEN,DARKGREEN, (215,214.9, 175, 175.1/3), 5, 0, 0)#middle Box!
        pygametext("Continue",224,224,50,DARKGREEN)
        pygametext("Rematch",224,224+59,50,DARKGREEN)
        pygametext("Quit",224,224+59+59,50,GREEN)
        pygame.draw.rect(SCREEN,DARKGREEN , (215,214.9+59, 175, 175.1/3), 5, 0, 0)#middle Box!
        pygame.draw.rect(SCREEN,GREEN , (215,214.9+59+59, 175, 175.1/3), 5, 0, 0)#middle Box!
      pygame.event.get()
      keys = pygame.key.get_pressed()
      if keys[ord('s')] or keys[pygame.K_DOWN]:
        if self.OptionSelect < 3:
          self.OptionSelect += 1
        pygame.time.wait(200)
            #print("(",GameVairables.xx,",",GameVairables.yy,")")
      elif keys[ord('w')] or keys[pygame.K_UP]:
          if self.OptionSelect > 1:
            self.OptionSelect -= 1
          pygame.time.wait(200)
      elif keys[pygame.K_RETURN]:
        Clearscreen(DARKGREEN)
        print(keys[pygame.K_RETURN])
        pygame.time.wait(200)
        #print("YO...BAD")
        self.GameResultMenuOption()
  def GameResultMenuOption(self):
    if self.OptionSelect == 1:
        GameVairables.DefaultGamePreSetUpData()
    if self.OptionSelect == 2:
        GameVairables.ReplayGamePreSetUpData()
    if self.OptionSelect == 3:
        GameVairables.QuitGamePreSetUpData()
  def Draw_ResultsScreen(self,GameResult):
      VeryBrightColour = [0,0,0]
      for rgbValue in range(0,3):
        if GREEN[rgbValue] != 0:
          VeryBrightColour[rgbValue] = 255
      if GameResult == "Win":
        PlayerTextResult = "Victory!"
        ComputerTextResult = "Defeat!"
        ComputerDisplayColour = max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)
        PlayerDisplayColour = DARKGREEN
        pygame.draw.polygon(SCREEN,(max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)),[(30,30),(570,30),(570,570)])
        pygame.draw.line(SCREEN,ComputerDisplayColour,(59.5+(15.25*10),392),(60+(15.25*10),0),5)
        pygame.draw.line(SCREEN,ComputerDisplayColour,(60+(15.185*10),392),(600,392),5)
      else:
        ComputerTextResult= "Victory!"
        PlayerTextResult = "Defeat!"
        PlayerDisplayColour = max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)
        ComputerDisplayColour = DARKGREEN
        pygame.draw.polygon(SCREEN,(max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)),[(30,30),(30,570),(570,570)])
        pygame.draw.line(SCREEN,PlayerDisplayColour,(392,60+(15.185*10)),(0,60+(15.185*10)),5)
        pygame.draw.line(SCREEN,PlayerDisplayColour,(392,60+(15.185*10)),(392,600),5)
      pygame.draw.rect(SCREEN, PlayerDisplayColour, (392,60, 150, 150), 0, 0, 0)
      pygame.draw.rect(SCREEN,(max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)) , (215,214.9, 175, 175.1), 0, 0, 0)#middle Box!
      pygame.draw.rect(SCREEN,PlayerDisplayColour , (405,230, 50, 50), 5, 0, 0)
      pygame.draw.circle(SCREEN, PlayerDisplayColour, (430, 230+25), 15,5)
      pygame.draw.rect(SCREEN,PlayerDisplayColour , (405+30,230+22, 12, 7), 0, 0, 0)
      pygame.draw.rect(SCREEN,PlayerDisplayColour , (405+7,230+22, 12, 7), 0, 0, 0)
      pygame.draw.rect(SCREEN,PlayerDisplayColour , (405+21.5,230+7, 7, 12), 0, 0, 0)
      pygame.draw.rect(SCREEN,PlayerDisplayColour , (405+21.5,230+32, 7, 12), 0, 0, 0)
      pygame.draw.circle(SCREEN, PlayerDisplayColour, (420, 230+25+45), 10,4)
      pygame.draw.circle(SCREEN, PlayerDisplayColour, (420, 230+25+45), 4)
      pygame.draw.circle(SCREEN, PlayerDisplayColour, (440, 230+25+55), 10,4)
      pygame.draw.circle(SCREEN, PlayerDisplayColour, (440, 230+25+55), 4)
      pygame.draw.circle(SCREEN, PlayerDisplayColour, (420, 230+25+65), 10,4)
      pygame.draw.circle(SCREEN, PlayerDisplayColour, (420, 230+25+65), 4)
      pygame.draw.circle(SCREEN, PlayerDisplayColour, (430, 230+25+55+55), 5)
      pygame.draw.circle(SCREEN, PlayerDisplayColour, (430, 230+25+55+55), 15,5)
      pygame.draw.rect(SCREEN,PlayerDisplayColour , (405,230+55, 50, 50), 5, 0, 0)
      pygame.draw.rect(SCREEN,PlayerDisplayColour , (405,230+55+55, 50, 50), 5, 0, 0)
      pygametext(PlayerTextResult,200,45,50,PlayerDisplayColour)
      pygametext(Human.username,200,45+50,30,PlayerDisplayColour)
      try:
        #print(Human.GameHits)
        #print(Human.GameMiss)
        #print(Human.GameHits/Human.GameMiss)
        if GameVairables.gamemode == 3:
          accuracy = round((Human.GameMiss/(Human.GameHits+Human.GameMiss))*100)
        else:
           accuracy = round((Human.GameHits/(Human.GameHits+Human.GameMiss))*100)
        pygametext(str(accuracy),465,352,40,PlayerDisplayColour)
        pygametext(str(Human.MaxShotStreak),465,352-55,40,PlayerDisplayColour)
        pygametext(str(Human.FirstStrike),465,352-55-55,40,PlayerDisplayColour)
      except ZeroDivisionError:
        pygametext("0",465,352,40,PlayerDisplayColour)
        pygametext("0",465,352-55,40,PlayerDisplayColour)
        pygametext("0",465,352-55-55,40,PlayerDisplayColour)
      #--------------------------------------------------
      pygametext(ComputerTextResult,45,200,50,ComputerDisplayColour)
      pygametext(Enemy.username,45,200+50,30,ComputerDisplayColour)
      pygame.draw.rect(SCREEN,ComputerDisplayColour , (230,405, 50, 50), 5, 0, 0)
      pygame.draw.rect(SCREEN,ComputerDisplayColour , (230+55,405, 50, 50), 5, 0, 0)
      pygame.draw.rect(SCREEN,ComputerDisplayColour , (230+55+55,405, 50, 50), 5, 0, 0)
      pygame.draw.circle(SCREEN, ComputerDisplayColour, (230+25,430), 15,5)
      pygame.draw.rect(SCREEN,ComputerDisplayColour , (230+7,405+21.5, 12, 7), 0, 0, 0)
      pygame.draw.rect(SCREEN,ComputerDisplayColour , (230+30,405+21.5, 12, 7), 0, 0, 0)
      pygame.draw.rect(SCREEN,ComputerDisplayColour , (230+22,405+7, 7, 12), 0, 0, 0)
      pygame.draw.rect(SCREEN,ComputerDisplayColour , (230+22,405+30, 7, 12), 0, 0, 0)

      pygame.draw.circle(SCREEN, ComputerDisplayColour, (230+25+45,420), 10,4)
      pygame.draw.circle(SCREEN, ComputerDisplayColour, (230+25+45,420), 4)
      pygame.draw.circle(SCREEN, ComputerDisplayColour, (230+25+55,440), 10,4)
      pygame.draw.circle(SCREEN, ComputerDisplayColour, (230+25+55,440), 4)
      pygame.draw.circle(SCREEN, ComputerDisplayColour, (230+25+65,420), 10,4)
      pygame.draw.circle(SCREEN, ComputerDisplayColour, (230+25+65,420), 4)
      pygame.draw.circle(SCREEN, ComputerDisplayColour, (230+25+55+55,430), 5)
      pygame.draw.circle(SCREEN, ComputerDisplayColour, (230+25+55+55,430), 15,5)
      try:
        if GameVairables.gamemode == 3:
          CompAccuracy = round((Enemy.GameMiss/(Enemy.GameHits+Enemy.GameMiss))*100)
        else:
          CompAccuracy = round((Enemy.GameHits/(Enemy.GameHits+Enemy.GameMiss))*100)
        pygametext(str(CompAccuracy),352,465,40,ComputerDisplayColour)
        pygametext(str(Enemy.MaxShotStreak),352-55,465,40,ComputerDisplayColour)
        pygametext(str(Enemy.FirstStrike),352-55-55,465,40,ComputerDisplayColour)
      except ZeroDivisionError:
        pass
      #------------------------------------------------------------------------------------------------------
      pygame.draw.rect(SCREEN, DARKGREEN, (60,392, 150, 150), 0, 0, 0)
      pygame.draw.rect(SCREEN, DARKGREEN, (392,60, 150, 150), 0, 0, 0)
      drawGrid(15,60,392,2) #small left board
      drawGrid(15,392,60,2) #small right board
      Draw_FinalBoards(SCREEN,0,-23,Enemy,(max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)),VeryBrightColour)
      Draw_FinalBoards(SCREEN,332,-355,Human,(max(GREEN[0] - 30, 0),max(GREEN[1] - 30, 0), max(GREEN[2] - 30, 0)),VeryBrightColour)
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
      pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
      if self.AccountNeedsUpdate:
         if Human.SignedIn == True:
            user_data_response = PlayerAccount.get_user_data(Human.username,Human.password) #getattr(self,
            if GameVairables.gamemode == 0:
               gamemode = "Classic"
            elif GameVairables.gamemode == 1:
               gamemode = "Salvo"
            elif GameVairables.gamemode == 2:
               gamemode = "FOW"
            elif GameVairables.gamemode == 3:
               gamemode = "RR"
            elif GameVairables.gamemode == 4:
               gamemode = "CTF"
            longest_hit_streak = user_data_response.get('longest_hit_streak')
            if longest_hit_streak < Human.MaxShotStreak:
              HitStreak = Human.MaxShotStreak
            else:
              HitStreak = longest_hit_streak
            print(HitStreak)
            Wins = user_data_response.get(f"{gamemode}_Wins")
            Loss = user_data_response.get(f"{gamemode}_Loss")
            print(Wins)
            print(Loss)
            if GameResult == "Win":
              Wins += 1
              Loss = Loss
            else:
              Wins = Wins
              Loss += 1
            Accuracy = user_data_response.get(f"{gamemode}_accuracy")
            print(Accuracy)
            if Accuracy == 0:
               Accuracy= accuracy
            else:
              Accuracy = (Accuracy + accuracy)/2
            last_five_results = user_data_response.get(f"{gamemode}_last_five_results")
            print(last_five_results)
            last_five_results_list = last_five_results.split(',')
            last_five_results_list.pop()
            if GameResult == "Win":
              last_five_results_list.insert(0,1)
            else:
              last_five_results_list.insert(0,0)
            last_five_results_text = ','.join([str(result) for result in last_five_results_list])
            if GameVairables.gamemode == 0:
               PlayerAccount.update_user(Human.username,Human.password,None,None,HitStreak,Wins,Loss,Accuracy,last_five_results_text)
            elif GameVairables.gamemode == 1:
               PlayerAccount.update_user(Human.username,Human.password,None,None,HitStreak,None,None,None,None,Wins,Loss,Accuracy,last_five_results_text)
            elif GameVairables.gamemode == 2:
               PlayerAccount.update_user(Human.username,Human.password,None,None,HitStreak,None,None,None,None,None,None,None,None,Wins,Loss,Accuracy,last_five_results_text)
            elif GameVairables.gamemode == 3:
               PlayerAccount.update_user(Human.username,Human.password,None,None,HitStreak,None,None,None,None,None,None,None,None,None,None,None,None,Wins,Loss,Accuracy,last_five_results_text)
            elif GameVairables.gamemode == 4:
               PlayerAccount.update_user(Human.username,Human.password,None,None,HitStreak,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,None,Wins,Loss,Accuracy,last_five_results_text)
            self.AccountNeedsUpdate = False
      self.GameResultsControls()
#------------------
#Human.auto_board_set_up()
#Human.PrintFullBoard()
#!!!!!!!!
#MainMusic = None
#----------------
class MusicManager:
    def __init__(self):
        # Dictionary to store loaded music tracks
        self.music_tracks = {}

    def load_music(self, track_name, music_folder):
        #Loads the first audio file from the specified folder and stores it under the given track name
        pygame.mixer.init()
       
        # Get a list of files in the directory
        try:
          files = os.listdir(music_folder)
          # Filter the list to include only files with supported audio extensions
          audio_files = [file for file in files if file.endswith(('.mp3', '.ogg', '.wav'))]
        except FileNotFoundError:
          files = None
        #except TypeError:
          audio_files = None
       
        # Check if there are any audio files in the directory
        if audio_files:
            # Get the first audio file in the directory
            first_file = audio_files[0]
            music_file = os.path.join(music_folder, first_file)
           
            # Load the music file as a Sound object and store it with the track name
            self.music_tracks[track_name] = pygame.mixer.Sound(music_file)
            print(f"Loaded {track_name} from {music_file}.")
            return self.music_tracks[track_name]
        else:
            print(f"No audio files found in the directory: {music_folder}")
            return None

    def play_music(self, track_name):
        #Plays the specified Audio track in a loop.
        if track_name in self.music_tracks:
            track = self.music_tracks[track_name]
            if track.get_num_channels() < 1:
              self.music_tracks[track_name].play(-1,0,10000)  # Play the music indefinitely
              print(f"Playing {track_name}.")
        else:
            #print(f"Track {track_name} not found.")
          pass
           
    def play_soundEffect(self, track_name):
        #Plays the specified auido track once.
        if track_name in self.music_tracks:
            track = self.music_tracks[track_name]
            if track.get_num_channels() < 1:
              self.music_tracks[track_name].play()  # Play the music indefinitely
              print(f"Playing {track_name}.")
        else:
            #print(f"Track {track_name} not found.")
          pass

    def get_music(self, track_name):
        #Returns the specified music track object if it exists.
        return self.music_tracks.get(track_name, None)

    def stop_music(self, track_name):
        #Stops the specified music track if it is playing.
        if track_name in self.music_tracks:
            self.music_tracks[track_name].fadeout(5000)
            #print(f"Stopped {track_name}.")
        else:
            #print(f"Track {track_name} not found.")
          pass

    def set_volume(self, track_name, volume):
        # Set the volume of the specified music track
        if track_name in self.music_tracks:
            self.music_tracks[track_name].set_volume(volume)
            print(f"Volume set to {volume} for {track_name}.")
        else:
            #print(f"Track {track_name} not found.")
            pass

    def get_volume(self, track_name):
        # Gets the volume of the specified music track
        if track_name in self.music_tracks:
            track = self.music_tracks.get(track_name)
            if track:
                return track.get_volume()
        return None
    def is_track_not_playing(self, track_name):
        # Returns True if the specified track is not playing, False otherwise
        if track_name in self.music_tracks:
            track = self.music_tracks[track_name]
            return track.get_num_channels() == 0
        else:
            #print(f"Track {track_name} not found.")
            return True  # Assume not playing if the track is not found

# Example usage
music_manager = MusicManager()
music_manager.load_music("M_Menu", r"C:\Users\User\Documents\Battleship\Music\Menu Music")
music_manager.load_music("M_Gameplay", r"C:\Users\User\Documents\Battleship\Music\Gameplay Music")
# Load and manage multiple music tracks
music_manager.load_music("SE_Radar", r"C:\Users\User\Documents\Battleship\Music\Radar Sound Effect")
music_manager.load_music("SE_Hit", r"C:\Users\User\Documents\Battleship\Music\Hit Sound Effect")
music_manager.load_music("SE_Miss", r"C:\Users\User\Documents\Battleship\Music\Miss Sound Effect")

class GamePreSetUp():
  def __init__(self):
    self.xx = 1
    self.yy = 1
    self.loggedplayer = [] #max 4
    self.loggedOpponent = [] #max 4
    self.menu = 0 #2 account
    self.gamemode = None
    self.vsscreen = 0
    self.running = True
    self.setup = False
    Results.AccountNeedsUpdate = True
  def DefaultGamePreSetUpData(self):
    self.xx = 1
    self.yy = 1
    self.loggedplayer = [] #max 4
    self.loggedOpponent = [] #max 4
    self.menu = 0
    self.gamemode = None
    self.vsscreen = 0
    self.running = True
    self.setup = False
    self.Match = None
    Human.reset()
    Enemy.reset()
    Enemy.auto_board_set_up()
    VS.Reset()
    Results.AccountNeedsUpdate = True
  def ReplayGamePreSetUpData(self):
    self.xx = 1
    self.yy = 1
    self.loggedplayer = [] #max 4
    self.loggedOpponent = [] #max 4
    #self.menu = 0
    #self.gamemode = None
    self.vsscreen = 0
    self.running = True
    self.setup = False
    self.Match = None
    Human.reset()
    Enemy.reset(Enemy.username)
    Enemy.auto_board_set_up()
    VS.Reset()
    Results.AccountNeedsUpdate = True
  def QuitGamePreSetUpData(self):
    self.xx = 1
    self.yy = 1
    self.loggedplayer = [] #max 4
    self.loggedOpponent = [] #max 4
    self.menu = 5
    self.gamemode = None
    self.vsscreen = 0
    self.running = True
    self.setup = False
    self.Match = None
    Results.AccountNeedsUpdate = True
    #Human.reset()
    #Enemy.reset()
    #Enemy.auto_board_set_up()
# Play the GameVairables.menu music
#------------
#GameVairables.menu = 1
#GameVairables.gamemode = 4
#GameVairables.vsscreen = 0
#--------------------------------

Results = GameResults()
GameVairables = GamePreSetUp()
Info = IntelMenu()
Account = AccountMenu(Human)
VS = VSScreen()

#--------------------------------
def main():
  global SCREEN
  CLOCK = pygame.time.Clock()
  SCREEN.fill(DARKGREEN)
  pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,40,40)
  pygame.draw.rect(SCREEN, GRAY, (0, 0, WINDOW_WIDTH*2, WINDOW_HEIGHT*2),30,0,0)
  music_manager.play_music("SE_Radar")
 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True  # This ensures that Flask thread will close when the main program exits
    flask_thread.start()

while GameVairables.running:
    counter += 1
    seconds = int(counter / (40*1))
    #print(seconds)
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.WINDOWMINIMIZED:
            GameVairables.running = False
    #pygame.mouse.set_visible(False)
    main()
    if GameVairables.setup == True:
        music_manager.stop_music("M_Menu")
        if music_manager.is_track_not_playing("M_Menu"):
          music_manager.play_music("M_Gameplay")
    if GameVairables.menu == 0:
      #Results.Draw_ResultsScreen("Win")
      Mainmenu()
      music_manager.stop_music("M_Gameplay")
      if music_manager.is_track_not_playing("M_Gameplay"):
        music_manager.play_music("M_Menu")
      GameVairables.vsscreen = 200
      GameVairables.setup = False
    elif GameVairables.menu == 1 and GameVairables.vsscreen > 0 and GameVairables.gamemode != None:
      VS.Render()
      GameVairables.vsscreen -= 1
      if GameVairables.vsscreen == 0:
        Clearscreen(DARKGREEN)
    elif GameVairables.menu == 1 and GameVairables.gamemode == 0 and GameVairables.vsscreen == 0:
      if GameVairables.setup:
        if GameVairables.Match == "InProgress":
            # Run the game loop and check the result
            result = ClassicGameplay()
            #OptionSelect = 1
            # Check if the game ended
        if result == "Win" or result == "Lose":
                GameVairables.Match = "Ended"
                Results.Draw_ResultsScreen(result)
                matrix = [[0 for col in range(10)] for row in range(10)]
        else:
            GameVairables.Match = "InProgress"
      else:
        # Perform fleet GameVairables.setup
        GameVairables.setup = FleetSetup()
        if GameVairables.setup:
            Clearscreen(DARKGREEN)
            GameVairables.Match = "InProgress"  # Set the GameVairables.match to in progress after GameVairables.setup
    elif GameVairables.menu == 1 and GameVairables.gamemode == 1 and GameVairables.vsscreen == 0:
      if GameVairables.setup:
        if GameVairables.Match == "InProgress":
            # Run the game loop and check the result
            result = SalvoGameplay()
           
            # Check if the game ended
        if result == "Win" or result == "Lose":
                GameVairables.Match = "Ended"
                Results.Draw_ResultsScreen(result)
                matrix = [[0 for col in range(10)] for row in range(10)]
        else:
            GameVairables.Match = "InProgress"
      else:
        # Perform fleet GameVairables.setup
        GameVairables.setup = FleetSetup()
        if GameVairables.setup:
            Clearscreen(DARKGREEN)
            GameVairables.Match = "InProgress"  # Set the GameVairables.match to in progress after GameVairables.setup
    elif GameVairables.menu == 1 and GameVairables.gamemode == 2 and GameVairables.vsscreen == 0:
      if GameVairables.setup:
        if GameVairables.Match == "InProgress":
            # Run the game loop and check the result
            result = FogOfWarGameplay()
            # Check if the game ended
        if result == "Win" or result == "Lose":
                GameVairables.Match = "Ended"
                Results.Draw_ResultsScreen(result)
                matrix = [[0 for col in range(10)] for row in range(10)]
        else:
            GameVairables.Match = "InProgress"
      else:
        # Perform fleet GameVairables.setup
        GameVairables.setup = FleetSetup()
        if GameVairables.setup:
            Clearscreen(DARKGREEN)
            GameVairables.Match = "InProgress"  # Set the GameVairables.match to in progress after GameVairables.setup
    elif GameVairables.menu == 1 and GameVairables.gamemode == 4 and GameVairables.vsscreen == 0:
      if GameVairables.setup:
        if GameVairables.Match == "InProgress":
            # Run the game loop and check the result
            result = CaptureTheFlagGameplay(FlagShip,FlagShipSize)
            # Check if the game ended
        if result == "Win" or result == "Lose":
                GameVairables.Match = "Ended"
                Results.Draw_ResultsScreen(result)
                matrix = [[0 for col in range(10)] for row in range(10)]
        else:
            GameVairables.Match = "InProgress"
      else:
        # Perform fleet GameVairables.setup
        GameVairables.setup = FleetSetup()
        FlagShipOption = ["Cruiser","Submarine","Battleship","Destroyer","AircraftCarrier"]
        try:
          print(FlagShip)
        except NameError:
           FlagShip = random.choice(FlagShipOption)
           FlagShipSize = Human.ships[FlagShipOption.index(FlagShip)]
        if GameVairables.setup:
            Clearscreen(DARKGREEN)
            GameVairables.Match = "InProgress"  # Set the GameVairables.match to in progress after GameVairables.setup
    elif GameVairables.menu == 1 and GameVairables.gamemode == 3 and GameVairables.vsscreen == 0: #Rules Reverced
      if GameVairables.setup:
        if GameVairables.Match == "InProgress":
            # Run the game loop and check the result
            result = ClassicGameplay(False) #Rules Reverced
           
            # Check if the game ended
        if result == "Win" or result == "Lose":
                GameVairables.Match = "Ended"
                Results.Draw_ResultsScreen(result)
                matrix = [[0 for col in range(10)] for row in range(10)]
        else:
            GameVairables.Match = "InProgress"
      else:
        # Perform fleet GameVairables.setup
        GameVairables.setup = FleetSetup()
        if GameVairables.setup:
            Clearscreen(DARKGREEN)
            GameVairables.Match = "InProgress"  # Set the GameVairables.match to in progress after GameVairables.setup
    elif GameVairables.menu == 1:
      GameVairables.gamemode = Gamesetup()
      #pass
    elif GameVairables.menu == 2:
      Account.render()
    elif GameVairables.menu == 3:
      Info.Render()
    elif GameVairables.menu == 4:
      Level = options_menu.render()
    elif GameVairables.menu == 5:
      Clearscreen(DARKGRAY)
      GameVairables.running = False
    # flip() the display to put your work on SCREEN
    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60


pygame.quit()