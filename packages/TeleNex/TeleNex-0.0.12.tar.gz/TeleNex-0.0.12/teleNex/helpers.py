from typing import List, Optional

from .types import TeleObj

import aiohttp


def list_payload(arr):
    res = []
    for v in arr:
        if isinstance(v, TeleObj):
            res.append(v.dict())
        elif type(v) is list:
            res.append(list_payload(v))
        elif v is not None:
            res.append(v)
    return res


def generate_payload(args: dict):
    args.pop('self', None)
    args.pop('__class__', None)
    data = {}
    for k, v in args.items():
        if isinstance(v, TeleObj):
            data[k] = v.dict()
        elif type(v) is list:
            data[k] = list_payload(v)
        elif v is not None:
            data[k] = v

    return data


class ApiHelper:
    def __init__(self, token):
        self.token = token

        self._session: aiohttp.ClientSession = None

        self.request_config = { 'ssl': False }

    @property
    def session(self):
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def make_request(self, method: str, data: dict = None) -> Optional[dict]:
        url = f'https://api.telegram.org/bot{self.token}/{method}'
        async with self.session.post(url, json=data, **self.request_config) as resp:
            return await resp.json()

    async def download_file(self, file_path: str, save_path: str=None):
        async with self.session.get(f'https://api.telegram.org/file/bot{self.token}/{file_path}', **self.request_config) as resp:
            if save_path:
                with open(save_path, 'wb') as file:
                    data = await resp.content.read()
                    file.write(data)
            else:
                return await resp.content.read()

    async def get_updates(
            self,
            offset: Optional[int]=None, 
            limit: Optional[int]=None, 
            timeout: Optional[int]=None,
            allowed_updates: Optional[List[str]] = None
        ) -> Optional[dict]:
        data = generate_payload(locals().copy())

        return await self.make_request('getUpdates', data=data)