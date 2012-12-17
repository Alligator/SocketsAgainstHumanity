// Events

// Nothing is really based on gamestate which is bad.

// ----------------------------------------------------------------------------
// Registration
$(document).bind('RegistrationSuccess', function() {
  fadeOutModal('.registration');
  $('.lobbies').fadeIn();
});
$(document).bind('RegistrationError', function(e, reason) {
  $('.registration .modal-error').text(reason);
});

function register(name) {
  player.register(name);
};


// ----------------------------------------------------------------------------
// Lobby
var lobbies = [];
$(document).bind('LobbyUpdate', function(e, lob) {
  // creator: "gate"
  // maxplayers: 20
  // name: "butt"
  // password: false
  // players: 1
  lobbies = lob

  var elm = $('.lobbies').empty()
  $.each(lobbies, function(i, game) {
    var html = '<div class="card lobby btn" data-index="'+i+'">'+game.name+'<br />'+game.players+'/'+game.maxplayers+'<br />';
    if (game.password) {
      html += '<img src="static/lock.png />';
    }
    html += '</div>';
    elm.append(html);
  });

  elm.append('<div class="card btn add-game">+</div>');
});


// ----------------------------------------------------------------------------
// Game creation
$(document).bind('AddGameSuccess', function(e) {
  console.log('game successfully added');
});
$(document).bind('AddGameError', function(e) {
  console.log('game not added');
});

function add_game(name, maxplayers, password) {
  player.add_game(name, maxplayers, password);
}


// ----------------------------------------------------------------------------
// Game joining
var handle = 0;
$(document).bind('JoinGameSuccess', function(e, hndl) {
  handle = hndl;
  $('.lobbies').fadeOut('fast', function() {
    $('.game').fadeIn();
  });
});
$(document).bind('JoinGameError', function(e) {
  console.log('game not joined');
});

function join_game(name, password) {
  player.join_game(name, password);
}


// ----------------------------------------------------------------------------
// In-Game

// General updates
$(document).bind('GameStateUpdate', function(e, state) {
  if (state == settings.STATE_GAME_NOT_STARTED) {
    fadeInModal('.waiting');
  } else {
    fadeOutModal('.waiting');
  }
});

var players = {};
$(document).bind('PlayerListUpdate', function(e, player_list) {
  players = {};
  $.each(player_list, function(i, player) {
    players[player.handle] = {
      name: player.name,
      points: player.points
    };
  });
  UpdatePlayers();
});

var roundData;
$(document).bind('RoundDataUpate', function(e, rnd_data) {
  // black_card: string
  // czar: number
  // draw_amt: number
  roundData = rnd_data;
  console.log(roundData);
  selectedCards = [];

  $('.winning-cards').empty();
  $('.black-card').text(roundData.black_card);
  $('.my-hand').fadeIn();
  if (roundData.czar == handle) {
    $('.czar-overlay').fadeIn();
  } else {
    $('.czar-overlay').fadeOut();
  }
  UpdatePlayers();
  updateCards();
});

var myCards = []
$(document).bind('HandUpdate', function(e, cards) {
  myCards = cards;
});

var submitted = false;
$(document).bind('SubmitCardSuccess', function(e) {
  $('.submit-card').fadeOut();
  $('.my-hand').fadeOut();
  submitted = true;
});
$(document).bind('SubmitCardError', function(e) {
  console.log('submit card error');
});

var played_cards = {};
$(document).bind('PlayedCards', function(e, cards) {
  $('.czar-overlay').fadeOut();
  $('.my-hand').fadeOut();
  $('.winning-cards').empty();

  var elm = $('.submitted-cards').empty().fadeIn();

  $.each(cards, function(i, cardgroup) {
    var out = '<div class="card-group" data-handle="'+cardgroup[0]+'">';
    played_cards[cardgroup[0]] = cardgroup[1];
    $.each(cardgroup[1], function(i, card) {
      out += '<div class="card btn">'+card+'</div>';
    });
    elm.append(out + '</div>');
  });
});
$(document).bind('CardPlayedNotification', function(e, handle) {
  if (submitted) {
    var elm = $('submitted-cards').fadeIn();
    var out = '<div class="card-group">'
    for (var i = 0; i < roundData.draw_amt; i++) {
      out += '<div class="card"></div>';
    }
    elm.append(out + '</div>');
  }
});

$(document).bind('WinnerSelected', function(e, winner) {
  var elm = $('.winning-cards');
  $('.submitted-cards').fadeOut();
  $.each(played_cards[winner], function(i, card) {
    elm.append('<div class="card">'+card+'</div>');
  });
});

