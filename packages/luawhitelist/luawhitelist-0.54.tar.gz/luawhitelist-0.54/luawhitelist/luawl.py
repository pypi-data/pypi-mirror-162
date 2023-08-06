import requests

apikey = ''
url = 'https://whitelist.boblox.ga/'

def whitelist_add(discord_id: str, expire_timestamp: int) -> dict:
    return requests.get(url + f'api/v1/add/whitelist/{apikey}/{discord_id}/{expire_timestamp}').json()

def whitelist_del(discord_id: str) -> dict:
    return requests.get(url + f'api/v1/del/whitelist/{apikey}/{discord_id}').json()

def reset_hwid(discord_id: str) -> dict:
    return requests.get(url + f'api/v1/whitelist/reset-hwid/{apikey}/{discord_id}').json()

def reset_key(discord_id: str) -> dict:
    return requests.get(url + f'api/v1/whitelist/reset-key/{apikey}/{discord_id}').json()

def set_time(discord_id: str, expire_timestamp: int):
    return requests.get(url + f'api/v1/whitelist/settime/{apikey}/{discord_id}/{expire_timestamp}').json()

def info(discord_id: str):
    return requests.get(url + f'api/v1/info/whitelist/{apikey}/{discord_id}').json()

def list_whitelist():
    return requests.get(url + f'api/v1/list/premium/{apikey}').json()