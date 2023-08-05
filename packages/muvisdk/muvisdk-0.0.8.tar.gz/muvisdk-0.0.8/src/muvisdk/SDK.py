from .mercadopago_sdk.MercadoPagoSDK import MercadoPagoSDK
from .decidir_sdk.DecidirSDK import DecidirSDK


class SDK:
    def __init__(self, merchant:dict,processor:str=None):
        # Si se le indica el procesador
        self.processor = None
        if processor == 'mercadopago':
            self._sdk = MercadoPagoSDK(merchant)
            self.processor = 'mercadopago'
            return
        elif processor == 'decidir':
            self._sdk = DecidirSDK(merchant)
            self.processor = 'decidir'
            return
        # Si no utiliza el preferrred_processor que tenga el merchant
        if 'credentials' in merchant and merchant['credentials']['preferred_processor'] == 'decidir':
            self._sdk = DecidirSDK(merchant)
            self.processor = 'decidir'
        else:
            self._sdk = MercadoPagoSDK(merchant)
            self.processor = 'mercadopago'

    def customer(self):
        return self._sdk.customer()

    def card(self):
        return self._sdk.card()

    def card_token(self):
        return self._sdk.card_token()

    def payment(self):
        return self._sdk.payment()

    def which(self):
        return self.processor 
