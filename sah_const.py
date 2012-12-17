# Internal event names, generally don't touch these.
EVT_LOBBY_DATA_REQUEST = "lobby"
EVT_CHAT_MSG = "chat"

EVT_GAME_JOIN = "game_join"
EVT_GAME_LEAVE = "game_leave"
EVT_GAME_CREATE = "game_create"
EVT_GAME_PLAYED_CARDS = "game_played_cards"
EVT_GAME_ROUND_DATA = "game_round_data"
EVT_GAME_STATE = "game_state"
EVT_GAME_WINNER_SELECT = "game_winner_select"
EVT_GAME_PLAYER_LIST = "game_player_list"

EVT_USER_EJECT = "user_get_out"
EVT_USER_REG = "user_register"

EVT_CARD_GET = "card_get"
EVT_CARD_SUBMIT = "card_submit"
EVT_CARD_PLAYED_NOTIFICATION = "card_played"

STATE_GAME_NOT_STARTED = 0
STATE_PLAYING = 1
STATE_CZAR_SELECT = 2
STATE_SHOW_WINNER = 3

MAX_HANDLES_PER_GAME = 250000

# Strings (use for localisation)
STR_MAX_CONNECTIONS = "Maximum connections per game has been reached."
STR_HOST_LEFT = "The game creator has left."