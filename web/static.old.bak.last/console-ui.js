// Events
$(document).bind('RegistrationSuccess', function() {
  console.log('registration complete');
});
$(document).bind('RegistrationError', function(e, reason) {
  console.log('registration failed. reason: ' + reason);
});

$(document).bind('LobbyUpdate', function(e, lobbies) {
  $.each(lobbies, function(i, game) {
    console.log(game.name);
  });
});

$(document).bind('AddGameSuccess', function(e) {
  console.log('game successfully added');
});
$(document).bind('AddGameError', function(e) {
  console.log('game not added');
});

$(document).bind('JoinGameSuccess', function(e) {
  console.log('game successfully joined');
});
$(document).bind('JoinGameError', function(e) {
  console.log('game not joined');
});


// Custom functions
// These are just examples of how to implement these, hence why they just call
// other functions.
function register(name) {
  player.register(name);
};

function add_game(name, maxplayers) {
  player.add_game(name, maxplayers);
}
function add_game_password(name, maxplayers, password) {
  player.add_game(name, maxplayers, password);
}

function join_game(name) {
  player.join_game(name);
}
function join_game_password(name, password) {
  player.join_game(name, password);
}

// indexes is always an array, even if submitting one card
function submit_card(indexes) {
  player.submit_card(indexes);
}

// winner is the winner's handle, not name
function select_winner(winner) {
  player.select_winner(winner);
}
