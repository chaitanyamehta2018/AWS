import boto3
import csv

CSV_FILE = 'LaunchInstance.csv'
USER_DATA_FILE = 'UserData.txt'
REGION = 'ap-south-1'

ec2 = boto3.client('ec2', region_name=REGION)
ec2_resource = boto3.resource('ec2', region_name=REGION)

# Step 1: Get VPC ID by name
def get_vpc_id_by_name(vpc_name):
    response = ec2.describe_vpcs(
        Filters=[{'Name': 'tag:Name', 'Values': [vpc_name]}]
    )
    vpcs = response['Vpcs']
    if not vpcs:
        raise Exception(f"VPC with name '{vpc_name}' not found.")
    return vpcs[0]['VpcId']

# Step 2: Map AZ to subnet in VPC
def get_subnet_in_az(vpc_id, az):
    response = ec2.describe_subnets(
        Filters=[
            {'Name': 'vpc-id', 'Values': [vpc_id]},
            {'Name': 'availability-zone', 'Values': [az]}
        ]
    )
    subnets = response['Subnets']
    if not subnets:
        raise Exception(f"No subnet found in {az} for VPC {vpc_id}")
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
                'AvailabilityZone': row['AvailabilityZone'],
                'IncludeUserData': row.get('IncludeUserData', 'No').strip().lower() == 'yes',
                'VpcName': row.get('VpcName', '').strip(),
                'AutoAssignPublicIp': row.get('AutoAssignPublicIp', 'No').strip().lower() == 'yes'
            })
    return instances

# Step 5: Load user data if required
def load_user_data():
    try:
        with open(USER_DATA_FILE, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️ Could not load user data: {e}")
        return ''

# Step 6: Launch EC2 Instances
def launch_instances(instance_specs):
    user_data_script = load_user_data()

    for spec in instance_specs:
        try:
            vpc_id = get_vpc_id_by_name(spec['VpcName']) if spec['VpcName'] else get_vpc_id_by_name('default')
            subnet_id = get_subnet_in_az(vpc_id, spec['AvailabilityZone'])
            sg_id = get_sg_id_from_name(spec['SecurityGroup'], vpc_id)

            params = {
                'ImageId': spec['ImageId'],
                'InstanceType': spec['InstanceType'],
                'KeyName': spec['KeyName'],
                'MinCount': 1,
                'MaxCount': 1,
                'SubnetId': subnet_id,
                'SecurityGroupIds': [sg_id],
                'TagSpecifications': [
                    {
                        'ResourceType': 'instance',
                        'Tags': [{'Key': 'Name', 'Value': spec['Name']}]
                    }
                ]
            }

            if spec['IncludeUserData']:
                params['UserData'] = user_data_script

            if spec['AutoAssignPublicIp']:
                params['NetworkInterfaces'] = [
                    {
                        'SubnetId': subnet_id,
                        'DeviceIndex': 0,
                        'AssociatePublicIpAddress': True,
                        'Groups': [sg_id]
                    }
                ]
                # Remove these as they conflict with NetworkInterfaces
                del params['SubnetId']
                del params['SecurityGroupIds']

            response = ec2.run_instances(**params)
            instance_id = response['Instances'][0]['InstanceId']
            print(f"✅ Launched instance {instance_id} in {spec['AvailabilityZone']} as {spec['Name']}")
        except Exception as e:
            print(f"❌ Failed to launch {spec['Name']} in {spec['AvailabilityZone']}: {str(e)}")

# Step 7: Main Execution
if __name__ == "__main__":
    print(f"📄 Reading instance configs from: {CSV_FILE}")
    instance_data = read_instances_from_csv(CSV_FILE)

    if not instance_data:
        print("⚠️ No instance data found in CSV.")
    else:
        launch_instances(instance_data)
