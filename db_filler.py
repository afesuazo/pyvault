import asyncio

import aiohttp

log_in_url = "http://127.0.0.1:4557/auth/login"
user_creation_url = "http://127.0.0.1:4557/auth/signup"
user_friendships_url = "http://127.0.0.1:4557/friends/add"
user_credentials_url = "http://127.0.0.1:4557/dashboard/credentials"
user_sites_url = "http://127.0.0.1:4557/dashboard/sites"

users_base = {
    "email": "test1@gmail.com",
    "username": "test1",
    "first_name": "Tester",
    "last_name": "1",
    "password": "master",
}

friendship_base = {
    "favorite_state": 0,
    "user_1_id": 1,
    "user_2_id": 2
}

credential_base = {
    "nickname": "testCredential1",
    "email": "test@gmail.com",
    "username": "testUsername",
    "password": "testPassword",
    "user_id": 1,
    "site_id": 1
}

site_base = {
    "name": "Site1",
    "url": "https://Site1.com",
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
        credential["site_id"] = (int(credential["site_id"]) % 3 ) + 1

    yield credential


def users_sites_generator():
    site = site_base
    for i in range(2):
        yield site
        site["name"] = f'Site{int(site["name"].split("Site")[1]) + 1}'
        site["url"] = f'https://Site{int(site["name"].split("Site")[1]) + 1}.com'

    yield site


async def add_base_data():
    async with aiohttp.ClientSession() as session:

        for user in users_generator():
            async with session.post(user_creation_url, json=user) as resp:
                user_response = await resp.json()
                print(user_response)

        token = ''

        async with session.post(log_in_url, data={"username": "test1", "password": "master"}) as resp:
            user_response = await resp.json()
            print(user_response)
            token = user_response["access_token"]

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f"Bearer {token}",
        }

        for site in users_sites_generator():
            async with session.post(user_sites_url, json=site,
                                    headers=headers) as resp:
                site_response = await resp.json()
                print(site_response)

        for credential in users_credentials_generator():
            async with session.post(user_credentials_url, json=credential,
                                    headers=headers) as resp:
                credential_response = await resp.json()
                print(credential_response)

        return


async def add_friends():
    async with aiohttp.ClientSession() as session:
        for friendship in users_friendship_generator():
            async with session.post(user_friendships_url, json=friendship,
                                    auth=aiohttp.BasicAuth("test1", "master")) as resp:
                friendship_response = await resp.json()
                print(friendship_response)

        return


def main():
    asyncio.run(add_base_data())
    # asyncio.run(add_friends())


if __name__ == "__main__":
    main()
