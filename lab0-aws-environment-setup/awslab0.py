import boto3
import io
import zipfile

sts = boto3.client("sts")
lambda_client = boto3.client("lambda")

account = sts.get_caller_identity()["Account"]
role_arn = f"arn:aws:iam::{account}:role/LabRole"
name = "my-first-lambda"
buffer = io.BytesIO()

with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
    z.write("lambda_function.py")

package_bytes = buffer.getvalue()

response = lambda_client.create_function(
    FunctionName=name,
    Runtime="python3.13",
    Role=role_arn,
    Handler="lambda_function.lambda_handler",
    Code={"ZipFile": package_bytes},
)

print(response)