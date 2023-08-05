from .model import Model

class StrexRegistrationSms(Model):

    def _accepted_params(self):
        return [
            'transactionId',
            'recipient',
            'merchantId',
            'smsText',
        ]
