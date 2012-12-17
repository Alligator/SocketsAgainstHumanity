# TODO: RECYCLE REMOVED HANDLES
# REWRITE 2 / CLEANUP
from sah_const import *

# Filter for ignoring dead player handles.
def PlayerFilter(s):
  if s is None:
    return False
  else:
    return True

class Game():
  def __init__(self,name,maxplayers,creator,password = None):
    self.name = name
    self.players = []
    self.maxplayers = maxplayers
    self.creator = None
    self.rounds = []
    self.password = password
    self.game_deck = Deck()
    self.kill = False
    self.AcceptAndCreatePlayer(creator)
    self.creator = self.players[0]

  def JoinAttempt(self,socket,pw):
    # Check if already somehow in the game
    for p in filter(PlayerFilter,self.players):
      if p.socket == socket:
        return False
    if self.password == pw and self.GetPlayerCount() < self.maxplayers:
        return self.AcceptAndCreatePlayer(socket)
    return False

  #After validating that the player can join (password and playercount conditions), create a player object to bind to this connection.
  def AcceptAndCreatePlayer(self, socket):
    player_obj = Player(socket,self)
    self.AddPlayer(player_obj)
    return True

  #This function will return an unused handle. This is used when creating a new player.
  def FetchNewHandle(self):
    self.players.append(None)
    return len(self.players) - 1

  # Add player object to game, set up hand and send needed data.
  def AddPlayer(self,player):
    # Check if a single game instance is using too many handles and sucking up >10MB memory
    if len(self.players) > 250000:
      self.GameEnd('TOO MANY HANDLES, GET OUT.')

    self.players[player.handle] = player
    for i in range(0,10):
      player.hand.append(self.game_deck.GetRandomWhiteCard())
    player.SendHand()
    
    if not self.GetCurrentRound():
      self.StartNewRound(False)
    else:
      self.SendRoundData(self.GetCurrentRound())
    self.PlayerDataUpdate()

  def RemovePlayer(self,player):

    if self.creator is player:
      self.GameEnd('Host has left.')
    elif self.GetCurrentRound().card_czar is player:
      self.StartNewRound(False)
      self.SendChatMessage('SYSTEM','Card czar has left the game. Starting new round.')

    self.players[player.handle] = None
    self.GetCurrentRound().RemovePlayerCards(player)
    player.Emit(EVT_USER_EJECT)
    self.PlayerDataUpdate()


  def GetPlayerCount(self):
    return len(filter(PlayerFilter,self.players))
    
  def SendChatMessage(self,nick,msg):
    self.SendEventToAllPlayers(EVT_CHAT_MSG,nick=nick,msg=msg)

  def GameEnd(self,reason):
    self.SendEventToAllPlayers(EVT_USER_EJECT)
    self.kill = True

  def GetCurrentRound(self):
    if len(self.rounds) > 0:
      return self.rounds[len(self.rounds) - 1]
    else:
      return None

  def StartNewRound(self,prev_valid = True):
    new_round = Round()
    if len(self.players) > 1:
      new_round.SetCzar(random.choice(self.players))
    else:
      new_round.SetCzar(self.creator)

    b_card = self.game_deck.GetRandomBlackCard()

    new_round.SetBlackCard(b_card)
    new_round.SetDrawAmount(b_card.count('_'))

    if prev_valid:
      for player in filter(PlayerFilter,self.players):
        player.cards.append(self.game_deck.GetRandomWhiteCard())
      for player in filter(PlayerFilter,self.players):
        player.SendHand()

    self.rounds.append(new_round)
    self.SendRoundData(self.GetCurrentRound())
    self.PlayerDataUpdate()

  def SendRoundData(self,rnd):
    # Round data, send the handle of the czar 
    for player in self.players:
      player.Emit(EVT_GAME_ROUND_DATA,czar=rnd.card_czar.handle,black_card=rnd.black_card,draw_amount=rnd.draw_amt)

  def GetLobbyObject(self):
    c = lambda x:  x is not None
    return {"name":self.name,"players":self.GetPlayerCount(),"maxplayers":self.maxplayers,"password":c(self.password),"creator":self.creator.name}
    
  def PlayerDataUpdate(self):
    pl_list = []
    for player in filter(PlayerFilter,self.players):
      pl_list.append({"handle":player.handle,"name":player.name,"points":player.points})
    self.SendEventToAllPlayers(EVT_GAME_PLAYER_LIST,player_list=pl_list)

  def SendEventToAllPlayers(self,*args,**kwargs):
    for p in filter(PlayerFilter,self.players):
      p.Emit(*args,**kwargs)


  def SubmitCard(self,player,card):
    c = self.GetCurrentRound().PlayCard(player,card)
    # Fire a 'player has locked in event here'
    if c:
      self.SendEventToAllPlayers(EVT_CARD_PLAYED_NOTIFICATION)

    # Check if all have played then change state
    if len(self.GetCurrentRound().played_cards) == self.GetPlayerCount() - 1:
      self.GetCurrentRound().ChangeState(1,60)
      self.SendEventToAllPlayers(EVT_GAME_STATE,state=1)
      self.ShowRoundCards()
    return c

  def ShowRoundCards(self):
    cards = self.GetCurrentRound().played_cards



  def CzarSelectedCard(self,player,card):
    # Get player, award points, notify people player y got a point. Move to next state.
    # Client side will show who owns which card anyway.
    if player is self.GetCurrentRound().card_czar and self.GetCurrentRound().IsCzarSelecting():
      winning_player = self.GetCurrentRound().GetPlayerByCard(card)
      winning_player.points += 1
      self.GetCurrentRound().ChangeState(2,3)
      for p in self.players:
        p.emit(EVT_GAME_STATE,state=2,winner=winning_player.name)
      self.PlayerDataUpdate()


  def Pulse(self):
    # I cannot fathom why this logic isn't going off on the remove player crud.
    if self.creator not in self.players:
      self.kill = True
    if self.GetCurrentRound().card_czar not in self.players:
      self.StartNewRound()

    # # Gets pulsed once per second. Abuse this for counters, etc. 
    # if self.GetCurrentRound().IsInGame():
    #   if self.GetCurrentRound().counter > 0:
    #     self.GetCurrentRound().counter -= 1
    #   if self.GetCurrentRound().counter == 10:
    #     for p in self.players:
    #       p.emit('idle_counter',{})
    # if self.GetCurrentRound().counter == 0:

    #   # Kick out who didn't play
    #   # not_idle = [] 
    #   # for p in self.GetCurrentRound().played_cards:
    #   #   not_idle.append(p[0])
    #   # for player in self.players:
    #   #   if player not in not_idle:
    #   #     self.RemovePlayer(player)
    #   self.GetCurrentRound().ChangeState(1,60)

    # if self.GetCurrentRound().IsCzarSelecting():
    #   if self.GetCurrentRound().counter > 0:
    #     self.GetCurrentRound().counter -= 1
    #   if self.GetCurrentRound().counter == 0:
    #     # Handle idle czar
    #     self.RemovePlayer(self.GetCurrentRound().card_czar)
    #     return

    if self.GetCurrentRound().IsShowingEnd():
      # Show end for 10 seconds then start new round.
      if self.GetCurrentRound().counter > 0:
        self.GetCurrentRound().counter -= 1
      if self.GetCurrentRound().counter == 0:
        self.StartNewRound()


# This isn't the nicest way to solve it but, this should fix recursive imports.
from deck import Deck
from round import Round
from player import Player