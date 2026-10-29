from fastapi import Request

def get_clickhouse_client(request: Request):
    """ Retourne le client ClickHouse stocké dans app.state.clickhouse. """
    return request.app.state.clickhouse
