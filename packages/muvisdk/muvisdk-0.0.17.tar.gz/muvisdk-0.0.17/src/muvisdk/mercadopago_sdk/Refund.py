import mercadopago
from iso8601 import parse_date
from ..response import ok, error

class Refund:
    def __init__(self, sdk: mercadopago.SDK):
        self.sdk = sdk

    def create(self, payment_id:str,amount:float=None):
        refund_data = {
            "amount": amount
        }
        refund_response = self.sdk.refund().create(payment_id,refund_data)
        if refund_response['status'] < 400:
            return ok(refund_response['response'])
        else:
            return error(refund_response['response'])
