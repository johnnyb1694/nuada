import boto3
import botocore
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

# 'Getters'

def get_vpc_id(name: str = 'vpc-nuada') -> bool:
    """
    Get the VPC ID associated with a given name tag
    """
    ec2 = boto3.client('ec2')
    res = ec2.describe_vpcs(Filters=[{'Name': 'tag:Name', 'Values': [name]}])

    id = 0
    if len(res['Vpcs']) >= 1:
        id = res['Vpcs'][0]['VpcId']
    return id

def get_subnet_ids(vpc_id: int):
    """
    Get the subnet IDs associated with a given VPC
    """
    ec2 = boto3.client('ec2')

    logging.info(f'Retrieving subnet identifiers for VPC with identifier: "{vpc_id}"')
    try:
        res = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
        ids = [subnet['SubnetId'] for subnet in res['Subnets']]
    except botocore.exceptions.ClientError as e:
        logging.error(e)
        raise e
    return ids

# Initialisation 
    
def init_vpc(name: str = 'vpc-nuada') -> int:
    """
    Configures a VPC inside AWS

    :param name: the desired name of the VPC (defaults to `vpc-nuada`)
    """
    ec2 = boto3.client('ec2')

    logging.info(f'Checking whether VPC exists with name: "{name}"')
    id = get_vpc_id(name)
    if id != 0:
        logging.info(f'VPC already exists with name: "{name}". Returning VPC ID: "{id}"')
        return id 
    
    try:
        logging.info(f'Creating VPC: "{name}"')
        res = ec2.create_vpc(CidrBlock='10.0.0.0/16', AmazonProvidedIpv6CidrBlock=False) # NB: configures a private network with network identifiers 10.0.0.0 - 10.0.255.254 (which are further subnetted in AWS)
        id = res['Vpc']['VpcId']
        logging.info(f'VPC successfully created with identifier: "{id}"')
        ec2.create_tags(Resources=[id], Tags=[{'Key': 'Name', 'Value': name}])
    except botocore.exceptions.ClientError as e:
        logging.error(e)
        raise e
    return id

def main():
    
    vpc_id = init_vpc()
    subnet_ids = get_subnet_ids(vpc_id)

    return True

if __name__ == '__main__':
    main()
