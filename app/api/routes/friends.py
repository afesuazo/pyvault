from typing import List, Optional

from fastapi import APIRouter, Depends

from app.crud.friendship import FriendshipCRUD
from app.crud.user import UserCRUD
from app.dependencies.auth import get_current_user
from app.models.friendship import Friendship, FriendshipCreate
from app.models.user import UserBase

router = APIRouter()


@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"ping": "pong!"}


@router.get("/all")
async def get_friends(friendship_crud: FriendshipCRUD = Depends(FriendshipCRUD),
                      user_crud: UserCRUD = Depends(UserCRUD), user = Depends(get_current_user)) -> List[UserBase]:
    friendships = await friendship_crud.read_many(0, 500, group_id=user.id)
    friends = [friendship.user_1_id if friendship.user_1_id != user.id else friendship.user_2_id for friendship in
               friendships]
    users = [await user_crud.read(int(friend)) for friend in friends]
    return users


@router.post("/add")
async def add_friend(
        friendship_data: FriendshipCreate,
        friendship_crud: FriendshipCRUD = Depends(FriendshipCRUD),
        user_crud: UserCRUD = Depends(UserCRUD),
        user = Depends(get_current_user)
) -> Optional[Friendship]:
    # Check if friendship exists already
    friendship = await friendship_crud.read_friend_pair(user.id, friendship_data.user_2_id)
    if friendship:
        return friendship

    friend_user = await user_crud.read(friendship_data.user_2_id)
    if friend_user is None:
        return

    if user.id < friendship_data.user_2_id:
        friendship_data.friendship_state = 1
    else:
        friendship_data.friendship_state = 2

    friendship = await friendship_crud.create(friendship_data=friendship_data)
    return friendship


@router.post("/remove")
async def remove_friend(friend_id: int, friendship_crud: FriendshipCRUD = Depends(FriendshipCRUD), user = Depends(get_current_user)) -> None:
    friendship = await friendship_crud.read_friend_pair(user.id, friend_id)
    await friendship_crud.delete(friendship.uid)