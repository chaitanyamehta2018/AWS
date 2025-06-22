import boto3

# Step 1: Prompt for instance name (optional) and instance count
base_name = input("Enter a base Name for your EC2 instances (press Enter to skip tagging): ").strip()
try:
    count = int(input("Enter the number of instances to launch: ").strip())
    if count < 1:
        raise ValueError
except ValueError:
    print("❌ Please enter a valid positive number.")
    exit()

# Step 2: Launch EC2 instances
ec2 = boto3.client('ec2', region_name='ap-south-1')

response = ec2.run_instances(
    ImageId='ami-0287a05f0ef0e9d9a',     # ✅ Valid RHEL 9 AMI (Mumbai)
    InstanceType='t2.micro',
    MinCount=count,
    MaxCount=count,
    KeyName='Ubuntu_ATS',               # ✅ Replace with your key pair
    SecurityGroups=['default'],         # ✅ Replace with your security groups
)

# Step 3: Assign name tags to each launched instance
instance_ids = [inst['InstanceId'] for inst in response['Instances']]

ec2_resource = boto3.resource('ec2', region_name='ap-south-1')

for i, instance_id in enumerate(instance_ids, start=1):
    name_tag = f"{base_name}_{i}" if base_name else None
    if name_tag:
        ec2_resource.create_tags(
            Resources=[instance_id],
            Tags=[{'Key': 'Name', 'Value': name_tag}]
        )
        print(f"🎉 Launched instance {instance_id} with name tag: {name_tag}")
    else:
        print(f"🎉 Launched instance {instance_id} (no name tag)")
