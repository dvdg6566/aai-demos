import boto3
import time

ec2 = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')   

def list_vpcs():
    response = ec2.describe_vpcs()
    vpcs = response.get('Vpcs', [])
    ids = []
    for vpc in vpcs:
        vpcname = ""
        for tag in vpc.get('Tags', []):
            if tag['Key'] == 'Name':
                vpcname = tag['Value']
        if "demo" not in vpcname: continue
        ids.append(vpc['VpcId'])
        print(f"VPC ID: {vpc['VpcId']}, CIDR: {vpc['CidrBlock']}")
    return ids

def list_instances():
    response = ec2.describe_instances()
    reservations = response['Reservations']
    instance_ids = []
    for reservation in reservations:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_obj = ec2_resource.Instance(instance_id)
            instance_name = ""

            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':  # Adjust if you use a different tag key
                    instance_name = tag['Value']

            if "demo" not in instance_name: continue
            if instance["State"]["Name"] == "terminated": continue

            instance_ids.append(instance_id)
            
    return instance_ids

# 2. Terminate instances
def terminate_instances(instance_ids):
    if instance_ids:
        ec2.terminate_instances(InstanceIds=instance_ids)
        print("The following instances have been terminated:")
        for instance_id in instance_ids:
            print(instance_id)
        time.sleep(20)
    else:
        print("No running instances found to terminate.")

def delete_subnets(vpc_id):
    vpc = ec2_resource.Vpc(vpc_id)

    # Delete dependencies
    for subnet in vpc.subnets.all():
        for interface in subnet.network_interfaces.all():
            interface.delete()
        subnet.delete()

    for gateway in vpc.internet_gateways.all():
        vpc.detach_internet_gateway(InternetGatewayId=gateway.id)
        gateway.delete()

    filters = [{'Name': 'vpc-id', 'Values': [vpc.id]}]
    response = ec2.describe_vpc_endpoints(Filters=filters)
    endpoint_ids = [endpoint['VpcEndpointId'] for endpoint in response['VpcEndpoints'] 
                    if endpoint['VpcEndpointType'] == 'Gateway']

    if endpoint_ids:
        ec2.delete_vpc_endpoints(VpcEndpointIds=endpoint_ids)
        print("The following gateway endpoints have been deleted:")
        for endpoint_id in endpoint_ids:
            print(endpoint_id)

def delete_vpc(vpc_id):
    print()
    print("Deleting vpc", vpc_id)
    vpc = ec2_resource.Vpc(vpc_id)

    for route_table in vpc.route_tables.all():
        print(route_table)
        for association in route_table.associations:
            print(association, association.main)
            if not association.main:
                association.delete()

        # Delete the routes in the route table
        for route in route_table.routes:
            if route.destination_cidr_block != vpc.cidr_block:
                ec2.delete_route(  # Use the client to delete the route
                    RouteTableId=route_table.id,
                    DestinationCidrBlock=route.destination_cidr_block
                )

        try: 
            route_table.delete()
        except Exception as e:
            print(e)

    for security_group in vpc.security_groups.all():
        if security_group.group_name != 'default':
            security_group.delete()

    # # Delete VPC itself
    vpc.delete()
    print(f"VPC ID: {vpc_id} deleted")

def main():
    vpcs = list_vpcs()
    ec2_instances = list_instances()
    terminate_instances(ec2_instances)

    for vpc in vpcs:
        delete_subnets(vpc)
    for vpc in vpcs:
        delete_vpc(vpc)

if __name__ == '__main__':
    main()