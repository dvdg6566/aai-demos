import boto3
from botocore.exceptions import ClientError
from secrets import token_hex
import json
import time

lambda_client = boto3.client('lambda')
iam = boto3.client('iam')

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

def create_lambda_function(func_name, role_arn, code_file):

	with open(code_file, "rb") as f:
		zip_file = f.read()
	
	try:
		response = lambda_client.create_function(
			FunctionName=func_name,
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

def main():
	prefix = "demo" + token_hex(4)
	role_arn = create_lambda_iam_role(prefix)
	create_lambda_function(f"{prefix}-home", role_arn, "func1/lambda.zip")
	create_lambda_function(f"{prefix}-secondary", role_arn, "func2/lambda.zip")

if __name__ == '__main__':
	main()