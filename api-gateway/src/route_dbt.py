from fastapi import APIRouter, HTTPException

import os
import httpx

dbt_router = APIRouter()

# ================================================
# Environment
# ================================================
URL_APIDBT = os.environ["URL_APIDBT"]

@dbt_router.get("/run-status", include_in_schema=False)
async def get_status():
    """
    Calls api-dbt/run_status and return the status.json from it
    """
    try:
        async with httpx.AsyncClient(timeout=60) as client_apidbt:
            status = await client_apidbt.get(f'{URL_APIDBT}/run-status')
            status.raise_for_status() 
    # Il faut pouvoir relayer un code 409 (en case de conflit de run en cours dans api-dbt)
    # Et remonter au client le code 409 pour qu'il sache qu'un run est déjà en cours
    # sinon, si on ne relaie pas le 409, alors le client reçoit un 502 : gateway est en erreur à cause d'un 409 de api-dbt, ce qui est trompeur
    except httpx.HTTPStatusError as error_apidbt:
        if error_apidbt.response.status_code == 409:
            raise HTTPException(status_code=409, detail="run en cours")
        else:
            raise HTTPException(status_code=502, detail=f"api-dbt en erreur : {error_apidbt}")
    except httpx.HTTPError as error_apidbt:
        raise HTTPException(status_code=502, detail=f"api-dbt injoignable ou en erreur : {error_apidbt}")
    return status.json()


@dbt_router.post("/run", include_in_schema=False)
async def post_dbt_run():
    """
    Calls api-dbt/run and return the status.json from it
    """
    try:
        async with httpx.AsyncClient(timeout=60) as client_apidbt:
            status = await client_apidbt.post(f'{URL_APIDBT}/run')
            status.raise_for_status()
    # Il faut pouvoir relayer un code 409 (en case de conflit de run en cours dans api-dbt)
    # Et remonter au client le code 409 pour qu'il sache qu'un run est déjà en cours
    # sinon, si on ne relaie pas le 409, alors le client reçoit un 502 : gateway est en erreur à cause d'un 409 de api-dbt, ce qui est trompeur
    except httpx.HTTPStatusError as error_apidbt:
        if error_apidbt.response.status_code == 409:
            raise HTTPException(status_code=409, detail="run en cours")
        else:
            raise HTTPException(status_code=502, detail=f"api-dbt en erreur : {error_apidbt}")
    except httpx.HTTPError as error_apidbt:
        raise HTTPException(status_code=502, detail=f"api-dbt injoignable ou en erreur : {error_apidbt}")
    return status.json()