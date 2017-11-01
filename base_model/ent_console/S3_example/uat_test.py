import boto.ses

AWS_ACCESS_KEY = 'AKIAI47I6QMKEDYU5OXA'
AWS_SECRET_KEY = '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'

from boto.s3.connection import S3Connection
 
AWS_KEY = AWS_ACCESS_KEY
AWS_SECRET = AWS_SECRET_KEY
 
aws_connection = S3Connection(AWS_KEY, AWS_SECRET)
bucket = aws_connection.get_bucket('gtos-store-uat')

for file_key in bucket.list():
    print(file_key.name)

key = boto.s3.key.Key(bucket, 'testfile')
with open('testfile') as f:
    key.set_contents_from_file(f)



