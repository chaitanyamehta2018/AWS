import boto3
import csv

CSV_FILE = 'vpc_config.csv'

DEFAULTS = {
    'VpcName': 'DefaultVPC',
    'VpcCidrBlock': '10.0.0.0/16',
    'EnableDnsSupport': 'True',
    'EnableDnsHostnames': 'True',
    'Region': 'ap-south-1',
    'CreateIGW': 'False',
    'CreateRoute': 'False'
}

def str_to_bool(value):
    return str(value).strip().lower() in ['true', '1', 'yes']

def read_configs(csv_file):
    configs = []
    with open(csv_file, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cfg = DEFAULTS.copy()
            cfg.update({k: v.strip() for k, v in row.items() if v.strip()})
            configs.append(cfg)
    return configs

def create_vpc(ec2, cfg):
    vpc = ec2.create_vpc(CidrBlock=cfg['VpcCidrBlock'])
    vpc_id = vpc['Vpc']['VpcId']
    ec2.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': cfg['VpcName']}])
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': str_to_bool(cfg['EnableDnsSupport'])})
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': str_to_bool(cfg['EnableDnsHostnames'])})
    print(f"✅ Created VPC: {vpc_id} [{cfg['VpcName']}]")
    return vpc_id

def create_igw_and_rt(ec2, vpc_id):
    igw_id = rt_id = None
    igw = ec2.create_internet_gateway()
    igw_id = igw['InternetGateway']['InternetGatewayId']
    ec2.attach_internet_gateway(VpcId=vpc_id, InternetGatewayId=igw_id)
    print(f"🌐 Attached IGW: {igw_id}")

    rt = ec2.create_route_table(VpcId=vpc_id)
    rt_id = rt['RouteTable']['RouteTableId']
    ec2.create_route(RouteTableId=rt_id, DestinationCidrBlock='0.0.0.0/0', GatewayId=igw_id)
    print(f"🛣️ Created Route Table: {rt_id}")
    return igw_id, rt_id

def create_subnet(ec2, cfg, vpc_id, rt_id):
    subnet = ec2.create_subnet(
        VpcId=vpc_id,
        CidrBlock=cfg['SubnetCidrBlock'],
        AvailabilityZone=cfg['AvailabilityZone']
    )
    subnet_id = subnet['Subnet']['SubnetId']
    ec2.create_tags(Resources=[subnet_id], Tags=[{'Key': 'Name', 'Value': cfg['SubnetName']}])
    ec2.modify_subnet_attribute(SubnetId=subnet_id, MapPublicIpOnLaunch={'Value': str_to_bool(cfg['MapPublicIp'])})
    print(f"📦 Created Subnet: {subnet_id} [{cfg['SubnetName']}]")

    if rt_id and str_to_bool(cfg.get('CreateRoute', 'False')):
        ec2.associate_route_table(RouteTableId=rt_id, SubnetId=subnet_id)
        print(f"🔗 Associated subnet {subnet_id} to route table {rt_id}")

    return subnet_id

def main():
    configs = read_configs(CSV_FILE)
    if not configs:
        print("⚠️ No valid configs found.")
        return

    region = configs[0]['Region']
    ec2 = boto3.client('ec2', region_name=region)

    vpc_id = create_vpc(ec2, configs[0])
    igw_id = rt_id = None

    if str_to_bool(configs[0].get('CreateIGW', 'False')):
        igw_id, rt_id = create_igw_and_rt(ec2, vpc_id)

    for cfg in configs:
        create_subnet(ec2, cfg, vpc_id, rt_id)

    print("\n✅ All resources created successfully.")

if __name__ == '__main__':
    main()
