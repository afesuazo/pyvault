import logging
from typing import Optional, List

from aioredis import Redis
from config import ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi import APIRouter, HTTPException, status, Depends, Query, Response

from app.core.cypt_utils import encrypt_with_key, decrypt_with_key
from app.crud.credential import CredentialCRUD
from app.crud.site import SiteCRUD
from app.dependencies.auth import get_current_user
from app.dependencies.redis import get_redis
from app.models.site import SiteCreate, SiteRead, Site, SiteSimpleRead
from app.models.credential import Credential, CredentialCreate, CredentialRead, CredentialUpdate

router = APIRouter()

logger = logging.getLogger("pyvault.api.dashboard")
logging.basicConfig(level=logging.DEBUG)


@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"ping": "pong!"}


# ----------------- Sites -----------------


@router.post(
    "/sites",
    summary="Create a new site",
    response_model=SiteRead,
    status_code=status.HTTP_201_CREATED
)
async def create_site(
        site_data: SiteCreate, site_crud: SiteCRUD = Depends(SiteCRUD)
) -> Site:
    site = await site_crud.read_by_name(site_data.name)
    if site:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Site with this name already exist"
        )
    site = await site_crud.create(site_data=site_data)
    return site


@router.get(
    "/sites",
    summary="Get a list of all available sites",
    response_model=List[SiteRead],
    status_code=status.HTTP_200_OK,
)
async def read_sites(
        offset: int = 0,
        limit: int = Query(default=50, lte=50),
        site_crud: SiteCRUD = Depends(SiteCRUD),
) -> List[Site]:
    if limit < 0 or offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Offset and limit must be positive numbers",
        )
    sites = await site_crud.read_many(offset=offset, limit=limit)
    return sites


@router.get(
    "/sites/reduced",
    summary="Get a list of all available sites, id and name only",
    response_model=List[SiteSimpleRead],
    status_code=status.HTTP_200_OK,
)
async def read_sites(
        offset: int = 0,
        limit: int = Query(default=50, lte=50),
        site_crud: SiteCRUD = Depends(SiteCRUD),
) -> List[Site]:
    if limit < 0 or offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Offset and limit must be positive numbers",
        )
    sites = await site_crud.read_many(offset=offset, limit=limit)
    return sites


@router.get(
    "/sites/{site_id}",
    summary="Get a site by id",
    response_model=Optional[SiteRead],
    status_code=status.HTTP_200_OK,
)
async def read_site_by_id(
        site_id: int, sites: SiteCRUD = Depends(SiteCRUD)
) -> Optional[Site]:
    site = await sites.read(unique_id=site_id)
    return site


# ----------------- Credentials -----------------

@router.post(
    "/credentials",
    summary="Create a new credential",
    response_model=CredentialRead,
    status_code=status.HTTP_201_CREATED
)
async def create_credential(
        credential_data: CredentialCreate,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        user=Depends(get_current_user),
) -> Credential:
    # Overwrite the user_id with the current authenticated user id
    credential_data.user_id = user.id

    # Encrypt incoming password with user's key
    encryption_key = user.public_key
    plaintext_password = credential_data.encrypted_password
    credential_data.encrypted_password = encrypt_with_key(encryption_key, credential_data.encrypted_password)
    credential = await credential_crud.create(credential_data=credential_data)
    credential.encrypted_password = plaintext_password

    return credential


@router.get(
    "/credentials/{credential_id}",
    summary="Get a credential by id",
    response_model=Optional[CredentialRead],
    status_code=status.HTTP_200_OK,
)
async def read_credential_by_id(
        credential_id: int,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        user=Depends(get_current_user)
) -> Optional[Credential]:
    credential = await credential_crud.read_personal(unique_id=credential_id, user_id=user.id)
    if not credential:
        raise HTTPException(status_code=404, detail="Item not found")

    decryption_key = user.private_key
    credential.encrypted_password = decrypt_with_key(decryption_key, credential.encrypted_password)
    return credential


@router.get(
    "/credentials",
    summary="Get a list of credentials for the current user",
    response_model=List[CredentialRead],
    status_code=status.HTTP_200_OK,
)
async def read_credentials(
        offset: int = 0,
        limit: int = Query(default=10, lte=50),
        site_id: Optional[int] = None,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        user=Depends(get_current_user)
) -> list[Credential]:
    if limit < 0 or offset < 0:
        raise HTTPException(
            status_code=400,
            detail="Offset and limit must be positive numbers",
        )
    credentials = await credential_crud.read_personal_many(offset=offset, limit=limit, site_id=site_id,
                                                           user_id=user.id)

    # Decrypt incoming password with user's key
    decryption_key = user.private_key
    for credential in credentials:
        credential.encrypted_password = decrypt_with_key(decryption_key, credential.encrypted_password)

    return credentials


@router.delete(
    "/credentials/{credential_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_credential_by_id(
        credential_id: int,
        response: Response,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        user=Depends(get_current_user),
) -> None:
    credential = await credential_crud.read_personal(credential_id, user.id)
    if credential:
        await credential_crud.delete(unique_id=credential_id)
        return

    response.status_code = status.HTTP_404_NOT_FOUND


@router.put(
    "/credentials/{credential_id}",
    summary="Update a credential",
    response_model=CredentialRead,
    status_code=status.HTTP_200_OK,
)
async def update_credential_by_id(
        credential_id: int,
        credential_data: CredentialUpdate,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        site_crud: SiteCRUD = Depends(SiteCRUD),
        user=Depends(get_current_user),
) -> Credential:
    credential = await credential_crud.read_personal(credential_id, user.id)
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")

    # If password is provided, encrypt it with user's key
    if credential_data.encrypted_password:
        encryption_key = user.public_key
        credential_data.encrypted_password = encrypt_with_key(encryption_key, credential_data.encrypted_password)

    # If values are empty strings, set them to the current values
    credential_data = credential_data.dict()
    for key, value in credential_data.items():
        if value is None:
            if key == "site_id":
                credential_data[key] = None
            continue
        elif value == "" and key not in ["favorite"]:
            credential_data[key] = getattr(credential, key)
        elif key == "site_id":
            site = await site_crud.read(credential_data[key])
            if not site:
                raise HTTPException(status_code=404, detail="Site not found")
            credential_data[key] = site.id

    credential_data = CredentialUpdate(**credential_data)

    # Update the credential data to match the incoming data
    try:
        updated_credential = await credential_crud.update(credential_id, credential_data)
    except AssertionError as e:
        raise HTTPException(status_code=404, detail=str(e))

    updated_credential.encrypted_password = decrypt_with_key(user.private_key, updated_credential.encrypted_password)
    return updated_credential
