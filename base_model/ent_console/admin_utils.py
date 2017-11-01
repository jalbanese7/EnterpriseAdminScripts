import boto.ses

AWS_ACCESS_KEY = 'AKIAI3J3EK7XBUKDNUIQ'  
AWS_SECRET_KEY = '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'

class Email(object):  
    def __init__(self, to, subject):
        self.to = to
        self.subject = subject
        self._html = None
        self._text = None
        self._format = 'html'

    def html(self, html):
        self._html = html

    def text(self, text):
        self._text = text

    def send(self, from_addr=None):
        body = self._html

        if not from_addr:
            from_addr = 'enterprise@guardiantos.com'
        if not self._html and not self._text:
            raise Exception('You must provide a text or html body.')
        if not self._html:
            self._format = 'html'
            body = self._html

        connection = boto.ses.connect_to_region(
            'us-east-1',
            aws_access_key_id=AWS_ACCESS_KEY, 
            aws_secret_access_key=AWS_SECRET_KEY
        )

        return connection.send_email(
            from_addr,
            self.subject,
            None,
            self.to,
            format=self._format,
            text_body=self._text,
            html_body=self._html
        )



