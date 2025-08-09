import boto3
import json
import botocore

# ==== CONFIGURATION ====
bucket_name = "my-access-point-lab-bucket"  # must be globally unique
region = "ap-south-1"
account_id = "994626601075"
user_password = "Hello@123"

iam = boto3.client("iam")
s3 = boto3.client("s3", region_name=region)
s3control = boto3.client("s3control", region_name=region)

# ==== 1. CREATE S3 BUCKET ====
def create_bucket():
    try:
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={"LocationConstraint": region},
        )
        print(f"✅ Bucket '{bucket_name}' created.")
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "BucketAlreadyOwnedByYou":
            print(f"ℹ️ Bucket '{bucket_name}' already exists.")
        else:
            raise e

    # Create folders
    for folder in ["app1/", "app2/"]:
        s3.put_object(Bucket=bucket_name, Key=folder)
    print("✅ Created folders 'app1' and 'app2' inside bucket.")

# ==== 2. SET BUCKET POLICY ====
def set_bucket_policy():
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": "*"},
                "Action": "*",
                "Resource": [
                    f"arn:aws:s3:::{bucket_name}",
                    f"arn:aws:s3:::{bucket_name}/*"
                ],
                "Condition": {
                    "StringEquals": {
                        "s3:DataAccessPointAccount": account_id
                    }
                }
            }
        ]
    }
    s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy=json.dumps(policy)
    )
    print("✅ Bucket policy applied.")

# ==== 3. CREATE IAM USERS ====
def create_iam_user(username):
    try:
        iam.create_user(UserName=username)
        print(f"✅ User '{username}' created.")
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            print(f"ℹ️ User '{username}' already exists.")
        else:
            raise e

    # Create login profile
    try:
        iam.create_login_profile(
            UserName=username,
            Password=user_password,
            PasswordResetRequired=False
        )
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            print(f"ℹ️ Login profile for '{username}' already exists.")
        else:
            raise e

    # Create access key
    try:
        keys = iam.create_access_key(UserName=username)["AccessKey"]
        print(f"✅ Access key for '{username}':")
        print(f"  AccessKeyId: {keys['AccessKeyId']}")
        print(f"  SecretAccessKey: {keys['SecretAccessKey']}")
    except botocore.exceptions.ClientError as e:
        print(f"⚠️ Could not create access key for {username}: {e}")

# ==== 4. CREATE ACCESS POINTS ====
def create_access_point(ap_name, user_name, folder):
    try:
        s3control.create_access_point(
            AccountId=account_id,
            Name=ap_name,
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                'BlockPublicAcls': False,
                'IgnorePublicAcls': False,
                'BlockPublicPolicy': False,
                'RestrictPublicBuckets': False
            }
        )
        print(f"✅ Access point '{ap_name}' created.")
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "AccessPointAlreadyOwnedByYou":
            print(f"ℹ️ Access point '{ap_name}' already exists.")
        else:
            raise e

    # Access point policy
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "AWS": f"arn:aws:iam::{account_id}:user/{user_name}"
                },
                "Action": "s3:PutObject",
                "Resource": f"arn:aws:s3:{region}:{account_id}:accesspoint/{ap_name}/object/{folder}*"
            }
        ]
    }
    s3control.put_access_point_policy(
        AccountId=account_id,
        Name=ap_name,
        Policy=json.dumps(policy)
    )
    print(f"✅ Policy applied to access point '{ap_name}'.")

# ==== 5. CREATE POLICY AND ATTACH TO USERS ====
def create_and_attach_policy():
    policy_name = "access-point-user-access-policy"
    policy_doc = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:ListAccessPoints",
                    "s3:GetAccessPoint",
                    "s3:ListBucket"
                ],
                "Resource": "*"
            }
        ]
    }

    try:
        policy_arn = iam.create_policy(
            PolicyName=policy_name,
            PolicyDocument=json.dumps(policy_doc)
        )["Policy"]["Arn"]
        print(f"✅ Policy '{policy_name}' created.")
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "EntityAlreadyExists":
            policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
            print(f"ℹ️ Policy '{policy_name}' already exists.")
        else:
            raise e

    # Attach to both users
    for user in ["user1", "user2"]:
        iam.attach_user_policy(UserName=user, PolicyArn=policy_arn)
        print(f"✅ Policy attached to '{user}'.")

# ==== MAIN EXECUTION ====
if __name__ == "__main__":
    create_bucket()
    set_bucket_policy()
    create_iam_user("user1")
    create_iam_user("user2")
    create_access_point("access-point-1", "user1", "app1/")
    create_access_point("access-point-2", "user2", "app2/")
    create_and_attach_policy()
    print("🎯 All tasks completed.")
