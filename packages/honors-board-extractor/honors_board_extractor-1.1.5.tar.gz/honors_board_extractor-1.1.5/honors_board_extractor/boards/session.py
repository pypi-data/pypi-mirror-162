from typing import Dict, Optional
from aiohttp import ClientSession
from yarl import URL


async def create_session(url: URL, user: Dict[str, str]) -> ClientSession:
    """
    This creates an aiohttp.ClientSession with an access token for url and user embedded.
    """
    async with ClientSession() as sess:
        token = await get_access_token(sess, url, user)

    headers = {'Authorization': token}
    return ClientSession(headers=headers)


async def get_access_token(session: ClientSession, url: URL, user: Dict[str, str]) -> Optional[str]:
    """
    Datastore is login protected by a jwt. This extracts the jwt for a given user. This function
    will create the login url from the base datastore url.

    :param session:
    :param url: The base datastore url.
    :param user: The user should be an admin.
    :raises: Can raise if the post fails. Will pass that error up.
    :return: jwt
    """
    login_url = url / 'login'
    async with session.post(login_url, json=user) as resp:
        json_resp = await resp.json()
        if json_resp.get('status') == 'ok':
            data = json_resp.get('data')
            token = data.get('token') if type(data) is dict else None
            return token
