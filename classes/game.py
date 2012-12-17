from sah_const import *
import random
def PlayerFilter(obj):
  return obj is not None

class Game():
  # game_name,max_players,game_creator,password = None
  def __init__(self,**kwargs):
    self.__dict__.update(kwargs)
    self.player_list = []
    self.active_players = lambda: filter(PlayerFilter,self.player_list) # Is this expensive?
    self.rounds = []
    self.deck = Deck()
    self.remove = False # Mark when the game should be removed.
    self.PlayerCreateObject(self.creator)
    self.creator = self.player_list[0]

  # Player methods that generally aren't game logic.
  def PlayerJoin(self,socket,password):
    # Ensure the player isn't somehow already in the game.
    for player in self.active_players():
      if player.socket is socket:
        return False

    if password == self.password and self.PlayerCount() < self.max_players:
      if len(self.player_list) > MAX_HANDLES_PER_GAME:
        GameEnd(STR_MAX_CONNECTIONS)
        return False
      return self.PlayerCreateObject(socket) 

  def PlayerCreateObject(self,socket):
    player_object = Player(socket,self)
    self.PlayerAdd(player_object)
    return True

  def PlayerGetNewHandle(self):
    self.player_list.append(None)
    return len(self.player_list) - 1

  def PlayerAdd(self,player):
    # Place player into actual player list
    self.player_list[player.handle] = player
    player.Emit(EVT_GAME_JOIN,status=True,handle=player.handle) # Make sure the player gets the handle in time
    self.DataPlayerList()
    # Generate player hand
    for i in range(0,10):
      player.hand.append(self.deck.GetRandomWhiteCard())
    if self.RoundCurrent():
      player.SendHand()
      self.DataRoundInfo(player)
   
    if not self.RoundCurrent() and self.PlayerCount() >= 2:
      rnd = self.RoundCreate()
      self.RoundStart(rnd,False)
      return

    self.DataGameState(player)
    # TODO: Send certain data depending on state

  def PlayerRemove(self,player):
    self.player_list[player.handle] = None
    if self.creator is player:
      self.GameEnd(STR_HOST_LEFT)
      return # Tell everyone it's dead and don't bother cleaning anything up.
    if self.RoundCurrent():
      self.RoundCurrent().RemovePlayerCards(player.handle)
      # TODO: Notify theres new cards and clear czar
      if self.RoundCurrent().GetCzarHandle() == player.handle:
        self.RoundEnd(False)
        # Notify players

    self.DataPlayerList()

  def PlayerCount(self):
    return len(self.active_players())

  # Round Methods
  def RoundCreate(self):
    new_round = Round()
    black_card = self.deck.GetRandomBlackCard()
    new_round.SetBlackCard(black_card)
    new_round.SetDrawAmount(black_card.count('_'))
    return new_round


  def RoundStart(self,rnd,prev_valid = True):
    # This is a stupid fix for a really stupid bug
    if len(self.active_players()) == 0:
      self.GameEnd(STR_HOST_LEFT)
      return
    
    if prev_valid:
      self.DataPlayerList() # Worth updating the playerlist for the scores
      for player in self.active_players():
        if len(self.rounds) > 1:
          if player.handle != self.rounds[len(self.rounds) - 2].GetCzarHandle():
            player.hand.append(self.deck.GetRandomWhiteCard())  

    rnd.SetCzarHandle(random.choice(self.active_players()).handle)
    self.rounds.append(rnd)
    for player in self.active_players():
      player.SendHand()
      self.DataRoundInfo(player)
      self.DataGameState(player)


  def RoundEnd(self,valid = True):
    temp = self.RoundCreate()
    self.RoundStart(temp,valid)

  def RoundStateChange(self,state,counter = 60):
    self.RoundCurrent().ChangeState(state,counter)
    for player in self.active_players():
      self.DataGameState(player)

  def RoundCurrent(self):
    if len(self.rounds) > 0:
      return self.rounds[len(self.rounds) - 1]
    return None

  # Game Logic, some methods are player driven unfortunatly.
  def GameEnd(self,reason):
    self.remove = True
    self.DataSendEventToAll(EVT_USER_EJECT,reason=reason)

  def GameCardSubmit(self,player,cards):
    if len(cards) == self.RoundCurrent().GetDrawAmount():
      if self.RoundCurrent().CardSubmit(player,cards):
        self.DataNotifyPlayedCard(player.handle)
        player.Emit(EVT_CARD_SUBMIT,status=True)
        # Check if everyone has played cards
        for player in self.active_players():
          if player.handle != self.RoundCurrent().GetCzarHandle():
            if not self.RoundCurrent().PlayerHasPlayed(player.handle):
              return
        self.DataPlayedCards()
        self.RoundStateChange(STATE_CZAR_SELECT,60)
        return

    player.Emit(EVT_CARD_SUBMIT,status=False)

  def GameCzarSelect(self,czar_handle,winner_handle):
    if not self.RoundCurrent().IsCzarSelecting():
      return
    if czar_handle != self.RoundCurrent().GetCzarHandle():
      return
    # Stop invalid winner selection
    if winner_handle > len(self.player_list) - 1 and winner_handle <= -1:
      return
    if self.player_list[winner_handle] is None:
      return
    self.player_list[winner_handle].points += 1

    # Remove all played cards
    for handle in self.RoundCurrent().played_cards.keys():
      for card in self.RoundCurrent().played_cards[handle]:
        self.player_list[handle].hand.remove(card)

    self.DataSendEventToAll(EVT_GAME_WINNER_SELECT,winner=winner_handle)
    self.RoundStateChange(STATE_SHOW_WINNER,10)

  def GameLobbyData(self):
    c = lambda x:  x is not None
    return {"name":self.name,"players":self.PlayerCount(),"maxplayers":self.max_players,"password":c(self.password),"creator":self.creator.name}

  # Data SENDING functions (generally put anything SENDING data here)
  def DataSendEventToAll(self,*args,**kwargs):
    for player in self.active_players():
      player.Emit(*args, **kwargs)

  def DataPlayerList(self):
    refined_list = []
    for player in self.active_players():
      refined_list.append({"handle":player.handle,"name":player.name,"points":player.points})
    self.DataSendEventToAll(EVT_GAME_PLAYER_LIST,players=refined_list)

  def DataRoundInfo(self,player,rnd=None):
    if rnd is None:
      rnd = self.RoundCurrent()
    player.Emit(EVT_GAME_ROUND_DATA,czar=rnd.GetCzarHandle(),black_card=rnd.GetBlackCard(),draw_amt=rnd.GetDrawAmount())

  def DataGameState(self,player):
    if self.RoundCurrent():
      player.Emit(EVT_GAME_STATE,state=self.RoundCurrent().GetState())
    else:
      player.Emit(EVT_GAME_STATE,state=STATE_GAME_NOT_STARTED)

  def DataNotifyPlayedCard(self,hndl):
    self.DataSendEventToAll(EVT_CARD_PLAYED_NOTIFICATION,handle=hndl)

  def DataPlayedCards(self):
    self.DataSendEventToAll(EVT_GAME_PLAYED_CARDS,cards=self.RoundCurrent().played_cards.items())

  def DataChatMessage(self,handle,message):
    self.DataSendEventToAll(EVT_CHAT_MSG,handle=handle,message=message)

  # Pulse is called every second in a game. This is used for timers.
  def Pulse(self):
    if self.RoundCurrent():
      if self.RoundCurrent().IsShowingEnd():
        # Show end for 10 seconds then start new round.
        if self.RoundCurrent().counter > 0:
          self.RoundCurrent().counter -= 1
        if self.RoundCurrent().counter == 0:
          self.RoundEnd()

# This isn't the nicest way to solve it but, this should fix recursive imports.
from deck import Deck
from round import Round
from player import Player
