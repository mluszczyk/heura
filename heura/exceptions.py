class EvaluatingException(Exception):
        def __init__(self, text='undefined'):
                super().__init__()
                self.text = text

        def __unicode__(self):
                return 'Evaulation exception ({})'.format(self.text)

        def __str__(self):
                return self.__unicode__()
