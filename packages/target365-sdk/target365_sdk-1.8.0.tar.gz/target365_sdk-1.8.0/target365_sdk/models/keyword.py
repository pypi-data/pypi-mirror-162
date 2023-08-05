from .model import Model

class Keyword(Model):

    def _accepted_params(self):
        return [
            'keywordId',
            'shortNumberId',
            'keywordText',
            'mode',
            'forwardUrl',
            'preAuthSettings', # KeywordPreAuthSettings class
            'enabled',
            'created',
            'lastModified',
            'tags',
            'customProperties',
            'aliases',
        ]
