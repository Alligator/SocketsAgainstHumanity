
// EVENT HANDLERS
$(function() {

  // REGISTRATON
  //---------------------------------------------------------------------------
  $('.form-reg').on('submit', function() {
    var name = $('.form-reg-name').val();
    player.register(name);
    return false;
  });

  $(document).bind('RegistrationSuccess', function(e) {
    console.log('registration succeeded');
    $('.registration').fadeOut();
  });

  $(document).bind('RegistrationError', function(e, err) {
    console.log('registration failed:', err);
  });

  // LOBBIES
  //---------------------------------------------------------------------------
  $(document).bind('LobbyUpdate', function(e, lobbies) {
    $('.lobbies').html('').fadeIn();
    $.each(lobbies, function(i, lobby) {
      $('.lobbies').append(Mustache.render(templates.lobbies, lobby));
    });
  });

  $(document).on('click', '.lobby', function(e) {
    var $e = $(e.target);
    var name = $e.data('name');
    if ($e.data('password')) {
      $('.password').fadeIn().data('name', name)
    } else {
      console.log('b');
      player.join_game(name);
    }
  });

  $(document).bind('JoinGameSuccess', function(e, handle) {
    console.log('join game succeeded', handle);
    $('.lobbies').fadeOut(function() {
      $('.game').fadeIn();
    });
  });

  $(document).bind('JoinGameError', function(e) {
    console.log('join game failed');
  });

  // IN GAME
  //---------------------------------------------------------------------------
  $(document).bind('GameStateUpdate', function(e, state) {
    console.log('game state', state);
  });
  $(document).bind('PlayerListUpdate', function(e, data) {
    console.log('player list', data);
    $('.user-list').html('');
    $.each(data, function(i, player) {
      $('.user-list').append(Mustache.render(templates.user, player));
    });
  });
  $(document).bind('RoundDataUpate', function(e, data) {
    console.log('round data', data);
  });


  // GENERAL
  //---------------------------------------------------------------------------
  $(document).on('click', '.closeable', function(e) {
    $e = $(e.target);
    if ($e.hasClass('closeable'))
      $e.fadeOut();
  });
});