function UpdatePlayers() {
  if (typeof roundData === 'undefined') return;
  var elm = $('.user-list').empty();

  $.each(players, function(playerHandle, player) {
    var cl = "";
    if (playerHandle == handle) cl += " me";
    if (playerHandle == roundData.czar) cl += " czar";
    elm.append('<div class="user'+cl+'"><div class="user-name">'+player.name+'</div><div class="user-score">'+player.points+'</div></div>');
  });
}

// indexes is always an array, even if submitting one card
function submit_card(indexes) {
  player.submit_card(indexes);
}

// winner is the winner's handle, not name
function select_winner(winner) {
  player.select_winner(winner);
}

// ----------------------------------------------------------------------------
// Chat
$(document).bind('ChatMessage', function(e, data) {
  var playerName = players[data.handle].name;
  var elm = $('.chat-lines');
  elm.append('<div class="chat-line"><strong>'+playerName+'</strong> '+data.message+'</div>');
  elm.scrollTop(elm[0].scrollHeight);
});

function sendChatMessage(message) {
  game.send_chat(message);
}

// ----------------------------------------------------------------------------
// UI based event handlers
var lobby;
var selectedCards = [];
// var roundData = {draw_amt: 2}; // TODO delete
$(function() {
  // INITAL SETUP
  // $('.registration').hide();
  $('.new-game').hide();
  $('.game').hide();
  $('.password').hide();
  $('.waiting').hide();
  $('.lobbies').hide();


  $('.winning-cards').delegate('.card-selected', 'click', function() {
    var ind = $.inArray($(this).data('id'), selectedCards);
    selectedCards.splice(ind, 1);
    updateCards();
  });

  $('.my-hand').delegate('.card', 'click', function() {
    var elm = $(this);
    var id = elm.data('id');

    // update the array
    if (selectedCards.length >= roundData.draw_amt) {
      selectedCards.pop();
      selectedCards.push(id);
    } else {
      // otherwise just push the card
      selectedCards.push(id);
    }

    updateCards();
  });

  $('.submit-card').click(function() {
    var cards = [];
    $.each(selectedCards, function(i, card) {
      cards.push(getCardFromId(card).data('id'));
    });
    submit_card(cards);
  });

  $('.submitted-cards').delegate('.card-group', 'click', function() {
    if (handle != roundData.czar) return;

    select_winner($(this).data('handle'));
  });

  $('.lobbies').on('click', '.lobby', function() {
    lobby = lobbies[$(this).data('index')];
    console.log(lobby);
    if (lobby.password) {
      fadeInModal('.password');
    } else {
      join_game(lobby.name, null); // Why was this sending the max players as the password?
    }
  });

  $('.lobbies').on('click', '.add-game', function() {
    fadeInModal('.new-game');
  });

  $('.modal.closeable').click(function(e) {
    var target = $(e.target);
    // we only want the part
    if (target.hasClass('modal')) {
      fadeOutModal(this);
      // reset stuff we may have set
      // lobby = undefined;
    }
  });

  // updateCards(); // TODO delete
  // FORM THINGS
  $('.form-reg').submit(function() {
    var username = $('.form-reg-name').val();
    register(username);
    return false;
  });

  $('.form-ng').submit(function() {
    var name = $('.form-ng-name').val();
    var maxplayers = Number($('#form-ng-maxplayers').val());
    var password = $('.form-ng-pass').val();
    console.log(password);
    if (password == "") {
      add_game(name, maxplayers);
    } else {
      add_game(name, maxplayers, password);
    }
    fadeOutModal('.new-game');
    return false;
  });

  $('.form-pass').submit(function() {
    var password = String($('.form-pass-pass').val());
    fadeOutModal('.password');
    join_game(lobby.name, password);
    return false;
  });

  $('.chat-input').submit(function() {
    var message = $('.chat-input-text').val();
    $('.chat-input-text').val('');
    sendChatMessage(message);
    return false;
  });
});

// var myCards = [0,1,2,3]

function updateCards() {
  var elm = $('.my-hand').empty();
  $('.winning-cards').empty();

  // reset the cards
  $.each(myCards, function(i, card) {
    elm.append('<div class="card btn" data-id="'+i+'">'+card+'</div>');
  });

  // set the cards from the array
  for (var i = 0; i < selectedCards.length; i++) {
    var card = getCardFromId(selectedCards[i]);
    card.addClass('card-selected');
    card.appendTo('.winning-cards');
  }

  if (selectedCards.length == roundData.draw_amt) {
    $('.submit-card').fadeIn();
  } else {
    $('.submit-card').fadeOut();
  }
}

function getCardFromId(id) {
  return $('[data-id='+id+']');
}

function fadeOutModal(selector) {
    var elm = $(selector);
    elm.find('.modal-content').slideUp('fast', function() {
      elm.fadeOut();
    });
}

function fadeInModal(selector) {
    var elm = $(selector).fadeIn('fast', function() {
      elm.find('.modal-content').slideDown('fast');
    });
}
