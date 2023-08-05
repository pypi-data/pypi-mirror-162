from .model import Model

class DeliveryReport(Model):

    def _accepted_params(self):
        return [
            'correlationId',
            'sessionId',
            'transactionId',
            'price',
            'sender',
            'recipient',
            'operatorId',
            'statusCode',
            'detailedStatusCode',
            'delivered',
            'billed',
            'smscTransactionId',
            'smscMessageParts',
            'properties',
        ]
