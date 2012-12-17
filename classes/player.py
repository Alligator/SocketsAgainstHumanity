# Need to refactor to fit game.py method naming standard.
from sah_const import *
from game import Game

def InGame(func):
  def inner(self,*args):
    if self.game:
      func(self,*args)
  return inner

class Player():
  def __init__(self, socket, game):
    self.socket = socket
    socket.player = self
    self.name = socket.name # repeating data...
    
    self.game = game 
    self.handle = game.PlayerGetNewHandle()
    self.hand = []
    self.points = 0

  @InGame
  def SubmitCard(self,cards):
    self.game.GameCardSubmit(self,cards)
    

  @InGame
  def SelectWinner(self,winner_handle):
    self.game.GameCzarSelect(self.handle,winner_handle)
    pass

  def IsSpectator(self):
    pass

  def Spectate(self):
    pass
  
  @InGame
  def LeaveGame(self):
    self.game.PlayerRemove(self)

  @InGame
  def SendHand(self): #Send the player's hand. Do this at the start of a round/join.
    self.Emit(EVT_CARD_GET,cards=self.hand)
    
  def SendChatMessage(self,msg):
    self.game.DataChatMessage(self.handle,msg)
      
  @InGame
  def SendGamestate(self): # TO DEPRECATE
    if self.game:
      return self.game.RoundCurrent().GetState()

  def Emit(self,*args,**kwargs):
    self.socket.emit(args,kwargs)