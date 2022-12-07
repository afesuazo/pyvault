from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
async def ping() -> dict[str, str]:
    return {"ping": "pong!"}


@router.get("/all")
async def get_friends() -> None:
    pass


@router.get("/add")
async def add_friend() -> None:
    pass


@router.get("/remove")
async def remove_friend() -> None:
    pass
