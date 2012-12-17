// SCREEN STATES
var screen = {
  elements: [
    '#game-form-wrapper',
    '#login',
    '#lobby',
    '#password',
    '#game'
  ],

  // Screen reset. Hides everything except the title basically.
  // if a callback is provided it'll pass that to the FIRST element that fades.
  ResetScreen: function(callback) {
    var called = false;
    for(var i = 0; i < this.elements.length; i++) {
      if ($(this.elements[i]).is(':visible')) {
        if (!called && arguments.length > 0) {
          $(this.elements[i]).fadeOut('fast', callback);
        } else {
          $(this.elements[i]).fadeOut('fast');
        }
      }
    }
  },

  // Pass the selector for the element to transition to.
  ChangeTo: function(elm) {
    this.ResetScreen(function() {
      $(elm).fadeIn();
      if ($(elm).hasClass('invert')) {
        $('body').animate({'color': '#fff', 'background-color': '#000'});
      } else {
        $('body').animate({'color': '#000', 'background-color': '#ddd'});
      }
    });
  },

  // Just in case something goes weird
  DisplayError: function(error) {
    $('#error').html('<div class="black"></div><div class="card">' + error + "</div>");
    this.ChangeTo('#error');
  }
};


// GAME STUFF
var game = {
  IsCzar: false,

  RegisterName: function(name) {
    sock.emit(settings.EVT_USER_REG,{'name':name});
  },

  RegisterGame: function(name, maxplayers, password) {
    password = password || null;
    sock.emit(settings.EVT_GAME_CREATE,{'name':name,'maxplayers':maxplayers,'password':password});
  },

  UpdateLobbies: function(data) {
    var lobby = $('#lobby');
    lobby.html("");

    data = data.game_list;
    if (data.length >= 1) {
      $.each(data, function(k, v) {
        if (v.password) {
          lobby.append('<div class="card lobby-card password">' + v.creator + ' presents <br/><span class="game-name">' + v.name + '</span><br />' + v.players + '/' + v.maxplayers + '<br /><img src="static/lock.png" /></div>');
        } else {
          lobby.append('<div class="card lobby-card">' + v.creator + ' presents <br/><span class="game-name">' + v.name + '</span><br />' + v.players + '/' + v.maxplayers + '</div>');
        }
      });
      $(".lobby-card").each(function (i) {
        $(this).click(function () {
          var name = $(this).find('.game-name').text();
          if ($(this).hasClass('password')) {
            screen.ChangeTo('#password');
            $('#password-form').data('game-name', name);
          } else {
            game.JoinAttempt(name);
          }
        });
      });
    }
    // Add Lobby div
    lobby.append('<div id="add-game" class="card" onclick="screen.ChangeTo(\'#game-form-wrapper\');" style="text-align:center;"><span style="font-size:190px;">+</span></div>');
  },

  JoinAttempt: function(name, password) {
    if (arguments.length == 2) {
      sock.emit(settings.EVT_GAME_JOIN, { "name": name, "password": password });
    } else {
      sock.emit(settings.EVT_GAME_JOIN, { "name": name });
    }
  },

  JoinGame: function() {
    screen.ChangeTo('#game');
  },

  RegistrationComplete: function() {
    sock.emit(settings.EVT_LOBBY_DATA_REQUEST);
    setInterval(function() {
      sock.emit(settings.EVT_LOBBY_DATA_REQUEST);
    }, 5000);
    screen.ChangeTo('#lobby');
  },

  UpdatePlayers: function(data) {
    var player_div = $('#player-list');
    player_div.html("");
    var czar = "";
    $.each(data.player_list,function(k, v){
      if(v.czar) czar = "czar";
      else czar = "";
      player_div.append('<div class="player ' + czar + '"> <span class="player-name">' + v.name.toString() + '</span><span class="player-score">' + v.points.toString() + '</span></div>');
    });
  },

  UpdateHand: function(data) {
    var hand_div = $('#hand-cards');
    hand_div.html("");
    $.each(data.cards,function(k, v){
      hand_div.append('<div class="card card-small"><span class="card-text">' + v + '</span><div class="card-number"></div></div>');
    });
    /* $("#hand-cards").append('<div class="card card-black card-small card-submit" style="display:none">Submit<div class="card-number"></div></div>'); */
    this.InitHand();
  },

  UpdateRound: function(data) {
    this.IsCzar = false;
    // p sure this is racist
    var black_div = $('#black-card');
    black_div.html("");
    black_div.append('<div class="card card-black card-small">' + data.black_card + '</div>');
    if (data.czar) {
      // if we are the czar
      this.IsCzar = true;
      $('.hand').fadeOut('slow', function() {
        $('.hand').hide();
      });
    } else {
      $('.hand').show();
      $('#hand-cards').show();
      $('#played-cards').fadeOut();
    }
    $('#my-cards').html('');
    $('#my-cards').show();
    
    this.maxCards = data.draw_amount;
    this.selectedCards = [];
  },

  PlayCards: function() {
    // reset the cards
    $('#hand-cards').find('.card-number').html('');
    $('#hand-cards').find('.card').removeClass('card-selected');
    $('#hand-cards').find('.card').off('dblclick');

    for (var i = 0; i < this.selectedCards.length; i++) {
      var elm = $(this.selectedCards[i]);
      elm.appendTo('#my-cards');
      elm.off('click');
    }
    $("#hand-cards").fadeOut();
  },

  PlayCardsAttempt: function() {
    var cards = [];
    for (var i = 0; i < this.selectedCards.length; i++) {
      var elm = $(this.selectedCards[i]);
      cards.push(elm.find('.card-text').text());
    }
    sock.emit(settings.EVT_CARD_SUBMIT, cards);
  },

  InitHand: function() {
    var that = this;

    // reset the cards
    $('#hand-cards').find('.card-number').html('');
    $('#hand-cards').find('.card').removeClass('card-selected');
    $('#hand-cards').find('.card').off('dblclick');
    $('#black-card').off('click');
    // Clear all delegates, should fix weird double click issue.

    $("#played-cards").fadeOut('fast');
  },

  UpdatePlayedCards: function(data) {
    $('#played-cards').fadeIn();
    $('#played-cards').html('');
    $('#my-cards').fadeOut();
    console.log(data);
    $.each(data.card_data, function(i, cards) {
      // lists of cards for > 1 card rounds
      var s = '<div class="card-group">';
      $.each(cards, function(i, card) {
        s += '<div class="card card-small"><span class="card-text">' + card + '</span></div>';
      });
      $('#played-cards').append(s + '</div>');
    });
  },

  WinningCard: null,

  SelectWinner: function(data) {
    if (this.IsCzar) {
      // we need sick azz event handlers
      var that = this;
      $('#played-cards').delegate('.card-group', 'click', function() {
        if (that.WinningCard) {
          that.WinningCard.removeClass('group-selected');
        }
        that.WinningCard = $(this);
        $(this).addClass('group-selected');
        sock.emit(settings.EVT_GAME_WINNER_SELECT,{'card':$($(".group-selected").find('span')[0]).text()});
        $('#played-cards').undelegate();
      });
    } else {
    }
  }
};


