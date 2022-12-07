from typing import List

from fastapi import APIRouter, Depends

from app.crud.friendship import FriendshipCRUD
from app.crud.user import UserCRUD
from app.models.friendship import Friendship, FriendshipCreate
from app.models.user import UserBase

router = APIRouter()


@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"ping": "pong!"}


@router.get("/all")
async def get_friends(user_id: int, friendship_crud: FriendshipCRUD = Depends(FriendshipCRUD), user_crud: UserCRUD = Depends(UserCRUD)) -> List[UserBase]:
    friendships = await friendship_crud.read_many(0, 100, group_id=user_id)
    friends = [friendship.user_1_id if friendship.user_1_id != user_id else friendship.user_2_id for friendship in friendships]
    users = [await user_crud.read(int(friend)) for friend in friends]
    return users


@router.post("/add")
async def add_friend(
        friendship_data: FriendshipCreate, friendship_crud: FriendshipCRUD = Depends(FriendshipCRUD)
) -> Friendship:
    friendship = await friendship_crud.create(friendship_data=friendship_data)
    return friendship


@router.post("/remove")
async def remove_friend(friendship_id: int, friendship_crud: FriendshipCRUD = Depends(FriendshipCRUD)) -> None:
    await friendship_crud.delete(friendship_id)


