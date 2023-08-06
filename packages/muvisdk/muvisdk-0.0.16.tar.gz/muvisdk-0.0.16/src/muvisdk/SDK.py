from .mercadopago_sdk.MercadoPagoSDK import MercadoPagoSDK
from .decidir_sdk.DecidirSDK import DecidirSDK


class SDK:
    def __init__(self, merchant: dict, processor: str = None):
        # Si se le indica el procesador
        self.processor = processor
        if processor == 'mercadopago':
            self._sdk = MercadoPagoSDK(merchant)
            return
        elif processor == 'mp_marketplace':
            self._sdk = MercadoPagoSDK(merchant, marketplace=True)
            return
        elif processor == 'decidir':
            self._sdk = DecidirSDK(merchant)
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

    def refund(self):
        return self._sdk.refund()

    def which(self):
        return self.processor

