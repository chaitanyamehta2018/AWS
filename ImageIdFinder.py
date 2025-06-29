import boto3

ec2 = boto3.client('ec2', region_name='ap-south-1')

response = ec2.describe_images(
    Owners=['amazon'],
    Filters=[
        {'Name': 'name', 'Values': ['Windows_Server-2019-English-Full-Base-*']},
        {'Name': 'state', 'Values': ['available']},
        {'Name': 'architecture', 'Values': ['x86_64']},
        {'Name': 'root-device-type', 'Values': ['ebs']}
    ]
)

# Sort by creation date descending
images = sorted(response['Images'], key=lambda x: x['CreationDate'], reverse=True)
latest = images[0]
print("Latest 2019 Base AMI:", latest['ImageId'], "-", latest['Name'])
