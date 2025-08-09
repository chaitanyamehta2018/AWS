import boto3
import botocore

# ==== CONFIGURATION ====
bucket_name = "my-access-point-lab-bucket"
region = "ap-south-1"
account_id = "994626601075"
policy_name = "access-point-user-access-policy"
users = ["user1", "user2"]
access_points = [
    {"name": "access-point-1"},
    {"name": "access-point-2"}
]

iam = boto3.client("iam")
s3 = boto3.client("s3", region_name=region)
s3control = boto3.client("s3control", region_name=region)

# ==== 1. DETACH AND DELETE POLICY ====
def delete_policy():
    policy_arn = f"arn:aws:iam::{account_id}:policy/{policy_name}"
    
    # Detach from users
    for user in users:
        try:
            iam.detach_user_policy(UserName=user, PolicyArn=policy_arn)
            print(f"✅ Detached policy from {user}")
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] != "NoSuchEntity":
                raise e
    
    # Delete non-default policy versions
    try:
        versions = iam.list_policy_versions(PolicyArn=policy_arn)["Versions"]
        for v in versions:
            if not v["IsDefaultVersion"]:
                iam.delete_policy_version(PolicyArn=policy_arn, VersionId=v["VersionId"])
                print(f"✅ Deleted policy version {v['VersionId']}")
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            print(f"ℹ️ Policy {policy_name} does not exist.")
            return
        else:
            raise e

    # Delete the policy itself
    try:
        iam.delete_policy(PolicyArn=policy_arn)
        print(f"✅ Deleted policy {policy_name}")
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchEntity":
            print(f"ℹ️ Policy {policy_name} does not exist.")
        else:
            raise e


# ==== 2. DELETE USERS ====
def delete_users():
    for user in users:
        try:
            # Delete access keys
            keys = iam.list_access_keys(UserName=user)["AccessKeyMetadata"]
            for key in keys:
                iam.delete_access_key(UserName=user, AccessKeyId=key["AccessKeyId"])
                print(f"✅ Deleted access key for {user}")

            # Delete login profile
            try:
                iam.delete_login_profile(UserName=user)
                print(f"✅ Deleted login profile for {user}")
            except botocore.exceptions.ClientError as e:
                if e.response["Error"]["Code"] != "NoSuchEntity":
                    raise e

            # Finally delete user
            iam.delete_user(UserName=user)
            print(f"✅ Deleted user {user}")
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchEntity":
                print(f"ℹ️ User {user} does not exist.")
            else:
                raise e

# ==== 3. DELETE ACCESS POINTS ====
def delete_access_points():
    for ap in access_points:
        try:
            s3control.delete_access_point(
                AccountId=account_id,
                Name=ap["name"]
            )
            print(f"✅ Deleted access point {ap['name']}")
        except botocore.exceptions.ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchAccessPoint":
                print(f"ℹ️ Access point {ap['name']} does not exist.")
            else:
                raise e

# ==== 4. EMPTY AND DELETE BUCKET ====
def delete_bucket():
    try:
        # Delete all objects
        objects = s3.list_objects_v2(Bucket=bucket_name)
        if "Contents" in objects:
            delete_keys = [{"Key": obj["Key"]} for obj in objects["Contents"]]
            s3.delete_objects(Bucket=bucket_name, Delete={"Objects": delete_keys})
            print(f"✅ Deleted all objects from bucket {bucket_name}")

        # Delete bucket
        s3.delete_bucket(Bucket=bucket_name)
        print(f"✅ Deleted bucket {bucket_name}")
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchBucket":
            print(f"ℹ️ Bucket {bucket_name} does not exist.")
        else:
            raise e

# ==== MAIN ====
if __name__ == "__main__":
    delete_access_points()
    delete_policy()
    delete_users()
    delete_bucket()
    print("🧹 Cleanup completed.")
