import boto3
from botocore.exceptions import ClientError

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')
iam = boto3.client('iam')

def clear_bucket(bucket_name):
	print(f"Deleting bucket {bucket_name}")

	bucket = s3.Bucket(bucket_name)

	try:
		bucket.objects.all().delete()
	except ClientError as e:
		print(f"Error deleting objects from bucket {bucket_name}")
		print(e)
		exit(0)

	try:
		s3_client.delete_bucket(Bucket=bucket_name)
	except ClientError as e:
		print(f"Error deleting bucket: {bucket_name}")
		print(e)
		exit(0)

def get_bucket_names():
	try:
		resp = s3_client.list_buckets()
		buckets = [b['Name'] for b in resp['Buckets']]
	except ClientError as e:
		print("Error listing buckets")
		print(e)
		exit(0)

	return buckets

def delete_demo_iam_entities():
	prefix="demo"

	# Delete IAM Users
	try:
		users = iam.list_users()['Users']
		for user in users:
			if user['UserName'].startswith(prefix):
				print(f"Deleting user:{user['UserName']}")
				# Additional safety check: Check if user has active access keys
				keys = iam.list_access_keys(UserName=user['UserName'])['AccessKeyMetadata']
				for key in keys:
					iam.delete_access_key(UserName=user['UserName'], AccessKeyId=key['AccessKeyId'])
				iam.delete_user(UserName=user['UserName'])
				print(f"Deleted user: {user['UserName']}")
	except ClientError as e:
		print(f"Error listing or deleting users: {user['UserName']}")
		print(e)
		exit(0)

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
	
	# Delete IAM Policies
	try:
		policies = iam.list_policies(Scope='Local')['Policies'] 
		for policy in policies:
			if policy['PolicyName'].startswith(prefix):
				print(f"Deleting policy: {policy}" )
				# Ensure policy is not the default version before deleting
				if not policy['IsDefaultVersion']:
					iam.delete_policy(PolicyArn=policy['Arn'])
	except ClientError as e:
		print(f"Error listing or deleting policy: {policy['Arn']}")
		print(e)
		exit(0)

def main():
	# bucket_names = get_bucket_names()
	# for bucket in bucket_names:
	# 	clear_bucket(bucket)
	delete_demo_iam_entities() 

if __name__ == '__main__':
	main()