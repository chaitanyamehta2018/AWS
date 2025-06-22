import boto3

# Step 1: Prompt for instance name (optional)
instance_name = input("Enter a Name for your EC2 instance (press Enter to skip): ").strip()

# Step 2: Launch EC2 instance
ec2 = boto3.client('ec2', region_name='ap-south-1')  # Update region if needed

launch_params = {
    'ImageId': 'ami-0287a05f0ef0e9d9a',       # ✅ Valid RHEL 9 AMI (Mumbai region)
    'InstanceType': 't2.micro',
    'MinCount': 1,
    'MaxCount': 1,
    'KeyName': 'Ubuntu_ATS',                 # ✅ Replace with your key pair
    'SecurityGroups': ['default'],  # ✅ Replace with your security groups
}

# Step 3: Add Name tag only if user provided it
if instance_name:
    launch_params['TagSpecifications'] = [
        {
            'ResourceType': 'instance',
            'Tags': [{'Key': 'Name', 'Value': instance_name}]
        }
    ]

# Step 4: Launch instance
response = ec2.run_instances(**launch_params)
instance_id = response['Instances'][0]['InstanceId']

if instance_name:
    print(f"🎉 Launched EC2 instance '{instance_name}' with ID: {instance_id}")
else:
    print(f"🎉 Launched EC2 instance with ID: {instance_id} (no name tag)")
