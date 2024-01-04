import boto3
import botocore
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

def init_vpc(name: str = 'vpc-nuada') -> int:
    """
    Configures a VPC inside AWS

    :param name: the desired name of the VPC (defaults to `vpc-nuada`)
    """
    ec2 = boto3.client('ec2')
    try:
        
        logging.info(f'Creating VPC: "{name}"')
        res = ec2.create_vpc(CidrBlock='10.0.0.0/16', AmazonProvidedIpv6CidrBlock=False)
        id = res['Vpc']['VpcId']

        logging.info(f'VPC successfully created with identifier: "{id}"')
        ec2.create_tags(Resources=[id], Tags=[{'Key': 'Name', 'Value': name}])

    except botocore.exceptions.ClientError as e:
        logging.error(e)
        raise e
    return id

def main():
    
    vpc = init_vpc()

    return True

if __name__ == '__main__':
    main()