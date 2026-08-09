import boto3
    
def check_unused_eips(ec2_client):
    response = ec2_client.describe_addresses()
    unused = []
    for eip in response['Addresses']:
        if 'AssociationId' not in eip:
            unused.append(eip['PublicIp'])
    return unused

# ---This part actually runs the check ---
if __name__ == "__main__":
    session = boto3.Session(profile_name='cost-auditor', region_name='ca-central-1')
    ec2_client = session.client('ec2')

    result = check_unused_eips(ec2_client)
    print(result)
