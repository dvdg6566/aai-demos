import boto3
from botocore.exceptions import ClientError
from secrets import token_hex

ec2 = boto3.resource('ec2')
AZ = 'ap-southeast-1a'

def setup_vpc(prefix):
	vpc_cidr_block = '10.0.0.0/16' 
	subnet_1_cidr = '10.0.1.0/24' 
	subnet_2_cidr = '10.0.2.0/24'

	# Create VPC
	vpc = ec2.create_vpc(CidrBlock=vpc_cidr_block)
	vpc.create_tags(Tags=[{'Key': 'Name', 'Value': f'{prefix}-vpc'}])
	vpc.wait_until_available()
	print(f"Created VPC name {prefix}-vpc!")

	# Create Internet Gateway
	internet_gateway = ec2.create_internet_gateway()
	vpc.attach_internet_gateway(InternetGatewayId=internet_gateway.id)
	print("Created internet gateway!")

	# Create Route Table (Public)
	public_route_table = vpc.create_route_table()
	public_route_table.create_tags(Tags=[{'Key': 'Name', 'Value': f'{prefix}-Public-Route-Table'}])
	public_route_table.create_route(
	    DestinationCidrBlock='0.0.0.0/0',
	    GatewayId=internet_gateway.id
	)

	subnet_1 = ec2.create_subnet(CidrBlock=subnet_1_cidr, VpcId=vpc.id, AvailabilityZone=AZ)  
	subnet_2 = ec2.create_subnet(CidrBlock=subnet_2_cidr, VpcId=vpc.id, AvailabilityZone=AZ)  
	print(f"Subnet 1 created: {subnet_1.id}")
	print(f"Subnet 1 created: {subnet_2.id}")

	ami_id = 'ami-0e97ea97a2f374e3d'
	instance_type = 't2.micro'
	security_group = ec2.create_security_group(
	    GroupName=f'{prefix}-securitygroup',
	    Description='demo security group',
	    VpcId=vpc.id
	)

	instances = ec2.create_instances(
	    ImageId=ami_id,
	    InstanceType=instance_type,
	    MinCount=1,
	    MaxCount=1,
	    NetworkInterfaces=[{
	        'SubnetId': subnet_1.id, 
	        'DeviceIndex': 0,
	        'AssociatePublicIpAddress': True  # Automatically assign public IP
	    }],
	    SecurityGroupIds=[security_group.id]
	)

	instance = instances[0]
	instance.wait_until_available()

	print(f"EC2 instance launched with id {instance.id} and public IP {instance.public_ip_address}")

def main():
	prefix = "demo" + token_hex(4)
	setup_vpc(prefix)

if __name__ == '__main__':
	main()