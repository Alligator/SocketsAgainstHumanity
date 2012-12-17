import random

class Deck():
  def __init__(self,black_file = "black.txt",white_file = "white.txt"):
    self.black_file = black_file
    self.white_file = white_file
    self.DeckRefresh()

  def RemoveWhiteCard(self,text):
    self.whitecards.remove(text)
  def RemoveBlackCard(self,text):
    self.blackcards.remove(text)
  def GetRandomWhiteCard(self):
    if len(self.whitecards) < 11:
      self.DeckRefresh()
    c = random.choice(self.whitecards)
    self.whitecards.remove(c)
    return c
  def GetRandomBlackCard(self):
    if len(self.blackcards) < 2:
      self.DeckRefresh()
    c = random.choice(self.blackcards)
    self.blackcards.remove(c)
    return c
  def DeckRefresh(self):
    self.whitecards = []
    self.blackcards = []
    
    with open(self.black_file,'r') as f:
      for line in f.readlines():
        self.blackcards.append(line.strip())
      f.close()

    with open(self.white_file,'r') as f:
      for line in f.readlines():
        self.whitecards.append(line.strip())
      f.close()