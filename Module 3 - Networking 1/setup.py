import boto3
from botocore.exceptions import ClientError
from secrets import token_hex
import time

ec2 = boto3.resource('ec2')
ec2_client = boto3.client('ec2')
AZ = 'ap-southeast-1a'

def launch_ec2_instance(name, subnet_id, security_group_id):
	print()
	print("Launching EC2 instance, ", name)
	ami_id = 'ami-0e97ea97a2f374e3d'
	instance_type = 't2.micro'

	network_interface = ec2.create_network_interface(
		SubnetId=subnet_id,
		Groups=[security_group_id], 
		Description=f'ENI for Server {name}'
	)

	waiter = ec2_client.get_waiter('network_interface_available')
	waiter.wait(NetworkInterfaceIds=[network_interface.id])
	print("Network interface created: ", network_interface.id)

	instances = ec2.create_instances(
		ImageId=ami_id,
		InstanceType=instance_type,
		MinCount=1,
		MaxCount=1,
		NetworkInterfaces=[
			{
				'NetworkInterfaceId': network_interface.id,
				'DeviceIndex': 0
			}
		],
		TagSpecifications=[
			{
				'ResourceType': 'instance',
				'Tags': [{
					'Key': 'Name',
					'Value': name
				}]
			}
		]
	)

	instance = instances[0]
	instance.wait_until_running()

	print(f"Launched EC2 instance {name}")
	if instance.public_ip_address:
		print(f"Instance Public IP Address: {instance.public_ip_address}")
	
def launch_subnet(vpcid, cidr, igwid):
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

	ec2_client.create_route(
		RouteTableId=route_table_id,
		DestinationCidrBlock='0.0.0.0/0',  # All IPv4 addresses
		GatewayId=igwid
	)
	
	print("Attached IGW to route table!")
	return subnet

def attach_sg_rule(security_group_id):
	ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                'IpProtocol': 'tcp',
                'FromPort': 22,
                'ToPort': 22,
                'IpRanges': [
                    {
                        'CidrIp': '0.0.0.0/0',
                        'Description': 'Allow SSH'
                    },
                ]
            },
        ]
    )

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

	subnet_1 = launch_subnet(vpc.id, subnet_1_cidr, internet_gateway.id)
	subnet_2 = launch_subnet(vpc.id, subnet_2_cidr, internet_gateway.id)

	security_group = ec2.create_security_group(
		GroupName=f'{prefix}-securitygroup',
		Description='demo security group',
		VpcId=vpc.id
	)
	attach_sg_rule(security_group.id)

	launch_ec2_instance(f"{prefix}-demo1", subnet_1.id, security_group.id)
	launch_ec2_instance(f"{prefix}-demo2", subnet_2.id, security_group.id)
	
def setup_instance(prefix):
	instance_name = f"{prefix}-webserver"
	print()
	print(f"Launching Web-server EC2 instance {instance_name}")

	ami_id = 'ami-0e97ea97a2f374e3d'
	instance_type = 't2.micro'
	security_group = ec2.create_security_group(
		GroupName=f'{prefix}-webserver-securitygroup',
		Description='demo webserver security group'
	)
	attach_sg_rule(security_group.id)

	user_data = """#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd

echo "<h1>Hello, World!</h1>" > /var/www/html/index.html"
"""

	instances = ec2.create_instances(
		ImageId=ami_id,
		InstanceType=instance_type,
		MinCount=1,
		MaxCount=1,
		SecurityGroupIds=[security_group.id],
		UserData=user_data,
		TagSpecifications=[
			{
				'ResourceType': 'instance',
				'Tags': [{
					'Key': 'Name',
					'Value': instance_name
				}]
			}
		]
	)

	instance = instances[0]
	instance.wait_until_running()
	instance.reload()

	print(f"Launched EC2 instance {instance_name}")
	if instance.public_ip_address:
		print(f"Instance Public IP Address: {instance.public_ip_address}")

def main():
	prefix = "demo" + token_hex(4)
	setup_vpc(prefix)
	setup_instance(prefix)

if __name__ == '__main__':
	main()