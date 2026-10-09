import boto3
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


list_instances()
print(get_latest_amazon_linux_ami())
launch_instance("InstanceTest")