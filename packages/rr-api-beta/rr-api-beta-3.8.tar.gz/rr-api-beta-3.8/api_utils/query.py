import re


class BaseEntities:
    @staticmethod
    def countries():
        return "select rc.wyscout_id as id, rc.rankset_name as name from rankset.countries as rc " \
               "where rc.wyscout_id != 0 order by name asc;"

    @staticmethod
    def competitions(country_id: int):
        return f"select * from wyscout.competitions where country_id = {country_id};"

    @staticmethod
    def teams(competition_id: int):
        return f"select yt.competition_id, rt.rankset_id as id, rt.rankset_name as name from rankset.teams as rt, wyscout.teams as yt " \
               f"where rt.wyscout_id = yt.id and yt.competition_id = {competition_id};"

    @staticmethod
    def players(team_id: int):
        return "select distinct rt.rankset_id, rp.wyscout_id, rp.rankset_name from rankset.players as rp, rankset.teams as rt, wyscout.teams as wt " \
               f"where rt.rankset_id = rp.main_id and wt.id = rt.wyscout_id and rt.rankset_id = {team_id} and rp.wyscout_id != 0;"


class Players:
    @staticmethod
    def players_filter(object_id: int, data_type: int, argument: list = None):
        """  Returns all players by data type "
            - **current player team id **: 1
            - **country id **: 2
        """
        match data_type:
            case 1:
                return "select distinct rp.wyscout_id as id, rp.rankset_name as name, rp.rankset_id from rankset.players as rp, rankset.teams as rt, wyscout.teams as wt " \
                       f"where rt.rankset_id = rp.main_id and wt.id = rt.wyscout_id and rt.rankset_id = {object_id} and rp.wyscout_id != 0;"
            case 2:
                return f"select rp.wyscout_id as id, rp.rankset_name as name, rp.rankset_id from rankset.players as rp, rankset.teams as rt, " \
                       "wyscout.teams as wt, wyscout.competitions as wc where rt.rankset_id = rp.main_id and wt.id = rt.wyscout_id " \
                       f"and wc.id = wt.competition_id and wc.country_id = {object_id} and rp.wyscout_id != 0 "
            case 3 | 4:
                return "select distinct rp.wyscout_id as id, rp.rankset_name as name, rp.rankset_id from rankset.players as rp " \
                       f"where exists {get_internal_query(num=data_type, obj_id=object_id)} " \
                       "and exists (select * from rankset.position_metadata rpm " \
                       f"where rpm.player_id = rp.wyscout_id and rpm.position != 'n' and rpm.position in {str(get_argument(argument))}) " \
                       "group by rp.wyscout_id, rp.rankset_name;"

            case 5 | 6:
                val = argument[0]
                position = [argument[1]]
                return "select distinct rp.wyscout_id as id, rp.rankset_name as name, rp.rankset_id " \
                       f"{get_internal_query(num=data_type, obj_id=object_id, dt=data_type)} " \
                       f"and exists (select  * from rankset.player_metadata as rpm, rankset.position_metadata as rpm2 " \
                       "where rpm.player_id = rp.rankset_id " \
                       f"and rp.wyscout_id = rpm2.player_id and {get_metadata_field(val, data_type)} and rpm2.position in {str(get_argument(position))}) " \
                       "group by rp.wyscout_id, rp.rankset_name;"

            case 8:
                return f"select distinct similar_ids from rankset.similar_players as rsp where rsp.player_id = {object_id} limit 1;"

    @staticmethod
    def overview_base(player_id: int):
        return f"select player_name, age, place_of_birth, mv, mv_type, contract_expires, overview, achievements, transfer_history, injury_history, player_attributes, team_id " \
               f"from rankset.player_metadata as rpm " \
               f"where exists (select * from rankset.players as rp where rp.wyscout_id = {player_id} " \
               "and rpm.player_id = rp.rankset_id) limit 1;"

    @staticmethod
    def stats(player_id: int, required_stats: list):
        required_stat = str(required_stats).replace('[', '(').replace(']', ')')
        return "select distinct stat_name, " \
               "cast(sum(stat_value) / (select count(distinct event_id) from wyscout.player_stats " \
               f"where object_id = {player_id}) as decimal(10,2)) as stat_value " \
               f"from wyscout.player_stats where object_id = {player_id} " \
               f"and stat_name in {required_stat} group by stat_name order by stat_name asc;"

    @staticmethod
    def count_of_games(player_id: int):
        return f"select count(distinct event_id) from wyscout.player_stats where object_id = {player_id};"

    @staticmethod
    def position(player_id: int):
        return f"select position from rankset.position_metadata where player_id = {player_id} limit 1;"

    @staticmethod
    def search(content: str):
        return f"select distinct rp.wyscout_id as id, rp.rankset_name as name, rp.rankset_id from rankset.players as rp" \
               f" where rp.rankset_name like '%{content}%' order by rp.rankset_name asc limit 100;"

    @staticmethod
    def get_players_by_ids(players):
        return f"select distinct rp.wyscout_id as id, rp.rankset_name as name, rp.rankset_id from rankset.players as rp" \
               f" where rp.rankset_id in {tuple(players)} order by rp.rankset_name asc;"


