import boto3
import csv

CSV_FILE = 'subnetcreator.csv'
REGION = 'ap-south-1'

def read_subnet_config(csv_file):
    subnets = []
    vpc_name = None
    with open(csv_file, newline='') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if not vpc_name:
                vpc_name = row.get('VpcName', '').strip()
            subnets.append({
                'Name': row['Name'].strip(),
                'CIDR': row['CIDR'].strip(),
                'AZ': row['AZ'].strip(),
                'Public': row['Public'].strip().lower() == 'true'
            })
    return vpc_name, subnets

def get_vpc_id_by_name(ec2, vpc_name):
    vpcs = ec2.describe_vpcs(
        Filters=[{'Name': 'tag:Name', 'Values': [vpc_name]}]
    )
    if vpcs['Vpcs']:
        return vpcs['Vpcs'][0]['VpcId']
    else:
        raise Exception(f"No VPC found with name: {vpc_name}")

def create_subnets(vpc_id, subnets):
    ec2 = boto3.client('ec2', region_name=REGION)
    for subnet in subnets:
        try:
            response = ec2.create_subnet(
                VpcId=vpc_id,
                CidrBlock=subnet['CIDR'],
                AvailabilityZone=subnet['AZ']
            )
            subnet_id = response['Subnet']['SubnetId']
            ec2.create_tags(Resources=[subnet_id], Tags=[{'Key': 'Name', 'Value': subnet['Name']}])

            if subnet['Public']:
                ec2.modify_subnet_attribute(SubnetId=subnet_id, MapPublicIpOnLaunch={'Value': True})

            print(f"✅ Created Subnet: {subnet_id} [{subnet['Name']}] Public={subnet['Public']}")
        except Exception as e:
            print(f"❌ Failed to create subnet {subnet['Name']}: {e}")

if __name__ == '__main__':
    vpc_name, subnet_list = read_subnet_config(CSV_FILE)
    ec2 = boto3.client('ec2', region_name=REGION)
    try:
        vpc_id = get_vpc_id_by_name(ec2, vpc_name)
        print(f"🔍 Found VPC: {vpc_id} for name: {vpc_name}")
        create_subnets(vpc_id, subnet_list)
    except Exception as err:
        print(f"❌ Error: {err}")