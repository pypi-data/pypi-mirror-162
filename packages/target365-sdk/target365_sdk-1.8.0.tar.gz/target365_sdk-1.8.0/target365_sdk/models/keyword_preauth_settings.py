from .model import Model

class KeywordPreAuthSettings(Model):


    def _accepted_params(self):
        return [
            'InfoText',
            'InfoSender',
            'PrefixMessage',
            'PostfixMessage',
            'Delay',
            'MerchantId',
            'ServiceDescription',
            'Active',
        ]
