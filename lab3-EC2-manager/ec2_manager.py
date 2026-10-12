import boto3
import urllib.request
import urllib.error
import time

from botocore.exceptions import WaiterError

ec2 = boto3.client("ec2", region_name="us-east-1")
ssm = boto3.client("ssm", region_name="us-east-1")


def list_instances():
    paginator = ec2.get_paginator("describe_instances")
 
    rows = []
    for page in paginator.paginate():
        for reservation in page["Reservations"]:
            for inst in reservation["Instances"]:
                rows.append(inst)
 
    for inst in rows:
        tags = {t["Key"]: t["Value"] for t in inst.get("Tags", [])}
        print(f"{inst['InstanceId']:<21} "
              f"{inst['InstanceType']:<12} "
              f"{inst['State']['Name']:<12} "
              f"{inst.get('PublicIpAddress', '-'):<16} "
              f"{tags.get('Name', '(no name)')}")


def get_latest_amazon_linux_ami():
    parameter = (
        "/aws/service/ami-amazon-linux-latest/"
        "al2023-ami-kernel-default-x86_64"
    )

    response = ssm.get_parameter(Name=parameter)

    return response["Parameter"]["Value"]

def launch_instance(name):
    ami_id = get_latest_amazon_linux_ami()

    response = ec2.run_instances(
        ImageId=ami_id,
        InstanceType="t3.micro",
        MinCount=1,
        MaxCount=1,
        KeyName="vockey",
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [
                {"Key": "Name", "Value": name},
                {"Key": "CreatedBy", "Value": "boto3-lab"},
            ],
        }],
    )

    instance_id = response["Instances"][0]["InstanceId"]

    print(
        instance_id,
        response["Instances"][0]["State"]["Name"]
    )
    
    try:
        print("Waiting for the instance to reach 'running' ...")

        waiter = ec2.get_waiter("instance_running")

        waiter.wait(
            InstanceIds=[instance_id],
            WaiterConfig={
                "Delay": 15,
                "MaxAttempts": 40
            }
        )

        print("Instance is running.")

    except WaiterError:
        print("Timed out. Check the AWS Console.")
        return instance_id

    # the public IP only exists once it is running
    detail = ec2.describe_instances(
        InstanceIds=[instance_id]
    )

    running = detail["Reservations"][0]["Instances"][0]

    print(
        "Public IP:",
        running.get("PublicIpAddress", "not assigned")
    )

    return instance_id



def start_instance(instance_id):
    try:
        response = ec2.start_instances(
            InstanceIds=[instance_id]
        )

        change = response["StartingInstances"][0]

        print(
            change["PreviousState"]["Name"],
            "->",
            change["CurrentState"]["Name"]
        )

        print("Waiting for the instance to start...")

        ec2.get_waiter("instance_running").wait(
            InstanceIds=[instance_id],
            WaiterConfig={
                "Delay": 15,
                "MaxAttempts": 40
            }
        )

        print("Instance is running.")

    except WaiterError:
        print("Timeout: check the AWS Console.")


def stop_instance(instance_id):
    try:
        response = ec2.stop_instances(
            InstanceIds=[instance_id]
        )

        change = response["StoppingInstances"][0]

        print(
            change["PreviousState"]["Name"],
            "->",
            change["CurrentState"]["Name"]
        )

        print("Waiting for the instance to stop...")

        ec2.get_waiter("instance_stopped").wait(
            InstanceIds=[instance_id],
            WaiterConfig={
                "Delay": 15,
                "MaxAttempts": 40
            }
        )

        print("Instance is stopped.")

    except WaiterError:
        print("Timeout: check the AWS Console.")



def reboot_instance(instance_id):
    response = ec2.describe_instances(
        InstanceIds=[instance_id]
    )

    instance = response["Reservations"][0]["Instances"][0]
    state = instance["State"]["Name"]

    if state != "running":
        print(f"Cannot reboot instance: current state is {state}.")
        print("Start the instance first.")
        return

    ec2.reboot_instances(
        InstanceIds=[instance_id]
    )

    print("Reboot requested for:", instance_id)
    
    

