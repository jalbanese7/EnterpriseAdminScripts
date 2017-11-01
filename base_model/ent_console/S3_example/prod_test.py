import boto.ses

AWS_ACCESS_KEY = 'AKIAJULL4AXDJTB73D4A'
AWS_SECRET_KEY = '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'

from boto.s3.connection import S3Connection
 
AWS_KEY = AWS_ACCESS_KEY
AWS_SECRET = AWS_SECRET_KEY
 
aws_connection = S3Connection(AWS_KEY, AWS_SECRET)
bucket = aws_connection.get_bucket('gtos-store-prod')

for file_key in bucket.list():
    print(file_key.name)

key = boto.s3.key.Key(bucket, 'testfile')
with open('testfile') as f:
    key.set_contents_from_file(f)



