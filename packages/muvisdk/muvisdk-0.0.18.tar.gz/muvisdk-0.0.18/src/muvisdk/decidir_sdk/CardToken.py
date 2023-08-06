import requests
import json

from ..response import ok, error


class CardToken:
    def __init__(self, url: str, private_key: str, public_key: str):
        self.url = url
        self.private_key = private_key
        self.public_key = public_key
        self.headers = {
            'apikey': self.private_key,
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }

    def create(self, card: dict):
        if 'decidir_id' in card:
            card['id'] = card['decidir_id']

        body = {
            'token': card['id'],
            'security_code': '999'
        }
        self.headers['apikey'] = self.public_key
        r = requests.post(self.url + '/tokens', headers=self.headers, data=json.dumps(body))
        self.headers['apikey'] = self.private_key
        response = r.json()
        if r.status_code > 299:
            return error(response)
        return ok(response)
