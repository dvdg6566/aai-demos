import boto3
import time

ec2 = boto3.client('ec2')
ec2_resource = boto3.resource('ec2')   

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

def main():
    ec2_instances = list_instances()
    terminate_instances(ec2_instances)

if __name__ == '__main__':
    main()