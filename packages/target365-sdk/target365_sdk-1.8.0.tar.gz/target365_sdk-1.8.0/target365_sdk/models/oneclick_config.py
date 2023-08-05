from .model import Model

class OneClickConfig(Model):

    def _accepted_params(self):
        return [
            'configId',
            'shortNumber',
            'merchantId',
            'serviceCode',
            'businessModel',
            'preAuthServiceId',
            'preAuthServiceDescription',
            'recurring',
            'redirectUrl',
            'onlineText',
            'offlineText',
            'age',
            'isRestricted',
            'invoiceText',
            'price',
            'subscriptionPrice',
            'subscriptionInterval',
            'subscriptionStartSms',
            'timeout',
            'created',
            'lastModified',
        ]
