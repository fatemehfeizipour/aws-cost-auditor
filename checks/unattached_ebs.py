import boto3

def check_unattached_volumes(ec2_client):

    """
    Scan for EBS volumes that are not attached to any instance.
    Returns a list of dicts with details on each unattached volume.
    """

    unattached_volumes =[]

    paginator = ec2_client.get_paginator('describe_volumes')
    page_iterator = paginator.paginate(
        Filters=[
            {'Name': 'status', 'Values': ['available']}
        ]
    )

    for page in page_iterator:
        for volume in page['Volumes']:
            volume_info = {
                'volume_id': volume['VolumeId'],
                'size_gb': volume['Size'],
                'volume_type': volume['VolumeType'],
                'availability_zone': volume['AvailabilityZone'],
                'create_time': volume['CreateTime'],
            }
            unattached_volumes.append(volume_info)
    return unattached_volumes

# --- This part actually runs the check ---

if __name__ == "__main__":
    session = boto3.Session(profile_name = 'cost-auditor', region_name = 'ca-central-1')
    ec2_client = session.client('ec2')

    result = check_unattached_volumes(ec2_client)
    print(result)

