// Socket.io setup
$(function() {
  sock = io.connect(document.location.origin + "/gs", {
    rememberTransport: false,
    reconnect: false
  });

  // --------------------------------------------------------------------------
  // Player obj events
  sock.on(settings.EVT_USER_REG, function(data) {
    if (data.status) {
      $(document).trigger('RegistrationSuccess')
    } else {
      $(document).trigger('RegistrationError', data.reason)
    }
  });

  sock.on(settings.EVT_LOBBY_DATA_REQUEST, function(data) {
    $(document).trigger('LobbyUpdate', [data.game_list])
  });

  sock.on(settings.EVT_GAME_CREATE, function(data) {
    if (data.status) {
      $(document).trigger('AddGameSuccess')
    } else {
      $(document).trigger('AddGameError')
    }
  });

  sock.on(settings.EVT_GAME_JOIN, function(data) {
    if (data.status) {
      $(document).trigger('JoinGameSuccess', data.handle)
    } else {
      $(document).trigger('JoinGameError')
    }
  });

  // --------------------------------------------------------------------------
  // Game obj events
  sock.on(settings.EVT_GAME_STATE, function(data) {
    $(document).trigger('GameStateUpdate', data.state)
  });

  sock.on(settings.EVT_GAME_PLAYER_LIST, function(data) {
    $(document).trigger('PlayerListUpdate', [data.players]);
  });

  sock.on(settings.EVT_GAME_ROUND_DATA, function(data) {
    $(document).trigger('RoundDataUpate', data);
  });

  sock.on(settings.EVT_CARD_GET, function(data) {
    $(document).trigger('HandUpdate', [data.cards]);
  });

  // darvs shite, submit the index of the card, Reece.
  sock.on(settings.EVT_CARD_SUBMIT, function(data) {
    if(data.status) {
      $(document).trigger('SubmitCardSuccess')
    } else {
      $(document).trigger('SubmitCardError')
    }
  });

  sock.on(settings.EVT_CARD_PLAYED_NOTIFICATION,function(data) {
    $(document).trigger('CardPlayedNotification', data.handle);
  });

  sock.on(settings.EVT_GAME_PLAYED_CARDS, function(data){
    console.log(data);
    $(document).trigger('PlayedCards', [data.cards]);
  });

  sock.on(settings.EVT_GAME_WINNER_SELECT, function(data) {
    $(document).trigger('WinnerSelected', data.winner);
  });

  sock.on(settings.EVT_CHAT_MSG, function(data) {
    $(document).trigger('ChatMessage', data);
  });

});


// Player (as in the player playing in this browser) things go here
var player = {
  handle: 0,
  
  register: function(name) {
    sock.emit(settings.EVT_USER_REG, {'name': name})
  },

  // --------------------------------------------------------------------------
  add_game: function(name, maxplayers, password) {
    console.log(arguments);
    if (typeof password === 'undefined') {
      sock.emit(settings.EVT_GAME_CREATE, {
        'name': name,
        'maxplayers': maxplayers
      });
    } else {
      sock.emit(settings.EVT_GAME_CREATE, {
        'name': name,
        'maxplayers': maxplayers,
        'password': password
      });
    }
  },

  // --------------------------------------------------------------------------
  join_game: function(name, password) {
    if (typeof password === 'undefined') {
      sock.emit(settings.EVT_GAME_JOIN, {'name': name});
    } else {
      sock.emit(settings.EVT_GAME_JOIN, {
        'name': name,
        'password': password
      });
    }
  },

  // ----------- Darvs Crud
  // Submit the indexes of the cards (e.g. 0 and 5)
  submit_card: function(index_array) {
    sock.emit(settings.EVT_CARD_SUBMIT,{'cards':index_array});
  },

  select_winner: function(winner_handle) {
    sock.emit(settings.EVT_GAME_WINNER_SELECT,{"handle":winner_handle});
  },

  select_winner_success: function() {
    console.log('Valid winner handle selected.');
  },
  select_winner_failure: function() {
    console.log('Invalid winner handle.');
  }
};


// Game things go here
var game = {
  players: {},

  card_played: function(handle) {
    // maybe put a client thing that changes the playerlist to show they have played? nfi.
    console.log(handle.toString() + ' has played a card.');
  },

  winner_picked: function(handle){
    console.log(handle.toString() + 'won the game.');
  },

  send_chat: function(message) {
    sock.emit(settings.EVT_CHAT_MSG, {'message': message});
  }
};
