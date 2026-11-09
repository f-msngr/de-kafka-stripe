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
    except httpx.HTTPError as error_apidbt:
        raise HTTPException(status_code=502, detail=f"api-dbt injoignable ou en erreur : {error_apidbt}")
    return status.json()