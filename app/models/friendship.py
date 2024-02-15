from typing import Optional

from sqlmodel import Field, SQLModel

# Data only model


class FriendshipBase(SQLModel):
    friendship_state: int = Field(default=0)

    user_1_id: int = Field(foreign_key="user.id")
    user_2_id: int = Field(foreign_key="user.id")


class Friendship(FriendshipBase, table=True):
    __tablename__ = "friendship"

    uid: Optional[int] = Field(default=None, primary_key=True, index=True)


# Created to differentiate from Base in docs

class FriendshipCreate(FriendshipBase):
    pass


class FriendshipUpdate(FriendshipBase):
    pass
