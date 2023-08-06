from api_utils.constants import Keys


def get_position(conn, query):
    data = conn.get_data(query=query)[0]
    if data:
        return data[0][0].replace("[", '').replace("]", '').replace("'", '')
    return 'Not found data.'


def get_mv_data(data):
    age = '-'
    contract_expires = '-'
    mv = '-'
    nation = '-'
    try:
        if data.age.values[0]:
            age = int(data.age.values[0])
        if data.contract_expires.values[0]:
            contract_expires = data.contract_expires.values[0]
        if data.mv.values[0]:
            mv = int(data.mv.values[0])
        if data.mv_type.values[0]:
            mv = f"{mv}{data.mv_type.values[0]}"
        if data.place_of_birth.values[0]:
            nation = data.place_of_birth.values[0]

    except Exception as e:
        e
    return {Keys.AGE: age, Keys.CONTRACT_EXPIRES: contract_expires,
            Keys.MARKET_VALUE: mv, Keys.NATION: nation}
