# TODO: Clean/everything else
class Round():
  def __init__(self):
    self.card_czar = None
    self.black_card = None
    self.played_cards = dict()
    self.winning_card = None # list of winning card/cards
    self.winning_player = None 
    self.draw_amt = 0
    self.started = False # Still needed?
    self.counter = 60
    self.state = 1

  def CardSubmit(self,player,cards):
    # stop naughty people
    if self.PlayerHasPlayed(player.handle):
      return False
    if player.handle is self.GetCzarHandle():
      return False

    result = []

    for index in cards:
      print index
      try:
        result.append(player.hand[index])
      except:
        return False

    if len(result) != self.draw_amt:
      return False

    self.played_cards[player.handle] = result
    return True

  def SetCzarHandle(self,czar):
    self.card_czar = czar

  def GetCzarHandle(self):
    return self.card_czar
  def GetWinnerHandle(self):
    return self.winning_player

  def PlayerHasPlayed(self,handle):
    return handle in self.played_cards.keys()

  def SetBlackCard(self,card):
    self.black_card = card
  
  def GetBlackCard(self):
    return self.black_card

  def GetDrawAmount(self):
    return self.draw_amt

  def SetDrawAmount(self,amt):
    self.draw_amt = amt

  def GetState(self):
    return self.state

  def IsInGame(self):
    return self.state == 1

  def IsCzarSelecting(self):
    return self.state == 2

  def IsShowingEnd(self):
    return self.state == 3

  def ChangeState(self,state,counter = 10):
    self.state = state
    self.counter = counter

  def RemovePlayerCards(self,player):
    try:
      del self.played_cards[player.handle]
    except:
      pass