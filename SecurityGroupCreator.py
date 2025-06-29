import boto3
import csv
from botocore.exceptions import ClientError

REGION = 'ap-south-1'
ec2 = boto3.client('ec2', region_name=REGION)

def get_vpc_id_by_name(vpc_name):
    response = ec2.describe_vpcs(
        Filters=[{'Name': 'tag:Name', 'Values': [vpc_name]}]
    )
    vpcs = response['Vpcs']
    if not vpcs:
        raise Exception(f"❌ VPC with name '{vpc_name}' not found.")
    return vpcs[0]['VpcId']

def format_rules(ports):
    ports_clean = [p.strip().upper() for p in ports if p.strip()]
    if 'ALL' in ports_clean:
        return [{
            'IpProtocol': '-1',
            'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
        }]
    rules = []
    for p in ports_clean:
        if p.isdigit():
            rules.append({
                'IpProtocol': 'tcp',
                'FromPort': int(p),
                'ToPort': int(p),
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
            })
    return rules

with open('security_groups.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name = row['GroupName'].strip()
        desc = row['Description'].strip()
        in_p = row.get('InboundPorts', '').split(';')
        out_p = row.get('OutboundPorts', '').split(';')
        vpc_name = row.get('VpcName', '').strip()

        try:
            vpc_id = get_vpc_id_by_name(vpc_name)
            resp = ec2.create_security_group(
                GroupName=name,
                Description=desc,
                VpcId=vpc_id
            )
            sg_id = resp['GroupId']
            print(f"✅ Created {name} in {vpc_name} ({sg_id})")

            # Revoke default outbound rule
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
                    print("  ↪ Revoked default outbound rule")
                except ClientError:
                    pass

            # Inbound rules
            ingress = format_rules(in_p)
            if ingress:
                ec2.authorize_security_group_ingress(
                    GroupId=sg_id,
                    IpPermissions=ingress
                )
                print(f"  ↪ Inbound rules: {ingress}")

            # Outbound rules
            if egress_rules:
                ec2.authorize_security_group_egress(
                    GroupId=sg_id,
                    IpPermissions=egress_rules
                )
                print(f"  ↪ Outbound rules: {egress_rules}")

        except ClientError as e:
            print(f"❌ Error processing {name}: {e.response['Error']['Message']}")
        except Exception as e:
            print(f"❌ Unexpected error for {name}: {e}")
