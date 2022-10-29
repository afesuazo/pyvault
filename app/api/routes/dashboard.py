from typing import Optional, List

from fastapi import APIRouter, status, Depends

from app.crud.credential import CredentialCRUD
from app.crud.site import SiteCRUD
from app.models.credential import Credential, CredentialCreate
from app.models.site import Site, SiteCreate

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


@router.post(
    "/sites",
    response_model=Site,
    status_code=status.HTTP_201_CREATED
)
async def create_order(
        site_data: SiteCreate, sites: SiteCRUD = Depends(SiteCRUD)
) -> Site:
    site = await sites.create(site_data=site_data)
    return site


@router.post(
    "/credentials",
    response_model=Credential,
    status_code=status.HTTP_201_CREATED
)
async def create_order(
        credential_data: CredentialCreate, sites: CredentialCRUD = Depends(CredentialCRUD)
) -> Credential:
    credential = await sites.create(credential_data=credential_data)
    return credential


@router.get(
    "/credentials/{credential_id}",
    response_model=Optional[Credential],
    status_code=status.HTTP_200_OK,
)
async def read_credential_by_id(
        credential_id: int, credentials: CredentialCRUD = Depends(CredentialCRUD)
) -> Optional[Site]:
    credential = await credentials.read(unique_id=credential_id)
    return credential
