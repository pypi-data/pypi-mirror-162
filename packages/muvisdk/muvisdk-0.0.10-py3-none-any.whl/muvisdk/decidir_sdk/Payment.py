import requests
import json
from uuid import uuid4

from ..response import ok, error


class Payment:
    def __init__(self, url, private_key: str, public_key: str):
        self.url = url
        self.private_key = private_key
        self.public_key = public_key
        self.headers = {
            'apikey': self.private_key,
            'Content-Type': 'application/json',
            'Cache-Control': 'no-cache'
        }

    def create(self, payment_data: dict):
        body = {
            'customer': {
                'id': payment_data['payer']['decidir_id'],
                'email': payment_data['payer']['email']
            },
            'site_transaction_id': str(uuid4()),  # Debe ser unico? Unico por cliente o por merchant?
            # 'site_id': 28464385, # opcional
            'token': payment_data['token'],
            'payment_method_id': 1,    # Peso Argentino
            'bin': '450799',    # ?
            # se multiplica por 100; no acepta decimales.
            'amount': round(payment_data['transaction_amount'], 2) * 100,
            'currency': 'ARS',
            'installments': 1,
            'payment_type': 'single',
            'establishment_name': 'Cadena',  # opcional
            'sub_payments': []
        }
        if 'site_id' in payment_data:
            body['site_id'] = payment_data['site_id']
        if 'sub_payments' in payment_data:
            body['sub_payments'] = payment_data['sub_payments']
        if 'payment_type' in payment_data:
            body['payment_type'] = payment_data['payment_type']
        r = requests.post(self.url + '/payments', headers=self.headers, data=json.dumps(body))
        response = r.json()
        response['processor'] = 'decidir'
        if r.status_code < 400:
            response['status_detail'] = 'ok decidir'
            return ok(response)
        return error(response)

    def get(self, payment_id: int):
        r = requests.get(self.url + '/payments/{}'.format(payment_id), headers=self.headers)
        return ok(r.json())
