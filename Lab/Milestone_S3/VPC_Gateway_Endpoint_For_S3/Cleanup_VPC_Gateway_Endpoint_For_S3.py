import boto3

# ======== USER VARIABLES ========
REGION = "ap-south-1"  # Change if needed
# ================================

# AWS Clients
ec2_client = boto3.client("ec2", region_name=REGION)
s3_client = boto3.client("s3", region_name=REGION)
s3_resource = boto3.resource("s3", region_name=REGION)

print(f"==== Starting cleanup in region: {REGION} ====")

# 1. Terminate all EC2 instances
def terminate_all_ec2():
    print("[EC2] Searching for all running/stopped instances...")
    instances = ec2_client.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running", "stopped"]}]
    )
    instance_ids = [
        i["InstanceId"]
        for r in instances["Reservations"]
        for i in r["Instances"]
    ]
    if instance_ids:
        print(f"[EC2] Terminating instances: {instance_ids}")
        ec2_client.terminate_instances(InstanceIds=instance_ids)
    else:
        print("[EC2] No running/stopped instances found.")

# 2. Delete all S3 buckets in this account/region
def delete_all_s3():
    print("[S3] Listing all buckets...")
    buckets = s3_client.list_buckets()["Buckets"]
    if not buckets:
        print("[S3] No buckets found.")
        return

    for bucket in buckets:
        bucket_name = bucket["Name"]
        try:
            print(f"[S3] Emptying and deleting bucket: {bucket_name}")
            b = s3_resource.Bucket(bucket_name)
            b.objects.all().delete()
            s3_client.delete_bucket(Bucket=bucket_name)
        except Exception as e:
            print(f"[S3] Error deleting bucket {bucket_name}: {e}")

# 3. Delete all VPC Endpoints in the region
def delete_all_vpc_endpoints():
    print("[VPC] Listing all VPC Endpoints...")
    endpoints = ec2_client.describe_vpc_endpoints().get("VpcEndpoints", [])
    if not endpoints:
        print("[VPC] No VPC Endpoints found.")
        return

    for ep in endpoints:
        ep_id = ep["VpcEndpointId"]
        try:
            print(f"[VPC] Deleting VPC Endpoint: {ep_id}")
            ec2_client.delete_vpc_endpoints(VpcEndpointIds=[ep_id])
        except Exception as e:
            print(f"[VPC] Error deleting endpoint {ep_id}: {e}")

if __name__ == "__main__":
    terminate_all_ec2()
    delete_all_s3()
    delete_all_vpc_endpoints()
    print("==== Cleanup complete ====")
