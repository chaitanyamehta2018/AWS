import boto3

ec2 = boto3.resource('ec2', region_name='ap-south-1')  # 🔁 Change region if needed

def terminate_instance():
    user_input = input("Enter EC2 Instance ID (i-xxxx) or Name tag: ").strip()

    # If input looks like an instance ID
    if user_input.startswith("i-"):
        instance = ec2.Instance(user_input)
    else:
        instances = list(ec2.instances.filter(
            Filters=[{'Name': 'tag:Name', 'Values': [user_input]}]
        ))
        if not instances:
            print(f"❌ No instance found with Name tag: {user_input}")
            return
        instance = instances[0]

    print(f"🛑 Terminating instance: {instance.id}")
    instance.terminate()
    instance.wait_until_terminated()
    print("✅ Instance terminated successfully.")

terminate_instance()
