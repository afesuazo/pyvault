from typing import Optional, List

from aioredis import Redis
from fastapi import APIRouter, status, Depends, Query

import db_filler
from app.api.cypt_utils import decrypt, encrypt
from app.crud.credential import CredentialCRUD
from app.crud.friendship import FriendshipCRUD
from app.crud.shared_credential import SharedCredentialCRUD
from app.crud.site import SiteCRUD
from app.crud.user import UserCRUD
from app.dependencies.auth import get_current_user
from app.dependencies.redis import get_redis
from app.models.user import UserBase, User
from app.models.site import SiteCreate, SiteRead, Site, SiteSimpleRead
from app.models.credential import CredentialCreate, SharedCredential, SharedCredentialCreate, CredentialRead, Credential

router = APIRouter()


@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"ping": "pong!"}


@router.post(
    "/sites",
    response_model=SiteRead,
    status_code=status.HTTP_201_CREATED
)
async def create_site(
        site_data: SiteCreate, site_crud: SiteCRUD = Depends(SiteCRUD)
) -> Site:
    site = await site_crud.create(site_data=site_data)
    return site


@router.get(
    "/sites",
    response_model=List[SiteRead],
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
    "/sites/list",
    response_model=List[SiteSimpleRead],
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
    response_model=Optional[SiteRead],
    status_code=status.HTTP_200_OK,
)
async def read_site_by_id(
        site_id: int, sites: SiteCRUD = Depends(SiteCRUD)
) -> Optional[Site]:
    site = await sites.read(unique_id=site_id)
    return site


@router.post(
    "/credentials",
    response_model=CredentialRead,
    status_code=status.HTTP_201_CREATED
)
async def create_credential(
        credential_data: CredentialCreate,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        user=Depends(get_current_user),
        redis: Redis = Depends(get_redis)
) -> Credential:
    credential_data.user_id = user.id
    crypt_key = await redis.get(str(user.id))
    plain_pwd = credential_data.password
    credential_data.password = encrypt(crypt_key, credential_data.password).hex()
    credential = await credential_crud.create(credential_data=credential_data)

    credential.password = plain_pwd

    return credential


@router.get(
    "/credentials/shared",
    response_model=List[CredentialRead],
    status_code=status.HTTP_200_OK,
)
async def read_shared_credentials(
        offset: int = 0,
        limit: int = Query(default=10, lte=50),
        friend_id: Optional[int] = None,
        owned: Optional[bool] = False,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        shared_credential_crud: SharedCredentialCRUD = Depends(SharedCredentialCRUD),
        user=Depends(get_current_user),
        redis: Redis = Depends(get_redis)
) -> List[Credential]:
    shared_credentials = await shared_credential_crud.read_personal_many(offset, limit, user_id=user.id,
                                                                         friend_id=friend_id, owner=owned,
                                                                         credential_id=None)
    credentials = []
    if shared_credentials:
        credential_ids = [credential.credential_id for credential in shared_credentials]
        # TODO: Check for empty results
        credentials = [await credential_crud.read(int(credential)) for credential in credential_ids]

    crypt_key = await redis.get(str(user.id))
    for cred in credentials:
        cred.password = decrypt(crypt_key, cred.password)

    return credentials


@router.get(
    "/credentials/shared/{credential_id}/users",
    response_model=List[UserBase],
    status_code=status.HTTP_200_OK,
)
async def read_shared_credentials_users(
        credential_id: int,
        user_crud: UserCRUD = Depends(UserCRUD),
        shared_credential_crud: SharedCredentialCRUD = Depends(SharedCredentialCRUD),
        user=Depends(get_current_user)
) -> List[User]:
    shared_credentials = await shared_credential_crud.read_personal_many(0, 200, user.id, friend_id=None, owner=True,
                                                                         credential_id=credential_id)
    users = []
    if shared_credentials:
        user_ids = [credential.guest_id for credential in shared_credentials]
        users = [await user_crud.read(int(user_id)) for user_id in user_ids]
    return users


@router.get(
    "/credentials/{credential_id}",
    response_model=Optional[CredentialRead],
    status_code=status.HTTP_200_OK,
)
async def read_credential_by_id(
        credential_id: int,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        user=Depends(get_current_user),
        redis: Redis = Depends(get_redis)
) -> Optional[Credential]:
    credential = await credential_crud.read_personal(unique_id=credential_id, user_id=user.id)
    crypt_key = await redis.get(str(user.id))
    credential.password = decrypt(crypt_key, credential.password)
    return credential


@router.get(
    "/credentials",
    response_model=List[CredentialRead],
    status_code=status.HTTP_200_OK,
)
async def read_credentials(
        offset: int = 0,
        limit: int = Query(default=10, lte=50),
        site_id: Optional[int] = None,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        user=Depends(get_current_user),
        redis: Redis = Depends(get_redis)
) -> list[Credential]:
    credentials = await credential_crud.read_personal_many(offset=offset, limit=limit, site_id=site_id,
                                                           user_id=user.id)
    crypt_key = await redis.get(str(user.id))

    for cred in credentials:
        cred.password = decrypt(crypt_key, cred.password)

    return credentials


@router.delete(
    "/credentials/{credential_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_credential_by_id(
        credential_id: int,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        user=Depends(get_current_user)
) -> None:
    credential = await credential_crud.read_personal(credential_id, user.id)
    if credential:
        await credential_crud.delete(unique_id=credential_id)
    else:
        return status.HTTP_404_NOT_FOUND


@router.patch(
    "/credentials/shared/{credential_id}",
    status_code=status.HTTP_200_OK,
    response_model=Optional[SharedCredential]
)
async def share_credential_by_id(
        credential_id: int,
        friend_id: int,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        shared_credential_crud: SharedCredentialCRUD = Depends(SharedCredentialCRUD),
        friend_crud: FriendshipCRUD = Depends(FriendshipCRUD),
        user=Depends(get_current_user)
) -> Optional[SharedCredential]:
    credential = await credential_crud.read_personal(credential_id, user.id)
    if credential:
        # TODO: Better response object to eliminate nesting
        # Check if friend exists
        friendship = await friend_crud.read_friend_pair(user.id, int(friend_id))
        if friendship is None:
            return
        # Check if already shared with friend
        shared_credential = await shared_credential_crud.read_pair_personal(user.id, friend_id, credential_id)
        if not shared_credential:
            shared_credential = SharedCredentialCreate(credential_id=credential_id, owner_id=user.id,
                                                       guest_id=friend_id)
            return await shared_credential_crud.create(shared_credential)

        return shared_credential


@router.delete(
    "/credentials/shared/{shared_credential_id}",
    status_code=status.HTTP_200_OK,
)
async def delete_credential_by_id(
        shared_credential_id: int,
        shared_credential_crud: SharedCredentialCRUD = Depends(SharedCredentialCRUD),
        user=Depends(get_current_user)
) -> None:
    shared_credential = await shared_credential_crud.read_personal(shared_credential_id, user.id)
    if shared_credential:
        await shared_credential_crud.delete(unique_id=shared_credential_id)
    else:
        return status.HTTP_404_NOT_FOUND


@router.get("/debug_setup")
async def debug_setup() -> None:
    await db_filler.add_base_data()


@router.get("/debug_setup_friends")
async def debug_setup() -> None:
    await db_filler.add_friends()
