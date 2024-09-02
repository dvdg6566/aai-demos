import boto3
from botocore.exceptions import ClientError

iam = boto3.client('iam')
lambda_client = boto3.client('lambda')

def delete_demo_iam_roles():
	prefix="demo"

	# Delete IAM Roles
	try:
		roles = iam.list_roles()['Roles']
		for role in roles:
			if role['RoleName'].startswith(prefix):
				print(f"Deleting role:{role['RoleName']}")
				# Detach all policies before deleting
				for policy in iam.list_attached_role_policies(RoleName=role['RoleName'])['AttachedPolicies']:
					iam.detach_role_policy(RoleName=role['RoleName'], PolicyArn=policy['PolicyArn'])
				iam.delete_role(RoleName=role['RoleName'])
				print(f"Deleted role: {role['RoleName']}")
	except ClientError as e:
		print(f"Error listing or deleting roles: {role['roleName']}")
		print(e)
		exit(0)

def delete_lambda_functions():
    # Get all Lambda functions
    functions = lambda_client.list_functions()['Functions']

    # Filter and delete demo functions
    for function in functions:
        if function['FunctionName'].startswith('demo'):
            lambda_client.delete_function(FunctionName=function['FunctionName'])
            print(f"Deleted Lambda function: {function['FunctionName']}")

def main():
	delete_demo_iam_roles()
	delete_lambda_functions()

if __name__ == '__main__':
	main()