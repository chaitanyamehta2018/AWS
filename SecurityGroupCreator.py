import boto3
import csv
from botocore.exceptions import ClientError

# Initialize EC2 client
ec2 = boto3.client('ec2')

# Get default VPC ID
vpcs = ec2.describe_vpcs(Filters=[{'Name': 'isDefault', 'Values': ['true']}])
default_vpc_id = vpcs['Vpcs'][0]['VpcId']

def format_rules(ports):
    ports_clean = [p.strip().upper() for p in ports if p.strip()]
    # Handle ALL traffic
    if 'ALL' in ports_clean:
        return [{
            'IpProtocol': '-1',
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }]

    rules = []
    for p in ports_clean:
        # Numeric port -> TCP
        if p.isdigit():
            rules.append({
                'IpProtocol': 'tcp',
                'FromPort': int(p),
                'ToPort': int(p),
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            })
        # Extend here for protocols like icmp, udp, or custom CIDRs
    return rules

with open('security_groups.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name = row['GroupName']
        desc = row['Description']
        in_p = row.get('InboundPorts', '').split(';')
        out_p = row.get('OutboundPorts', '').split(';')

        try:
            # Create security group
            resp = ec2.create_security_group(
                GroupName=name,
                Description=desc,
                VpcId=default_vpc_id
            )
            sg_id = resp['GroupId']
            print(f"✅ Created {name} ({sg_id})")

            # Remove default outbound rule if custom egress specified
            egress_rules = format_rules(out_p)
            if egress_rules:
                try:
                    ec2.revoke_security_group_egress(
                        GroupId=sg_id,
                        IpPermissions=[{
                            'IpProtocol': '-1',
                            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                        }]
                    )
                    print(f"  ↪ Revoked default outbound rule")
                except ClientError as e:
                    # Ignore if default rule was already removed
                    pass

            # Add ingress rules
            ingress = format_rules(in_p)
            if ingress:
                ec2.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=ingress
                )
                print(f"  ↪ Inbound rules set: {ingress}")

            # Add egress rules
            if egress_rules:
                ec2.authorize_security_group_egress(
                    GroupId=sg_id,
                    IpPermissions=egress_rules
                )
                print(f"  ↪ Outbound rules set: {egress_rules}")

        except ClientError as e:
            print(f"❌ Error processing {name}: {e.response['Error']['Message']}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
