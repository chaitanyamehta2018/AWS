import boto3

# Initialize RDS client (change region if needed)
rds = boto3.client('rds', region_name='ap-south-1')  # Mumbai region

# Parameters from your lab
db_identifier = "MyDB"
master_username = "admin"
master_password = "Indian123"

try:
    response = rds.create_db_instance(
        DBInstanceIdentifier=db_identifier,
        AllocatedStorage=20,                   # 20 GB
        DBInstanceClass="db.t3.micro",
        Engine="mysql",
        MasterUsername=master_username,
        MasterUserPassword=master_password,
        MultiAZ=True,                          # Multi-AZ enabled
        StorageType="gp3",
        AutoMinorVersionUpgrade=True,
        PubliclyAccessible=False,
        BackupRetentionPeriod=7,
        DeletionProtection=False,
        DBName="myDatabase",
        StorageEncrypted=False,
        CopyTagsToSnapshot=True,
        MonitoringInterval=0,
        EnablePerformanceInsights=False,
        Tags=[
            {"Key": "Name", "Value": "MyDB-Lab"}
        ]
    )

    print("Creating Multi-AZ RDS instance...")
    print(f"DB Identifier: {db_identifier}")
    print(f"Status: {response['DBInstance']['DBInstanceStatus']}")

except Exception as e:
    print("Error creating RDS instance:", e)
