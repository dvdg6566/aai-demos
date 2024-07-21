import boto3
from botocore.exceptions import ClientError
from secrets import token_hex
import subprocess
import json
import time

region = 'ap-southeast-1'
s3_client = boto3.client('s3')
lambda_client = boto3.client('lambda')
iam = boto3.client('iam')

def create_buckets(prefix):
	bucketnames = [
		f"{prefix}-development",
		f"{prefix}-finance"
	]

	for bucket_name in bucketnames:
		try:
			s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region})
		except ClientError as e:
			print(f"Error creating bucket {bucket_name}")	
			print(e)
			exit(0)

	print("Successfully created S3 buckets!")

	subprocess.run("touch /tmp/test.txt", shell=True)
	with open("/tmp/test.txt", "w") as f:
		f.write("Upload Success!")

	for bucket_name in bucketnames:
		try: 
			s3_client.upload_file("/tmp/test.txt", bucket_name, "upload.txt")
		except ClientError as e:
			print(f"Error uploading demo file into bucket {bucket_name}")
			print(e)
			exit(0)

	print("Successfully written files to S3!")

def create_lambda_iam_role(prefix):
	role_name = f"{prefix}-lambda-role"

	trust_policy = {
		"Version": "2012-10-17",
		"Statement": [
			{
				"Effect": "Allow",
				"Principal": {
					"Service": "lambda.amazonaws.com"
				},
				"Action": "sts:AssumeRole"
			}
		]
	}

	try: 
		response = iam.create_role(
			RoleName = role_name,
			AssumeRolePolicyDocument=json.dumps(trust_policy)
		)

		role_arn = response['Role']['Arn']
		print(f"Created Lambda IAM Role with arn: {role_arn}")

		iam.attach_role_policy(
			RoleName = role_name,
			PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole'
		)

		print(f"Attached basic execution role to {role_arn}")
		
		time.sleep(10)

	except ClientError as e:
		print("Error creating Lambda IAM role!")
		print(e)
		exit(0)

	return role_arn

def create_lambda_function(prefix):
	function_name = f"{prefix}-listing"
	code_file = "lambda.zip"

	with open(code_file, "rb") as f:
		zip_file = f.read()

	role_arn = create_lambda_iam_role(prefix)
	
	try:
		response = lambda_client.create_function(
			FunctionName=function_name,
			Runtime='python3.11',
			Role=role_arn,
			Code={'ZipFile': zip_file},
			Handler='lambda_function.lambda_handler',
			Timeout=30,  # Adjust timeout as needed
			MemorySize=128,  # Adjust memory as needed
			Publish=True  # Publish the function immediately
		)

		print("Created Lambda function!")

	except ClientError as e:
		print(f"Error creating lambda function")
		print(e)
		exit(0)

	return role_arn

def generate_iam_policy(prefix, output):
	bucket_name = f"{prefix}-development"

	policy = {
	    "Version": "2012-10-17",
	    "Statement": [
	        {
	            "Sid": "ReadWriteAccess",
	            "Effect": "Allow",
	            "Action": [
	                "s3:GetObject",
	                "s3:PutObject",
	                "s3:ListBucket"
	            ],
	            "Resource": [
	                f"arn:aws:s3:::{bucket_name}",
	                f"arn:aws:s3:::{bucket_name}/*"
	            ]
	        }
	    ]
	}

	with open(output, "w") as f:
		json.dump(policy, f, indent=4)

def generate_resource_policy(prefix, output, lambda_arn):
	bucket_name = f"{prefix}-development"

	policy = {
	    "Version": "2012-10-17",
	    "Statement": [
	        {
	            "Sid": "AllowLambdaAccess",
	            "Effect": "Allow",
	            "Principal": {
	                "AWS": lambda_arn 
	            },
	            "Action": [
	                "s3:GetObject",
	                "s3:PutObject",
	                "s3:DeleteObject",
	                "s3:ListBucket"
	            ],
	            "Resource": [
	                f"arn:aws:s3:::{bucket_name}",
	                f"arn:aws:s3:::{bucket_name}/*"
	            ]
	        }
	    ]
	}

	with open(output, "w") as f:
		json.dump(policy, f, indent=4)

def main():
	prefix = "demo" + token_hex(4)
	create_buckets(prefix)
	lambda_role_arn = create_lambda_function(prefix)
	generate_iam_policy(prefix, "iam_policy.json")
	generate_resource_policy(prefix, "resource_policy.json", lambda_role_arn)

if __name__ == '__main__':
	main()