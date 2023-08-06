class General:
    DATABASE = 'rankset'
    DEFAULT_USER = 'root'
    DEFAULT_PASSWORD = 'password'
    HOST = 'host'
    DEFAULT_HOST = '127.0.0.1'


class Keys:
    COLUMNS = 'columns'
    STATUS_CODE = 'status_code'
    DATA_TYPE = 'data_type_name'
    DATA = 'data'
    COUNTRIES = 'countries'
    COMPETITIONS = 'competitions'
    TEAMS = 'teams'
    PLAYERS = 'players'
    OVERVIEW = 'overview'
    STATS = 'stats'
    RANK = 'ranking'
    PLAYER_RANK = 'player_rank'
    POSITION = 'position'
    COUNT_OF_GAMES = 'count_of_games'
    BASE_DATA = 'base_data'
    TM_DATA = 'tm_data'
    FM_DATA = 'fm_data'
    NAME = 'name'
    CONTRACT_EXPIRES = 'contract_expires'
    MARKET_VALUE = 'market_value'
    MARKET_VALUE_TYPE = 'market_value_type'
    AGE = 'age'
    NATION = 'place_of_birth'
    ACHIEVEMENTS = 'achievements'
    TM_HISTORY = 'transfer_history'
    TM_INJURY = 'injury_stats'
    ATTRIBUTES = 'player_attributes'
    TEAM_ID = 'team_id'
    NOT_FOUND_DATA = 'Not found data'
    ERROR = 'error'
    SUCCESS = 'success'


class Routs:
    ENTITIES = 'entities'
    PLAYERS = 'players'
    RANKING = 'ranking'


class FilterData:
    DEFAULT_STATS = ['minutes on field', 'goal', 'xg shot', 'assist', 'pre assist', 'shot assist', 'interception',
                     'yellow cards', 'red cards']

    DEF_CB_PERC = ["interception", "interception success", "recovery", "recovery success", "aerial duel",
                   "aerial duel success", "defensive duel", "defensive duel success", "tackle", "tackle success",
                   "clearance", "clearance success"]

    ATTK_CB_PERC = ["pass", "pass success", "dribble", "dribble success", "progressive pass",
                    "progressive pass success", "short medium pass", "short medium pass success", "key pass",
                    "key pass success", "long pass", "long pass success"]

    DEF_DB_PERC = ["defensive duel", "defensive duel success", "tackle", "tackle success", "interception",
                   "interception success", "pressing duel", "loss", "loss success"]

    ATTK_DB_PERC = ["dribble", "dribble success", "cross", "cross success", "deep completed cross",
                    "deep completed cross success", "pass to final third", "pass to final third success",
                    "key pass", "key pass success", "offensive duel", "offensive duel success"]

    DEF_MID_SIX_PERC = ["defensive duel", "defensive duel success", "interceptions", "interceptions success",
                        "pressing duel", "loose ball duel", "loose ball duel success", "recovery",
                        "recovery success", "aerial duel", "aerial duel success", "heading", "heading success"]

    ATTK_MID_SIX_PERC = ["offensive duel", "offensive duel success", "key pass", "key pass success", "pass",
                         "pass success", "loss", "loss success", "smart pass", "smart pass success",
                         "short medium pass", "short medium pass success", "dribble", "dribble success"]

    DEF_MID_EIGHT_PERC = ["tackle", "tackle success", "defensive duel", "defensive duel success", "loose ball duel",
                          "loose ball duel success", "offensive duel", "offensive duel success", "pressing duel",
                          "interception", "interception success", "recovery", "recovery success"]

    ATTK_MID_EIGHT_PERC = ["dribble", "dribble success", "pass to final third", "pass to final third success",
                           "pass to penalty area", "pass to penalty area success", "progressive pass",
                           "progressive pass success", "shot", "shot success", "key pass", "key pass success",
                           "loss", "loss success"]

    DEF_MID_TEN_PERC = ["offensive duel", "offensive duel success", "defensive duel", "defensive duel success",
                        "loss", "loss success", "pass", "pass success", "interception", "interception success"]

    ATTACK_MID_TEN_PERC = ["dribble", "dribble success", "key pass", "key pass success", "shot", "shot success",
                           "progressive pass", "progressive pass success", "pass to penalty area",
                           "pass to penalty area success", "shot assist", "shot assist success", "touch in box",
                           "touch in box success", "xg shot", "xg assist"]

    DEF_WNG_PERC = ["defensive duel", "defensive duel success", "progressive run", "progressive run success",
                    "loss", "loss success", "pressing duel", "loose ball duel", "loose ball duel success"]

    ATTK_WNG_PERC = ["pass to penalty area", "pass to penalty area success", "assist", "shot assist",
                     "shot assist success", "shot", "shot success", "touch in box", "touch in box success", "dribble",
                     "dribble success", "cross", "cross success", "offside", "key pass", "key pass success"]

    GEN_CF_PERC = ["aerial duel", "aerial duel success", "pressing duel", "loose ball duel", "loose ball duel success",
                   "loss", "loss success", "pass", "pass success"]

    ATTK_CF_PERC = ["xg shot", "shot", "shot success", "shot on goal", "shot on goal success", "touch in box",
                    "touch in box success", "heading", "heading success", "dribble", "dribble success"]
