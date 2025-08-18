import boto3

def create_vpc_and_subnets(region, vpc_name, cidr_block, subnets):
    ec2 = boto3.client('ec2', region_name=region)

    # Create VPC
    vpc = ec2.create_vpc(CidrBlock=cidr_block)
    vpc_id = vpc['Vpc']['VpcId']
    ec2.create_tags(Resources=[vpc_id], Tags=[{'Key': 'Name', 'Value': vpc_name}])
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={'Value': True})
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={'Value': True})
    print(f"✅ Created VPC {vpc_name} ({vpc_id}) in {region}")

    # Create Subnets
    for subnet_name, subnet_cidr, az in subnets:
        subnet = ec2.create_subnet(
            VpcId=vpc_id,
            CidrBlock=subnet_cidr,
            AvailabilityZone=az
        )
        subnet_id = subnet['Subnet']['SubnetId']
        ec2.create_tags(Resources=[subnet_id], Tags=[{'Key': 'Name', 'Value': subnet_name}])
        print(f"  ✅ Created Subnet {subnet_name} ({subnet_id}) in {az} - {subnet_cidr}")

    return vpc_id

# Configuration for both regions
mumbai_subnets = [
    ("Public_Subnet_1A", "192.168.100.0/26", "ap-south-1a"),
    ("Public_Subnet_1B", "192.168.100.64/26", "ap-south-1b"),
    ("Private_Subnet_1A", "192.168.100.128/26", "ap-south-1a"),
    ("Private_Subnet_1B", "192.168.100.192/26", "ap-south-1b"),
]

virginia_subnets = [
    ("Public_Subnet_1A", "192.168.200.0/26", "us-east-1a"),
    ("Public_Subnet_1B", "192.168.200.64/26", "us-east-1b"),
    ("Private_Subnet_1A", "192.168.200.128/26", "us-east-1a"),
    ("Private_Subnet_1B", "192.168.200.192/26", "us-east-1b"),
]

# Create VPCs and Subnets
india_vpc_id = create_vpc_and_subnets("ap-south-1", "India-VPC", "192.168.100.0/24", mumbai_subnets)
usa_vpc_id = create_vpc_and_subnets("us-east-1", "USA-VPC", "192.168.200.0/24", virginia_subnets)
