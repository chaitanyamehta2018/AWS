import boto3
import time

# Initialize RDS client
rds = boto3.client('rds', region_name='ap-south-1')  # change if needed

def delete_all_rds_instances():
    try:
        dbs = rds.describe_db_instances()
        instances = dbs['DBInstances']

        if not instances:
            print("✅ No RDS instances found. Cleanup complete.")
            return

        for db in instances:
            db_identifier = db['DBInstanceIdentifier']
            print(f"\n🗑️ Checking RDS instance: {db_identifier}")

            # Step 1: Check deletion protection
            if db.get("DeletionProtection", False):
                print(f"   ⚠️ Deletion protection is enabled for {db_identifier}, disabling it...")
                try:
                    rds.modify_db_instance(
                        DBInstanceIdentifier=db_identifier,
                        DeletionProtection=False,
                        ApplyImmediately=True
                    )
                    print(f"   ✅ Deletion protection disabled for {db_identifier}")
                    time.sleep(5)  # wait briefly for update to apply
                except Exception as e:
                    print(f"   ❌ Error disabling deletion protection for {db_identifier}: {e}")
                    continue

            # Step 2: Delete DB instance
            try:
                rds.delete_db_instance(
                    DBInstanceIdentifier=db_identifier,
                    SkipFinalSnapshot=True,
                    DeleteAutomatedBackups=True
                )
                print(f"   🗑️ Delete triggered for {db_identifier}")
            except Exception as e:
                print(f"   ❌ Error deleting {db_identifier}: {e}")

    except Exception as e:
        print("Error describing RDS instances:", e)


if __name__ == "__main__":
    delete_all_rds_instances()
