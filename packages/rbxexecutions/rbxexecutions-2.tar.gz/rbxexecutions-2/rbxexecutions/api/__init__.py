import aiohttp

url = 'https://counter.kelprepl.repl.co/api/'
key_dev = ''

class object_for_post:
	def __init__(self):
		self.key_dev = key_dev

async def send_request(href, body) -> dict:
    async with aiohttp.ClientSession() as session:
	    return await (await session.post(url + href, json = body.__dict__)).json()

async def get_execution() -> dict:
    payload = object_for_post()
    return await send_request('get', payload)

async def set_execution(value: int) -> dict:
    payload = object_for_post()
    payload.value = value
    return await send_request('setexecution', payload)

async def set_custom_name(name: str) -> dict:
    payload = object_for_post()
    payload.name = name
    return await send_request('customname', payload)