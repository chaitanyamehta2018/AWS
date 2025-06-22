import boto3

ec2 = boto3.client('ec2', region_name='ap-south-1')  # Change if you're in another region

response = ec2.run_instances(
    ImageId='ami-0287a05f0ef0e9d9a',      # ✅ Valid RHEL 9 AMI in Mumbai
    InstanceType='t2.micro',
    MinCount=1,
    MaxCount=1,
    KeyName='Ubuntu_ATS',         # ✅ Replace this
    SecurityGroups=['default']  # ✅ Replace this
)

instance_id = response['Instances'][0]['InstanceId']
print(f"🎉 Launched RHEL EC2 instance with ID: {instance_id}")
