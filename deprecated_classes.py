import json,random
from sah_const import *

# Setup a deck so we don't get repeating cards
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


class Round():
  def __init__(self):
    self.card_czar = None
    self.black_card = None
    self.played_cards = []
    self.winning_card = None # list of winning card/cards
    self.winning_player = None 
    self.draw_amt = 0
    self.started = False # Still needed?
    self.counter = 10
    self.state = 0

  def PlayCard(self,user,card): # ALWAYS PROVIDE A LIST EVEN IF IT'S ONLY ONE CARD, DONT FUCKING FORGET
    # stop naughty people
    for p in self.played_cards:
      if p[0] == user:
        print 'already played'
        return False
    if user is self.card_czar:
      print 'you a czar'
      return False
    for c in card:
      if c not in user.cards:
        print 'you dont have this dang card'
        return False

    # ok whatever, append.
    self.played_cards.append([user,card])
    return True

  def SetCzar(self,czar):
    self.card_czar = czar
  
  def SetBlackCard(self,card):
    self.black_card = card

  def SetDrawAmount(self,amt):
    self.draw_amt = amt

  def StartRound():
    self.started = True
    # ???
  def ForceUpdate():
    pass
  
  def GetPlayerByCard(self,card):
    for p in self.played_cards:
      for c in p[1]:
        if card == c:
          return p[0]
    return None

  def IsInGame(self):
    return self.state == 0

  def IsCzarSelecting(self):
    return self.state == 1

  def IsShowingEnd(self):
    return self.state == 2

  def ChangeState(self,state,counter = 10):
    self.state = state
    self.counter = counter

  def RemovePlayerCards(self,player):
    # wtf why did i write this ever
    for p in self.played_cards:
      if player is p[0]:
        for c in p[1]:
          player.cards.remove(c)

class Game():
  def __init__(self,name,maxplayers,creator,password = False):
    self.name = name
    self.maxplayers = int(maxplayers)
    self.players = []
    self.password = password
    self.rounds = []
    self.creator = creator
    self.game_deck = Deck()
    self.kill = False
  def ValidatePassword(self,pw):
    return self.password == pw

  def AddPlayer(self,player):
    if player in self.players:
      return False
    else:
      self.players.append(player)
      for i in range(0,10):
        player.cards.append(self.game_deck.GetRandomWhiteCard())
      self.SendHandToPlayer(player)
    
    if not self.GetCurrentRound():
      self.StartNewRound(False)
    
    else:
      self.SendRoundData(self.GetCurrentRound())
    
    self.ForceUpdate()

  def IsFull(self):
    return self.maxplayers == len(self.players)

  def RemovePlayer(self,player):
    # Check how important the player is first
    if self.creator is player:
      self.GameEnd('Host has left.')
    
    elif self.GetCurrentRound().card_czar is player:
      self.StartNewRound(False)
      self.SendChatMessage('SYSTEM','Card czar has left the game. Starting new round.')
    
    self.players.remove(player)
    self.GetCurrentRound().RemovePlayerCards(player)
    player.points = 0
    player.cards = []
    player.game = None
    player.emit(EVT_USER_EJECT)
    self.ForceUpdate()
  
  def SendChatMessage(self,nick,msg):
    for player in self.players:
      player.emit(EVT_CHAT_MSG,nick=nick,msg=msg)

  def GameEnd(self,reason):
    for player in self.players:
      player.emit(EVT_USER_EJECT)
    self.kill = True
    # notify all clients the game is dead and send them back to main screen

  def GetPlayerCount(self):
    return len(self.players)

  def GetCurrentRound(self):
    if len(self.rounds) > 0:
      return self.rounds[len(self.rounds) - 1]
    else:
      return None

  def HasPassword(self):
    return self.password != None
  
  def StartNewRound(self,prev_valid = True):
    new_round = Round()
    if len(self.players) > 1:
      new_round.SetCzar(random.choice(self.players))
    else:
      new_round.SetCzar(self.players[0])

    b_card = self.game_deck.GetRandomBlackCard()

    new_round.SetBlackCard(b_card)
    new_round.SetDrawAmount(b_card.count('_'))

    if prev_valid:
      for player in self.players:
        player.cards.append(self.game_deck.GetRandomWhiteCard())
      self.SendHandToPlayer()
    self.rounds.append(new_round)
    self.SendRoundData(self.GetCurrentRound())
    self.ForceUpdate()

  def SendRoundData(self,rnd):
  # Round data, include who's the czar and the black card 
    is_czar = lambda x: x is rnd.card_czar
    for player in self.players:
      player.emit(EVT_GAME_ROUND_DATA,czar=is_czar(player),black_card=rnd.black_card,draw_amount=rnd.draw_amt,state=rnd.state)
      #player.emit(EVT_GAME_ROUND_DATA,czar=is_czar(player),black_card=rnd.black_card,draw_amount=2,state=rnd.state)

  
  def GetLobbyObject(self):
    c = lambda x:  x is not None
    return {"name":self.name,"players":len(self.players),"maxplayers":self.maxplayers,"password":c(self.password),"creator":self.creator.name}
    
  def ForceUpdate(self):
    pl_list = []
    is_czar = lambda x: x is self.GetCurrentRound().card_czar
    for player in self.players:
      pl_list.append({"name":player.name,"points":player.points,"czar":is_czar(player)})

    for player in self.players:
      player.emit(EVT_GAME_PLAYER_LIST,player_list=pl_list)
      #player.emit(EVT_CARD_GET,json.dumps({"cards":player.cards}))

  def SendHandToPlayer(self,player = None):
    if not player:
      for p in self.players:
        p.emit(EVT_CARD_GET,cards=p.cards)
    else:
      player.emit(EVT_CARD_GET,cards=player.cards)

  def PlayCard(self,player,card):
    c = self.GetCurrentRound().PlayCard(player,card)
    # Fire a 'player has locked in event here'
    print c
    if c:
      for p in self.players:
        print player.name
        p.emit(EVT_CARD_PLAYED_NOTIFICATION) # why can't we have name here? weird collision that .emit doesnt like
    # Check if all have played then change state
    if len(self.GetCurrentRound().played_cards) == len(self.players) - 1:
      self.GetCurrentRound().ChangeState(1,60)
      for p in self.players:
        p.emit(EVT_GAME_STATE,state=1)
        self.ShowRoundCards()
    return c
    # There was meant to be more to this but i forgot what

  def ShowRoundCards(self):
    cards = self.GetCurrentRound().played_cards
    # temp = [] # so much ugly would be fixed if we just wrote our own json encoder.
    # for c in cards:
    #   temp.append((c[0].name,c[1]))

    for p in self.players:
      p.emit(EVT_GAME_PLAYED_CARDS,card_data=zip(*cards)[1])

    pass


  def CzarSelectedCard(self,player,card):
    # Get player, award points, notify people player y got a point. Move to next state.
    # Client side will show who owns which card anyway.
    if player is self.GetCurrentRound().card_czar and self.GetCurrentRound().IsCzarSelecting():
      winning_player = self.GetCurrentRound().GetPlayerByCard(card)
      winning_player.points += 1
      self.GetCurrentRound().ChangeState(2,3)
      for p in self.players:
        p.emit(EVT_GAME_STATE,state=2,winner=winning_player.name)
      self.ForceUpdate()


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
