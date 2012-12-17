from tornado import web,ioloop
from tornadio2 import SocketConnection, TornadioRouter, SocketServer,event
import os, json, logging, random,cgi,time,signal,sys
from classes.game import Game
from classes.player import Player
from sah_const import *
from generate_settings import generate_settings
import settings

# Global objects that hold all the connected clients and running games.
clients = []
games = []

# The game socket class, handles event receiving.
class GameSocket(SocketConnection):

  # Due to the strange nature of overriding the init with tornadio, a fake 
  # constructor is used. This needs to be looked into much further.
  def Fauxstructor(self):
    self.name = None
    self.player = None

  # Call the fake constructor on a new connection and add the socket connection
  # to the clients list for further modification.
  def on_open(self,info):
    self.Fauxstructor()
    clients.append(self)

  # Method stub required for Tornadio2.
  def on_message(self,message):
    pass

  # Method provided by tornadio2 on connection close.
  def on_close(self):
    if self in clients:
      if self.player:
        self.player.LeaveGame()
    clients.remove(self)

  # Handles chat message sending. TODO: Targets (users)
  @event(EVT_CHAT_MSG)
  def EventChatMessage(self,message):
    if self.player:
     self.player.SendChatMessage(cgi.escape(message))
  
  @event(EVT_USER_REG)
  def EventUserRegistration(self,name):
    name = cgi.escape(name)
    for c in clients:
      if c.name == name:
        self.emit(EVT_USER_REG,status=False,reason="Name taken.")
        return
    if len(name) > 14:
      self.emit(EVT_USER_REG,status=False,reason="Name too long.")
      return

    self.name = name
    self.emit(EVT_USER_REG,status=True)

  # CARD RELATED EVENTS
  # Allow a client to force sync the players hand. To be deprecated.
  @event(EVT_CARD_GET)
  def EventCardRetrieve(self):
    self.emit(EVT_CARD_GET,{"cards":self.player.hand})

  @event(EVT_CARD_SUBMIT)
  def EventCardSubmit(self,cards):
    if self.player:
      self.player.SubmitCard(cards)

  @event(EVT_GAME_JOIN)
  def EventGameJoinAttempt(self,name,password = None):
    if self.name and not self.player:
      game_obj = None
      for game in games:
        if game.name == name:
          game_obj = game

      if game_obj:
        if game_obj.PlayerJoin(self,password):
          return

    self.emit(EVT_GAME_JOIN,status=False,handle=None)
  
  @event(EVT_GAME_LEAVE)
  def EventGameLeave(self):
    if self.player.game:
      self.player.game.RemovePlayer(self.player)
      client.emit(EVT_USER_EJECT)

  @event(EVT_GAME_CREATE)
  def EventGameCreate(self,name,maxplayers,password = None):
    if self.name:
      for game in games:
        if game.name == name:
          self.emit(EVT_GAME_CREATE,status=False)
          return
      g = Game(name=name,max_players=maxplayers,creator=self,password=password)
      games.append(g)
      self.player.game = g
      self.emit(EVT_GAME_CREATE,status=True)

  @event(EVT_GAME_WINNER_SELECT)
  def EventGameWinnerSelected(self,handle):
    if self.player:
      try:
        handle = int(handle)
      except:
        return
      if handle >= 0:
        self.player.SelectWinner(handle)

class IndexHandler(web.RequestHandler):
  def get(self):
    self.render("web/game.html")
class TestHandler(web.RequestHandler):
  def get(self):
    self.render("web/testing.html")


# Defines the name of the socket, in our case we use "/gs" by default.
class RouterConnection(SocketConnection):
  __endpoints__ = {settings.SOCKET_ENDPOINT: GameSocket}

# Iterate through the games and send the pulse function.
# This is called on the periodic callback per second in the IO loop.
# Also send the lobby to clients not in a game.
def GamePulse():
  game_list = []
  for game in games:
    if game.remove:
      games.remove(game)
    else:
      game.Pulse()
      game_list.append(game.GameLobbyData()) # Expensive, to change.
  
  for client in clients:
    if client.name and not client.player:
      client.emit(EVT_LOBBY_DATA_REQUEST,game_list=game_list)


def InitServer():
  if settings.LOGGING:
    logging.getLogger().setLevel(logging.DEBUG)
  generate_settings()
  SAHRouter = TornadioRouter(RouterConnection)
  SAHApplication = web.Application(SAHRouter.apply_routes([(r"/",IndexHandler),(r"/test/",TestHandler),(r"/static/(.*)", web.StaticFileHandler, {"path": os.path.abspath(os.path.join(os.getcwd(),'web','static'))}),]),socket_io_port=settings.WS_PORT, debug=settings.DEBUG)
  SAHSocketServer = SocketServer(SAHApplication,auto_start = False)
  # Add periodic callback (aka faux-thread) into the ioloop before starting
  # Tornado doesn't respond well to running a thread while the IO loop is going. 
  cb = ioloop.PeriodicCallback(GamePulse,1000,SAHSocketServer.io_loop)
  cb.start()
  SAHSocketServer.io_loop.start()

if __name__ == '__main__':
  InitServer()
