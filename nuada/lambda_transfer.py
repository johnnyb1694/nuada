import logging

from dotenv import load_dotenv
load_dotenv()

log = logging.getLogger()
log.setLevel('INFO')

def lambda_handler(event, context):
    """
    Handler for AWS lambda integration.

    :param event: Payload of key-value pairs; these are parameters which can be dynamically passed to the underlying handler function
    """
    
    return True

if __name__ == '__main__':
    pass
