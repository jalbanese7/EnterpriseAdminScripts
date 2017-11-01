import boto.ses

AWS_ACCESS_KEY = 'AKIAI2XGMOBNF6E5WLSQ'
AWS_SECRET_KEY = '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'

from boto.s3.connection import S3Connection
 
AWS_KEY = AWS_ACCESS_KEY
AWS_SECRET = AWS_SECRET_KEY
 
aws_connection = S3Connection(AWS_KEY, AWS_SECRET)
bucket = aws_connection.get_bucket('gtos-store-dev')

for file_key in bucket.list():
    print(file_key.name)

key = boto.s3.key.Key(bucket, 'testfile')
with open('testfile') as f:
    key.set_contents_from_file(f)



