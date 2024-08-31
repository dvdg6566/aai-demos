import boto3
from botocore.exceptions import ClientError
from secrets import token_hex
import time
import json

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
iam = boto3.client('iam')
lambda_client = boto3.client('lambda')

AZ = 'ap-southeast-1a'
subnetID = ""
securityGroupId = ""

def launch_subnet(vpcid, cidr):
	global subnetID

	subnet = ec2.create_subnet(
		CidrBlock=cidr, 
		VpcId=vpcid, 
		AvailabilityZone=AZ
	)  
	ec2_client.modify_subnet_attribute(
		SubnetId=subnet.id,
		MapPublicIpOnLaunch={'Value': True}
	)
	
	print()
	print("Subnet created: ", cidr, subnet.id)

	response = ec2_client.create_route_table(VpcId=vpcid)
	route_table_id = response['RouteTable']['RouteTableId']
	ec2_client.associate_route_table(
		RouteTableId=route_table_id,
		SubnetId=subnet.id
	)
	print("Created route table ", route_table_id)

	subnetID = subnet.id

	return subnet

def create_security_group_in_vpc(vpc_id, group_name):
    ec2_client = boto3.client('ec2')

    try:
        response = ec2_client.create_security_group(
            GroupName=group_name,
            Description="placeholder",
            VpcId=vpc_id
        )

        global securityGroupId
        securityGroupId = response['GroupId']
        print(f"Security group '{group_name}' created with ID: {securityGroupId}")
        return securityGroupId

    except Exception as e:
        print(f"Error creating security group!")
        print(e)
        exit(0)

        return None

def setup_vpc(prefix):
	vpc_cidr_block = '10.0.0.0/16' 
	subnet_cidr = '10.0.1.0/24'

	# Create VPC
	vpc = ec2.create_vpc(CidrBlock=vpc_cidr_block)
	vpc.create_tags(Tags=[{'Key': 'Name', 'Value': f'{prefix}-vpc'}])
	vpc.wait_until_available()
	print(f"Created VPC name {prefix}-vpc!")

	# Launch 1 private Subnet
	launch_subnet(vpc.id, subnet_cidr)

	create_security_group_in_vpc(vpc.id, f"{prefix}-sg")

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

		iam.attach_role_policy(
			RoleName = role_name,
			PolicyArn='arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole'
		)
		
		print(f"Attached basic execution role to {role_arn}")
		
		time.sleep(10)

	except ClientError as e:
		print("Error creating Lambda IAM role!")
		print(e)
		exit(0)

	return role_arn

def create_lambda_function(prefix, subnet_ids, sg_ids):
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
			Timeout=5,  # Adjust timeout as needed
			MemorySize=128,  # Adjust memory as needed
			Publish=True,  # Publish the function immediately
			VpcConfig={
                'SubnetIds': subnet_ids,
                'SecurityGroupIds': sg_ids
            }
		)

		print("Created Lambda function!")

	except ClientError as e:
		print(f"Error creating lambda function")
		print(e)
		exit(0)

	return role_arn

def main():
	prefix = "demo" + token_hex(4)
	setup_vpc(prefix)

	global subnetID, securityGroupId

	print("Created subnetID ", subnetID)
	print("Created SG", securityGroupId)

	lambda_role_arn = create_lambda_function(prefix, [subnetID], [securityGroupId])

if __name__ == '__main__':
	main()
