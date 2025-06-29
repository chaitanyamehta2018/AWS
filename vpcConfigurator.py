import boto3
import csv

CSV_FILE = 'vpc_config.csv'

DEFAULTS = {
    'VpcName': 'DefaultVPC',
    'VpcCidrBlock': '10.0.0.0/16',
    'EnableDnsSupport': 'True',
    'EnableDnsHostnames': 'True',
    'SubnetName': 'DefaultSubnet',
    'SubnetCidrBlock': '10.0.1.0/24',
    'AvailabilityZone': 'ap-south-1a',
    'MapPublicIp': 'True',
    'CreateIGW': 'True',
    'CreateRoute': 'True',
    'Region': 'ap-south-1'
}

def read_config(csv_file):
    config = DEFAULTS.copy()
    try:
        with open(csv_file, newline='') as f:
            reader = csv.DictReader(f)
            row = next(reader, {})
            for key in DEFAULTS:
                if key in row and row[key].strip():
                    config[key] = row[key].strip()
    except Exception as e:
        print(f"⚠️ Could not read CSV properly. Using defaults. Reason: {e}")
    return config

def str_to_bool(value):
    return str(value).strip().lower() in ['true', '1', 'yes']

def create_vpc_resources(cfg):
    print(f"\n🚀 Creating VPC in region {cfg['Region']}")
    ec2 = boto3.client('ec2', region_name=cfg['Region'])

    # Create VPC
    vpc = ec2.create_vpc(CidrBlock=cfg['VpcCidrBlock'])
    vpc_id = vpc['Vpc']['VpcId']
    ec2.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': cfg['VpcName']}])
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': str_to_bool(cfg['EnableDnsSupport'])})
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': str_to_bool(cfg['EnableDnsHostnames'])})
    print(f"✅ Created VPC: {vpc_id} [{cfg['VpcName']}]")

    # Create Subnet
    subnet = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock=cfg['SubnetCidrBlock'],
        AvailabilityZone=cfg['AvailabilityZone']
    )
    subnet_id = subnet['Subnet']['SubnetId']
    ec2.create_tags(Resources=[subnet_id], Tags=[{'Key': 'Name', 'Value': cfg['SubnetName']}])
    ec2.modify_subnet_attribute(SubnetId=subnet_id, MapPublicIpOnLaunch={'Value': str_to_bool(cfg['MapPublicIp'])})
    print(f"✅ Created Subnet: {subnet_id} [{cfg['SubnetName']}]")

    igw_id = None
    rt_id = None

    # Create IGW and Route Table if required
    if str_to_bool(cfg['CreateIGW']):
        igw = ec2.create_internet_gateway()
        igw_id = igw['InternetGateway']['InternetGatewayId']
        ec2.attach_internet_gateway(VpcId=vpc_id, InternetGatewayId=igw_id)
        print(f"🌐 Attached Internet Gateway: {igw_id}")

        if str_to_bool(cfg['CreateRoute']):
            rt = ec2.create_route_table(VpcId=vpc_id)
            rt_id = rt['RouteTable']['RouteTableId']
            ec2.create_route(RouteTableId=rt_id, DestinationCidrBlock='0.0.0.0/0', GatewayId=igw_id)
            ec2.associate_route_table(RouteTableId=rt_id, SubnetId=subnet_id)
            print(f"🛣️ Created and associated Route Table: {rt_id}")

    return {
        'VpcId': vpc_id,
        'SubnetId': subnet_id,
        'InternetGatewayId': igw_id or 'N/A',
        'RouteTableId': rt_id or 'N/A'
    }

if __name__ == '__main__':
    config = read_config(CSV_FILE)
    summary = create_vpc_resources(config)

    print("\n📊 VPC Resource Summary:")
    for k, v in summary.items():
        print(f"{k}: {v}")
