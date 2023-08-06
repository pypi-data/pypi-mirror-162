from fastapi import APIRouter
from api_utils import Routs, Keys, base_model
from api_utils.query import Ranking


class RankingModel(base_model.BaseModel):
    """
    Initiate entities model
    """
    pass


router_ranking = APIRouter(
    prefix=f"/{Routs.RANKING}",
    tags=[Routs.RANKING])


@router_ranking.get(path="/players", summary="Returns all existing players in the DB")
async def players():
    """
        Returns all existing players in the DB"
    """
    return {Keys.DATA_TYPE: Keys.RANK,
            Keys.DATA:
                RankingModel.Meta.database.get_data(
                    query=Ranking.players())[0],
            Keys.STATUS_CODE: 200}


@router_ranking.get(path="/players_ranking/{data_type}/{object_id}",
                    summary="Returns rating rank for existing players in the DB")
async def players_ranking(data_type: int = 1, object_id: int = 0):
    """
        Returns rating rank for existing players in the DB"
        - **data_type**: filter option.
        data_type options:
            - all: 1
            - country id: 2
            - age: 4
            - mv: 5
    """
    data = RankingModel.Meta.database.get_data(
        query=Ranking.players_ranking(data_type=data_type, object_id=object_id))
    return {Keys.DATA_TYPE: Keys.RANK,
            Keys.DATA: data[0],
            Keys.COLUMNS: data[1],
            Keys.STATUS_CODE: 200}


@router_ranking.get(path="/player/{player_id}", summary="Returns player rank by player id")
async def player_rank_info(player_id: int):
    """
        Returns player rank by player id"
        - **player_id**: The player_id unique id.
    """
    data = RankingModel.Meta.database.get_data(
        query=Ranking.player_rank_info(player_id=player_id))
    pl_data = RankingModel.Meta.database.get_data(
        query=Ranking.player_rank(player_id=player_id))
    return {Keys.DATA_TYPE: Keys.RANK,
            Keys.DATA: data[0],
            Keys.COLUMNS: data[1],
            Keys.PLAYER_RANK: pl_data[0],
            Keys.STATUS_CODE: 200}
