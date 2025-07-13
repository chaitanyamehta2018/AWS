import boto3
import time

REGION = 'ap-south-1'
ec2 = boto3.resource('ec2', region_name=REGION)
client = boto3.client('ec2', region_name=REGION)
elbv2 = boto3.client('elbv2', region_name=REGION)

def delete_ec2_instances():
    print("🔸 Terminating EC2 instances...")
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}])
    ids = [instance.id for instance in instances]
    if ids:
        ec2.instances.filter(InstanceIds=ids).terminate()
        print(f"Terminated: {ids}")
        time.sleep(10)

def delete_nat_gateways():
    print("🔸 Deleting NAT Gateways...")
    ngws = client.describe_nat_gateways()['NatGateways']
    for ngw in ngws:
        try:
            client.delete_nat_gateway(NatGatewayId=ngw['NatGatewayId'])
            print(f"Deleted NAT Gateway: {ngw['NatGatewayId']}")
        except Exception as e:
            print(f"Error deleting NAT GW {ngw['NatGatewayId']}: {e}")

def release_eips():
    print("🔸 Releasing Elastic IPs...")
    eips = client.describe_addresses()['Addresses']
    for eip in eips:
        if 'AssociationId' not in eip:
            try:
                client.release_address(AllocationId=eip['AllocationId'])
                print(f"Released EIP: {eip['AllocationId']}")
            except Exception as e:
                print(f"Error releasing EIP: {eip['AllocationId']}: {e}")

def delete_target_groups():
    print("🔸 Deleting Target Groups...")
    tgs = elbv2.describe_target_groups()['TargetGroups']
    for tg in tgs:
        try:
            elbv2.delete_target_group(TargetGroupArn=tg['TargetGroupArn'])
            print(f"Deleted Target Group: {tg['TargetGroupArn']}")
        except Exception as e:
            print(f"Error deleting TG {tg['TargetGroupArn']}: {e}")

def delete_load_balancers():
    print("🔸 Deleting Load Balancers...")
    lbs = elbv2.describe_load_balancers()['LoadBalancers']
    for lb in lbs:
        try:
            elbv2.delete_load_balancer(LoadBalancerArn=lb['LoadBalancerArn'])
            print(f"Deleted LB: {lb['LoadBalancerArn']}")
        except Exception as e:
            print(f"Error deleting LB {lb['LoadBalancerArn']}: {e}")
    time.sleep(10)  # Allow deletion to complete

def delete_vpc_endpoints():
    print("🔸 Deleting VPC Endpoints...")
    endpoints = client.describe_vpc_endpoints()['VpcEndpoints']
    for ep in endpoints:
        try:
            client.delete_vpc_endpoints(VpcEndpointIds=[ep['VpcEndpointId']])
            print(f"Deleted VPC Endpoint: {ep['VpcEndpointId']}")
        except Exception as e:
            print(f"Error deleting Endpoint {ep['VpcEndpointId']}: {e}")

def delete_vpc_endpoint_services():
    print("🔸 Deleting VPC Endpoint Services...")
    services = client.describe_vpc_endpoint_service_configurations()['ServiceConfigurations']
    for svc in services:
        try:
            client.delete_vpc_endpoint_service_configurations(ServiceIds=[svc['ServiceId']])
            print(f"Deleted Endpoint Service: {svc['ServiceId']}")
        except Exception as e:
            print(f"Error deleting service {svc['ServiceId']}: {e}")

def delete_security_groups():
    print("🔸 Deleting Security Groups...")
    sgs = client.describe_security_groups()['SecurityGroups']
    for sg in sgs:
        if sg['GroupName'] != 'default':
            try:
                client.delete_security_group(GroupId=sg['GroupId'])
                print(f"Deleted SG: {sg['GroupId']}")
            except Exception as e:
                print(f"Error deleting SG {sg['GroupId']}: {e}")

def delete_key_pairs():
    print("🔸 Deleting Key Pairs...")
    keys = client.describe_key_pairs()['KeyPairs']
    for key in keys:
        try:
            client.delete_key_pair(KeyName=key['KeyName'])
            print(f"Deleted Key Pair: {key['KeyName']}")
        except Exception as e:
            print(f"Error deleting key {key['KeyName']}: {e}")

def delete_vpcs():
    print("🔸 Deleting VPCs and all associated resources...")
    vpcs = client.describe_vpcs()['Vpcs']
    for vpc in vpcs:
        vpc_id = vpc['VpcId']
        if vpc.get('IsDefault'):
            continue

        print(f"Processing VPC: {vpc_id}")

        # Detach & delete IGW
        igws = client.describe_internet_gateways(Filters=[{'Name': 'attachment.vpc-id', 'Values': [vpc_id]}])['InternetGateways']
        for igw in igws:
            try:
                client.detach_internet_gateway(InternetGatewayId=igw['InternetGatewayId'], VpcId=vpc_id)
                client.delete_internet_gateway(InternetGatewayId=igw['InternetGatewayId'])
                print(f"Deleted IGW: {igw['InternetGatewayId']}")
            except Exception as e:
                print(f"Error deleting IGW {igw['InternetGatewayId']}: {e}")

        # Delete subnets
        subnets = client.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['Subnets']
        for subnet in subnets:
            try:
                client.delete_subnet(SubnetId=subnet['SubnetId'])
                print(f"Deleted Subnet: {subnet['SubnetId']}")
            except Exception as e:
                print(f"Error deleting Subnet {subnet['SubnetId']}: {e}")

        # Delete route tables (not main)
        rts = client.describe_route_tables(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])['RouteTables']
        for rt in rts:
            main = any(assoc.get('Main') for assoc in rt.get('Associations', []))
            if not main:
                try:
                    client.delete_route_table(RouteTableId=rt['RouteTableId'])
                    print(f"Deleted RT: {rt['RouteTableId']}")
                except Exception as e:
                    print(f"Error deleting RT {rt['RouteTableId']}: {e}")

        # Finally delete the VPC
        try:
            client.delete_vpc(VpcId=vpc_id)
            print(f"Deleted VPC: {vpc_id}")
        except Exception as e:
            print(f"Error deleting VPC {vpc_id}: {e}")

def main():
    delete_ec2_instances()
    delete_nat_gateways()
    release_eips()
    delete_load_balancers()
    delete_target_groups()
    delete_vpc_endpoints()
    delete_vpc_endpoint_services()
    delete_security_groups()
    delete_key_pairs()
    delete_vpcs()
    print("\n✅ All lab resources deleted successfully.")

if __name__ == "__main__":
    main()
