Sorry for the shitty names, I think that'll be the first part of refactoring.
There's a lot of unneccesary shite.

Event: 'chat'

Send: msg : 'hello' Receive: name : 'darvell', msg: 'sup'

Event:  'get_out' Send: N/A Receive: Nothing. Just a notification for the
client that you've been killed.

Event: 'get_hand'

Send: Sends the players hand. Never use the send command though, will probably
cause desyncs. The server knows when to send them. Might deprecate soon.

Receive: A json array of the card strings.

Event: 'round_data'

Send: Might force the data to be sent. Don't do this.  Receive: "czar" : True,
"black_card": "I'm _", "draw_amount": 1

Event: 'play_card'

Send: Send an array of cards. Even if it's only one card, it must be in an
array. Name of argument is 'cards'.  Receive: 'status':True or False depending
on whether the card is valid.

Event: 'idle_counter'

Send: Nothing.  Receive: Only emitted when the idle counter (10 seconds) will
begin.


Event: 'czar_select' Receive: It's time for the czar to select. This might
change into just a general gamestate change function.

Event: 'played_card' Receive: 'name':'darvell', Sends the name of who just
played a card.

Event: 'game_end' Receive: 'msg':'The creator has left.', Sends a message to
all the remaining clients that the game has ended and why.

Event: 'played_cards'

Receive: 'card_data' : [["darvell":["card","card"],"alligator":["woof","dog"]],
sent when it's time for the czar to choose. I might change this so a name isn't
sent to the client since the round ending state event sends who the winner is
and it's determined by the card data anyway. 

Event: 'select_winner'

Send: Send the string of the selected card (don't send an array, just send the
exact card clicked, the server determines who that pair belonged to anyway..)
as the argument 'card'.
