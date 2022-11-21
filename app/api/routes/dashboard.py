from typing import Optional, List

from fastapi import APIRouter, status, Depends, Query

from app.crud.credential import CredentialCRUD
from app.crud.site import SiteCRUD
from app.models.credential import Credential, CredentialCreate
from app.models.site import Site, SiteCreate

router = APIRouter()


@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"ping": "pong!"}


@router.post(
    "/sites",
    response_model=Site,
    status_code=status.HTTP_201_CREATED
)
async def create_site(
        site_data: SiteCreate, site_crud: SiteCRUD = Depends(SiteCRUD)
) -> Site:
    site = await site_crud.create(site_data=site_data)
    return site


@router.get(
    "/sites/",
    response_model=List[Site],
    status_code=status.HTTP_200_OK,
)
async def read_sites(
        offset: int = 0,
        limit: int = Query(default=50, lte=50),
        site_crud: SiteCRUD = Depends(SiteCRUD),
) -> List[Site]:
    sites = await site_crud.read_many(offset=offset, limit=limit)
    return sites


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
    "/credentials",
    response_model=Credential,
    status_code=status.HTTP_201_CREATED
)
async def create_credential(
        credential_data: CredentialCreate, credential_crud: CredentialCRUD = Depends(CredentialCRUD)
) -> Credential:
    credential = await credential_crud.create(credential_data=credential_data)
    return credential


@router.get(
    "/credentials/{credential_id}",
    response_model=Optional[Credential],
    status_code=status.HTTP_200_OK,
)
async def read_credential_by_id(
        credential_id: int, credential_crud: CredentialCRUD = Depends(CredentialCRUD)
) -> Optional[Credential]:
    credential = await credential_crud.read(unique_id=credential_id)
    return credential


@router.get(
    "/credentials/",
    response_model=List[Credential],
    status_code=status.HTTP_200_OK,
)
async def read_credentials(
        offset: int = 0,
        limit: int = Query(default=10, lte=50),
        site_id: Optional[int] = None,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
) -> List[Credential]:
    credentials = await credential_crud.read_many(offset=offset, limit=limit, group_id=site_id)
    return credentials


@router.delete(
    "/credentials/{credential_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_credential_by_id(
        credential_id: int,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
) -> None:
    print(credential_id)
    await credential_crud.delete(unique_id=credential_id)