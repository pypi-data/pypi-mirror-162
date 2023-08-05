from .model import Model

class OutMessageStrex(Model):


    def _accepted_params(self):
        return [
            'merchantId',
            'serviceCode',
            'businessModel',
            'preAuthServiceId',
            'preAuthServiceDescription',
            'age',
            'isRestricted',
            'smsConfirmation',
            'invoiceText',
            'price',
            'timeout',
            'billed',
            'resultCode',
            'resultDescription',
        ]
