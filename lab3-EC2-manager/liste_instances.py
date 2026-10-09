import boto3
ec2 = boto3.client("ec2", region_name="us-east-1")

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

list_instances()