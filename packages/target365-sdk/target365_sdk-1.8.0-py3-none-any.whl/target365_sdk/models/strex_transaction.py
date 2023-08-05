from .model import Model

class StrexTransaction(Model):

    def _accepted_params(self):
        return [
            'transactionId',
            'sessionId',
            'correlationId',
            'shortNumber',
            'recipient',
            'content',
            'oneTimePassword',
            'deliveryMode',
            'statusCode',
            'detailedStatusCode',
            'statusDescription',
            'smscTransactionId',
            'created',
            'lastModified',
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
            'tags',
            'properties',
            'billed',
            'resultCode',
            'resultDescription',
        ]
