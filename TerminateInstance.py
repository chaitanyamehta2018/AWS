import boto3

ec2 = boto3.resource('ec2', region_name='ap-south-1')  # 🔁 Change region if needed

def terminate_instance():
    user_input = input("Enter EC2 Instance ID (i-xxxx), Name tag, or * to terminate all: ").strip()

    instances_to_terminate = []

    if user_input == "*":
        # Terminate all running/stopped instances
        all_instances = list(ec2.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}]
        ))
        if not all_instances:
            print("⚠️ No running or stopped instances found.")
            return
        instances_to_terminate = all_instances

    elif user_input.startswith("i-"):
        instances_to_terminate = [ec2.Instance(user_input)]

    else:
        matched = list(ec2.instances.filter(
            Filters=[{'Name': 'tag:Name', 'Values': [user_input]},
                     {'Name': 'instance-state-name', 'Values': ['running', 'stopped']}]
        ))
        if not matched:
            print(f"❌ No instance found with Name tag: {user_input}")
            return
        instances_to_terminate = matched

    # Confirm before termination
    for instance in instances_to_terminate:
        print(f"🛑 Terminating instance: {instance.id}")
        instance.terminate()

    for instance in instances_to_terminate:
        instance.wait_until_terminated()
        print(f"✅ Instance {instance.id} terminated successfully.")

terminate_instance()
