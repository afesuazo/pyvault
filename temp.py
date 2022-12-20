@router.get(
    "/credentials/share",
    response_model=List[Credential],
    status_code=status.HTTP_200_OK,
)
async def read_shared_credentials(
        offset: int = 0,
        limit: int = Query(default=10, lte=50),
        friend_id: Optional[int] = None,
        owned: Optional[bool] = False,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        shared_credential_crud: SharedCredentialCRUD = Depends(SharedCredentialCRUD),
        user=Depends(get_current_user)
) -> List[Credential]:
    shared_credentials = await shared_credential_crud.read_personal_many(offset, limit, user_id=user.uid,
                                                                         friend_id=friend_id, owner=owned,
                                                                         credential_id=None)
    credentials = []
    if shared_credentials:
        credential_ids = [credential.credential_id for credential in shared_credentials]
        print(credential_ids)
        # TODO: Check for empty results
        credentials = [await credential_crud.read(int(credential)) for credential in credential_ids]
    return credentials


@router.get(
    "/credentials/share/{credential_id}",
    response_model=List[UserBase],
    status_code=status.HTTP_200_OK,
)
async def read_shared_credentials(
        credential_id: int,
        credential_crud: CredentialCRUD = Depends(CredentialCRUD),
        shared_credential_crud: SharedCredentialCRUD = Depends(SharedCredentialCRUD),
        user=Depends(get_current_user)
) -> List[Credential]:
    shared_credentials = await shared_credential_crud.read_personal_many(0, 200, user.uid, friend_id=None, owner=True,
                                                                         credential_id=credential_id)
    credentials = []
    if shared_credentials:
        credential_ids = [credential.credential_id for credential in shared_credentials]
        credentials = [await credential_crud.read(int(credential)) for credential in credential_ids]
    return credentials