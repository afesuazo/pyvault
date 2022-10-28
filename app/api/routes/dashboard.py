from typing import Optional, List

from fastapi import APIRouter, status, Depends

from app.crud.credential import CredentialCRUD
from app.crud.site import SiteCRUD
from app.models.credential import Credential
from app.models.site import Site

router = APIRouter()


@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"ping": "pong!"}


@router.get(
    "/sites/{site_id}",
    response_model=Optional[Site],
    status_code=status.HTTP_200_OK,
)
async def read_site_by_id(
        site_id: int, sites: SiteCRUD = Depends(SiteCRUD)
) -> Optional[Site]:
    site = await sites.read(unique_id=site_id)
    return site


@router.get(
    "/credentials/{credential_id}",
    response_model=Optional[Credential],
    status_code=status.HTTP_200_OK,
)
async def read_site_by_id(
        credential_id: int, credentials: CredentialCRUD = Depends(CredentialCRUD)
) -> Optional[Site]:
    credential = await credentials.read(unique_id=credential_id)
    return credential