def describe_instance(instance_id):
    response = ec2.describe_instances(
        InstanceIds=[instance_id]
    )

    instance = response["Reservations"][0]["Instances"][0]

    # Read the tags
    tags = {
        tag["Key"]: tag["Value"]
        for tag in instance.get("Tags", [])
    }

    # Basic information
    print("\n========== INSTANCE DETAILS ==========")
    print("Instance ID:", instance["InstanceId"])
    print("Name:", tags.get("Name", "(no name)"))
    print("State:", instance["State"]["Name"])
    print("Instance Type:", instance["InstanceType"])
    print("AMI ID:", instance["ImageId"])

    # Network information
    print("Availability Zone:",
          instance["Placement"]["AvailabilityZone"])
    print("Public IP:",
          instance.get("PublicIpAddress", "Not assigned"))
    print("Private IP:",
          instance.get("PrivateIpAddress", "Not assigned"))

    # Key pair
    print("Key Pair:",
          instance.get("KeyName", "None"))

    # Launch time
    print("Launch Time:", instance.get("LaunchTime", "Unknown"))

    # Security groups
    print("Security Groups:")
    for group in instance.get("SecurityGroups", []):
        print("  -", group["GroupName"],
              "(" + group["GroupId"] + ")")

    # All tags
    print("Tags:")
    if tags:
        for key, value in tags.items():
            print(f"  {key}: {value}")
    else:
        print("  No tags")

    print("======================================")



def add_tag(instance_id):
    key = input("Enter tag key: ").strip()
    value = input("Enter tag value: ").strip()

    if not key or not value:
        print("Tag key and value cannot be empty.")
        return

    ec2.create_tags(
        Resources=[instance_id],
        Tags=[
            {
                "Key": key,
                "Value": value
            }
        ]
    )

    print(f"Tag added successfully: {key} = {value}")
    
    
#Clean UP

def cleanup_instances():
    # 1. Find all lab instances using server-side filters
    response = ec2.describe_instances(
        Filters=[
            {
                "Name": "tag:CreatedBy",
                "Values": ["boto3-lab"]
            },
            {
                "Name": "instance-state-name",
                "Values": [
                    "pending",
                    "running",
                    "stopping",
                    "stopped"
                ]
            }
        ]
    )

    # 2. Collect instance IDs
    ids = [
        inst["InstanceId"]
        for reservation in response["Reservations"]
        for inst in reservation["Instances"]
    ]

    # 3. Check whether there are instances to terminate
    if not ids:
        print("No lab instances found to clean up.")
        return

    # 4. Display the instances before termination
    print("\nThese instances will be terminated:")
    for instance_id in ids:
        print(" ", instance_id)

    # 5. Ask for explicit confirmation
    confirmation = input("Type YES to confirm: ").strip()

    if confirmation != "YES":
        print("Cleanup cancelled.")
        return

    # 6. Terminate all matching instances
    ec2.terminate_instances(InstanceIds=ids)

    # 7. Wait until every instance is terminated
    print("Waiting for all instances to terminate...")

    try:
        ec2.get_waiter("instance_terminated").wait(
            InstanceIds=ids,
            WaiterConfig={
                "Delay": 15,
                "MaxAttempts": 40
            }
        )

        print(f"Terminated {len(ids)} instance(s).")

    except WaiterError:
        print("Timeout: check the EC2 Console.")    
    
    
#list_instances()
#print(get_latest_amazon_linux_ami())
#launch_instance("InstanceTest")
#instance_id = input("Enter the EC2 instance ID: ").strip()
#start_instance(instance_id)
#stop_instance(instance_id)
#reboot_instance(instance_id)
#add_tag(instance_id)
#describe_instance(instance_id)
#cleanup_instances()



def main():
    while True:
        print("\n=========================================")
        print("              EC2 MANAGER")
        print("=========================================")
        print("  1. List Instances")
        print("  2. Launch Instance")
        print("  3. Start Instance")
        print("  4. Stop Instance")
        print("  5. Reboot Instance")
        print("  6. Describe Instance")
        print("  7. Add Tags")
        print("  8. Get Latest AMI ")
        print("  9. CLEAN UP all lab instances")
        print("  0. Exit")
        print("=========================================")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            list_instances()

        elif choice == "2":
            name = input("Enter instance name: ").strip()

            if name:
                launch_instance(name)
            else:
                print("Instance name cannot be empty.")

        elif choice == "3":
            instance_id = input("Enter instance ID: ").strip()
            if instance_id:
                start_instance(instance_id)

        elif choice == "4":
            instance_id = input("Enter instance ID: ").strip()
            if instance_id:
                stop_instance(instance_id)

        elif choice == "5":
            instance_id = input("Enter instance ID: ").strip()
            if instance_id:
                reboot_instance(instance_id)

        elif choice == "6":
            instance_id = input("Enter instance ID: ").strip()
            if instance_id:
                describe_instance(instance_id)

        elif choice == "7":
            instance_id = input("Enter instance ID: ").strip()
            if instance_id:
                add_tag(instance_id)

        elif choice == "8":
            get_latest_amazon_linux_ami()
            
                
        elif choice == "9":
            cleanup_instances()

        elif choice == "0":
            print("Exiting EC2 Manager. Goodbye!")
            break

        else:
            print("Invalid choice. Please select from 0 to 9.")


if __name__ == "__main__":
    main()