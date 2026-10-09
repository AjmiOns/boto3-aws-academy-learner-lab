import boto3
ec2 = boto3.client("ec2", region_name="us-east-1")
ssm = boto3.client("ssm", region_name="us-east-1")

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

    return instance_id


launch_instance("InstanceTest")