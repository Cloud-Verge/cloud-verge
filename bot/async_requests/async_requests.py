import aiohttp
import os


async def async_get(url, *, headers=None, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, **kwargs) as response:
            result = {
                'status': response.status,
                'content_type': response.headers.get('content-type'),
                'text': await response.text(),
                'json': await response.json()
            }
            return result

async def async_post(url, *, data=None, headers=None, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data, **kwargs) as response:
            result = {
                'status': response.status,
                'content_type': response.headers.get('content-type'),
                'text': await response.text(),
                'json': await response.json()
            }
            return result

async def async_put(url, *, data=None, headers=None, **kwargs):
    async with aiohttp.ClientSession() as session:
        async with session.put(url, headers=headers, data=data, **kwargs) as response:
            result = {
                'status': response.status,
                'content_type': response.headers.get('content-type'),
                'text': await response.text(),
                'json': await response.json()
            }
            return result

async def async_upload_file(url, path, headers=None):
    async with aiohttp.ClientSession(headers=headers) as session:
        with open(path, "rb") as file:
            form_data = aiohttp.FormData()
            form_data.add_field("file", file, filename=os.path.basename(path))
            async with session.put(url, data=form_data) as response:
                result = {
                    'status': response.status,
                    'content_type': response.headers.get('content-type'),
                    'text': await response.text(),
                    'json': await response.json()
                }
                return result