class Ranking:
    @staticmethod
    def players():
        return "select rp.rankset_id, rp.rankset_name from rankset.players as rp, rankset.player_rank as rpr " \
               "where rpr.player_id = rp.rankset_id order by rp.rankset_id asc"

    @staticmethod
    def players_ranking(data_type: int, object_id: int = None):
        main_query = "select distinct rp.rankset_id, rp.rankset_name, rpr.position, rpr.tour_name, cast(rpr.player_rank as decimal (10,2)) as avg_rank, rpr.season, rpm.age, rpm.place_of_birth," \
                     "CASE WHEN rpm.mv_type = 'Th.' THEN rpm.mv * 1000 WHEN rpm.mv_type = 'm' THEN rpm.mv * 1000000 WHEN rpm.mv_type = 'bn' THEN rpm.mv * 1000000000 ELSE 0 END as market_value " \
                     "from rankset.players as rp, rankset.teams as rt, rankset.countries as rc, rankset.player_rank as rpr, rankset.player_metadata as rpm " \
                     "where rt.rankset_id = rp.main_id and rc.rankset_id = rt.main_id and rpr.player_id = rp.rankset_id and rpm.player_id = rpr.player_id and season like '%/%' and rpr.tour_name not like '%cup%'"
        end_query = " and rpr.player_rank group by rp.rankset_id, rp.rankset_name, rpr.tour_name, rpr.position, rpr.player_rank, rpr.season, rpm.age,rpm.place_of_birth, rpm.mv, rpm.mv_type order by avg_rank, season desc;"
        match data_type:
            case 1:
                return f"{main_query}{end_query}"

            case 2:
                return f"{main_query} and rc.wyscout_id = {object_id} {end_query}"

    @staticmethod
    def player_rank(player_id: int):
        return f"select distinct rp.rankset_id, rp.rankset_name, cast(rpr.player_rank as decimal (10, 2)) as avg_rank " \
               f"from rankset.players as rp, rankset.player_rank as rpr where rpr.player_id = {player_id} " \
               "and rpr.player_id = rp.rankset_id;"

    @staticmethod
    def player_rank_info(player_id: int):
        return f"select * from rankset.players as rp, rankset.player_rank as rpr where rpr.player_id = {player_id} " \
               "and rpr.player_id = rp.rankset_id order by rpr.season desc;"


def get_internal_query(num: int, obj_id: int, dt: int = None):
    cal = num % 2
    if cal != 0 and not dt:
        return "(select * from rankset.teams as rt, wyscout.teams as wt where rt.rankset_id = rp.main_id " \
               f"and wt.id = rt.wyscout_id and rt.rankset_id = {obj_id} and rp.wyscout_id != 0)"
    elif dt == 5 or dt == 6:
        return "from rankset.players as rp, rankset.teams as rt, wyscout.teams as wt, wyscout.competitions as wc " \
               "where rt.rankset_id = rp.main_id and wt.id = rt.wyscout_id and wc.id = wt.competition_id " \
               f"and wc.country_id = {obj_id} and rp.wyscout_id != 0"
    else:
        return "(select * from rankset.teams as rt, wyscout.teams as wt, wyscout.competitions as wc " \
               "where rt.rankset_id = rp.main_id and wt.id = rt.wyscout_id and wc.id = wt.competition_id " \
               f"and wc.country_id = {obj_id} and rp.wyscout_id != 0)"


def get_argument(arg):
    if len(arg) == 1:
        return f"('{arg[0]}')"
    else:
        return tuple(arg)


def get_metadata_field(val, dt: int):
    if dt == 5:
        val = int(val)
        min_age = val - 1
        max_age = val + 1
        return f'rpm.age in ({min_age}, {val}, {max_age})'
    elif dt == 6:
        mv = int(re.findall(r'\d+', val)[0])
        if 'Th.' in val:
            if mv + 25 <= 1000:
                values = val, f"{mv - 5}Th.", f"{mv - 10}Th.", f"{mv - 15}Th.", f"{mv - 20}Th.", f"{mv - 25}Th.", \
                         f"{mv + 5}Th.", f"{mv + 10}Th.", f"{mv + 15}Th.", f"{mv + 20}Th.", f"{mv + 25}Th."
                return f"CONCAT(rpm.mv, '', rpm.mv_type) in {str(values)}"
            else:
                return f"CONCAT(rpm.mv, '', rpm.mv_type) in ('{val}')"
        elif 'm' in val:
            sec_part = val.replace(str(mv), '')
            if mv <= 1:
                return f"CONCAT(rpm.mv, '', rpm.mv_type) in ('{val}')"
            else:
                if mv < 20:
                    mv_range = 1
                else:
                    mv_range = 2
                values = val, f"{mv - mv_range}{sec_part}", f"{mv - int(mv_range * 1.5)}{sec_part}", f"{mv - int(mv_range * 2)}{sec_part}", \
                         f"{mv + mv_range}{sec_part}", f"{mv + int(mv_range * 1.5)}{sec_part}", f"{mv + int(mv_range * 2)}{sec_part}",
                return f"CONCAT(rpm.mv, '', rpm.mv_type) in {str(values)}"
