import boto3
import csv

CSV_FILE = 'LaunchInstance.csv'
REGION = 'ap-south-1'

ec2 = boto3.client('ec2', region_name=REGION)
ec2_resource = boto3.resource('ec2', region_name=REGION)

# Step 1: Get default VPC ID
def get_default_vpc_id():
    response = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
    return response['Vpcs'][0]['VpcId']

# Step 2: Map AZ to default subnet in that AZ
def get_default_subnet_in_az(vpc_id, az):
    response = ec2.describe_subnets(
        Filters=[
            {'Name': 'vpc-id', 'Values': [vpc_id]},
            {'Name': 'availability-zone', 'Values': [az]},
            {'Name': 'default-for-az', 'Values': ['true']}
        ]
    )
    subnets = response['Subnets']
    if not subnets:
        raise Exception(f"No default subnet found in {az}")
    return subnets[0]['SubnetId']

# Step 3: Convert SG name to SG ID
def get_sg_id_from_name(sg_name, vpc_id):
    response = ec2.describe_security_groups(
        Filters=[
            {'Name': 'group-name', 'Values': [sg_name]},
            {'Name': 'vpc-id', 'Values': [vpc_id]}
        ]
    )
    if not response['SecurityGroups']:
        raise Exception(f"Security group '{sg_name}' not found in VPC '{vpc_id}'")
    return response['SecurityGroups'][0]['GroupId']

# Step 4: Read instance definitions from CSV
def read_instances_from_csv(csv_file):
    instances = []
    with open(csv_file, 'r', newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            instances.append({
                'Name': row['Name'],
                'ImageId': row['ImageId'],
                'InstanceType': row['InstanceType'],
                'KeyName': row['KeyName'],
                'SecurityGroup': row['SecurityGroup'],
                'AvailabilityZone': row['AvailabilityZone']
            })
    return instances

# Step 5: Launch EC2 Instances
def launch_instances(instance_specs):
    vpc_id = get_default_vpc_id()

    for spec in instance_specs:
        try:
            subnet_id = get_default_subnet_in_az(vpc_id, spec['AvailabilityZone'])
            sg_id = get_sg_id_from_name(spec['SecurityGroup'], vpc_id)

            response = ec2.run_instances(
                ImageId=spec['ImageId'],
                InstanceType=spec['InstanceType'],
                KeyName=spec['KeyName'],
                MinCount=1,
                MaxCount=1,
                SubnetId=subnet_id,
                SecurityGroupIds=[sg_id],
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [{'Key': 'Name', 'Value': spec['Name']}]
                    }
                ]
            )
            instance_id = response['Instances'][0]['InstanceId']
            print(f"✅ Launched instance {instance_id} in {spec['AvailabilityZone']} as {spec['Name']}")
        except Exception as e:
            print(f"❌ Failed to launch {spec['Name']} in {spec['AvailabilityZone']}: {str(e)}")

# Step 6: Main Execution
if __name__ == "__main__":
    print(f"📄 Reading instance configs from: {CSV_FILE}")
    instance_data = read_instances_from_csv(CSV_FILE)

    if not instance_data:
        print("⚠️ No instance data found in CSV.")
    else:
        launch_instances(instance_data)
