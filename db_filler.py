import aiohttp

user_creation_url = "http://127.0.0.1:8000/auth/signup"
user_friendships_url = "http://127.0.0.1:8000/friends/add"
user_credentials_url = "http://127.0.0.1:8000/dashboard/credentials"

users_base = {
    "email": "test1@gmail.com",
    "username": "test1",
    "first_name": "Tester",
    "last_name": "1",
    "hashed_password": "master",
}

friendship_base = {
    "friendship_state": 1,
    "favorite_state": 0,
    "user_1_id": 1,
    "user_2_id": 2
}

credential_base = {
    "nickname": "testCredential1",
    "email": "test@gmail.com",
    "username": "testUsername",
    "password": "testPassword",
    "user_id": 0,
    "site_id": 0
}


def users_generator():
    user = users_base
    for i in range(5):
        yield user
        user["email"] = f'test{int(user["email"].split("test")[1].split("@")[0]) + 1}@gmail.com'
        user["username"] = f'test{int(user["username"].split("test")[1]) + 1}'
        user["last_name"] = f'{int(user["last_name"]) + 1}'


def users_friendship_generator():
    friendship = friendship_base
    for i in range(3):
        yield friendship
        friendship["user_1_id"] = int(friendship["user_1_id"])
        friendship["user_2_id"] = int(friendship["user_2_id"]) + 1

    yield friendship

    friendship["user_1_id"] = 3
    friendship["user_2_id"] = 4
    yield friendship


def users_credentials_generator():
    credential = credential_base
    for i in range(8):
        yield credential
        credential["nickname"] = f'testCredential{int(credential["nickname"].split("Credential")[1]) + 1}'

    yield credential


async def main():
    async with aiohttp.ClientSession() as session:
        for user in users_generator():
            async with session.post(user_creation_url, json=user) as resp:
                user_response = await resp.json()
                print(user_response)

        for friendship in users_friendship_generator():
            async with session.post(user_friendships_url, json=friendship) as resp:
                friendship_response = await resp.json()
                print(friendship_response)

        for credential in users_credentials_generator():
            async with session.post(user_credentials_url, json=credential) as resp:
                credential_response = await resp.json()
                print(credential_response)

        return