// CHAT STUFF
var chat = {
  UpdateChatLog: function(data) {
     var chat_div = $('#chat-lines');
     chat_div.append('<div class="chat-line"><span class="chat-name">' + data.nick + '</span><span class="chat-message">' + data.msg + '</span></div>');
     chat_div.scrollTop(chat_div.innerHeight());
  },

  SendChatMessage: function(msg) {
    sock.emit(settings.EVT_CHAT_MSG,{'msg':msg});
  }
};


// SOCKET STUFF
$(function () {
  sock = io.connect(document.location.origin + "/gs", {
    rememberTransport: false
  });

  sock.on(settings.EVT_CHAT_MSG, function (data) {
    $('#output').append(data);
  });

  sock.on(settings.EVT_USER_REG, function (data) {
    if (data.status) {
      game.RegistrationComplete(data);
    } else {
      $('#register-output').html("Name taken.");
    }
  });

  sock.on(settings.EVT_LOBBY_DATA_REQUEST, function (data) {
    game.UpdateLobbies(data);
  });

  sock.on(settings.EVT_GAME_CREATE,function (data) {
    if(data.status) {
      game.JoinGame();
    } else {
      // Display error message or just do nothing
    }
  });

  sock.on(settings.EVT_GAME_JOIN, function (data) {
    if(data.status) {
      game.JoinGame();
    } else {
      $('#password-output').html('Incorrect password');
    }
  });

  sock.on(settings.EVT_GAME_PLAYER_LIST,function (data) {
    game.UpdatePlayers(data);          
  });

  sock.on(settings.EVT_CARD_GET,function (data) {
    game.UpdateHand(data);          
  });

  sock.on(settings.EVT_GAME_ROUND_DATA,function (data) {
    game.UpdateRound(data);
  });

  sock.on(settings.EVT_CARD_SUBMIT,function (data) {
    if (data.status) {
      game.PlayCards();
    }
  });

  sock.on(settings.EVT_CARD_PLAYED_NOTIFICATION, function(data) {
    $('#played-cards').append('<div class="card card-small"></div>');
  });

  sock.on(settings.EVT_GAME_PLAYED_CARDS, function(data) {
    game.UpdatePlayedCards(data);
  });

  sock.on(settings.EVT_CHAT_MSG,function (data) {
    chat.UpdateChatLog(data);
  });

  sock.on(settings.EVT_GAME_STATE, function (data) {
    switch (data.state) {
    case 1:
      game.SelectWinner();
      break;
    }
  });
      $("#hand-cards").delegate('.card-submit','click',function() {
      game.PlayCardsAttempt();
    });
    $('#hand-cards').delegate('.card', 'click', function() {
      var elm = $(this);
      console.log(elm);
      if ($(this).hasClass("card-submit")){
        return; // get out we dont care, this is the dang submit card
      }
      // update the array
      if (elm.hasClass('card-selected')) {
        // if the card is selected, remove it from the array
        var ind = $.inArray(this, game.selectedCards);
        // cards.indexOf(that); always returns false for some reason.
        game.selectedCards.splice(ind, 1);
      } else {
        // otherwise add it to the array
        if (game.selectedCards.length >= game.maxCards) {
          // if the array is full pop the last card and replace it
          game.selectedCards.pop();
          game.selectedCards.push(this);
        } else {
          // otherwise just push the card
          game.selectedCards.push(this);
        }
      }

      // reset the cards
      $('#hand-cards').find('.card-number').html('');
      $('#hand-cards').find('.card').removeClass('card-selected');
      $('#hand-cards').find('.card').off('dblclick');
      $('#black-card').off('click');


      // set the cards from the array
      for (var i = 0; i < game.selectedCards.length; i++) {
        var card = $(game.selectedCards[i]);
        card.addClass('card-selected');
        if (game.maxCards > 1) {
          card.find('.card-number').html(i+1);
        }
      }

      if(game.selectedCards.length >= game.maxCards) {
        $(".card-submit").fadeIn();
      } else {
        $(".card-submit").fadeOut();
      }

      // if this is the last card give it the ~~special event handler~~
      if (game.maxCards == game.selectedCards.length) {
        $('#black-card').click(function() {
          game.PlayCardsAttempt();
        });
      }
    });
});
