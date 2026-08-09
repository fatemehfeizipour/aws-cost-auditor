import boto3

def check_s3_lifecycle_policies(s3_client):
    """ 
    Scan for S3 buckets that have no lifecycle policy configured.
    Returns a list of bucket names without a lifecycle policy.
    """

    buckets_without_lifecycle = []

    response = s3_client.list_buckets()

    for bucket in response['Buckets']:
        bucket_name = bucket['Name']

        try:
            s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)

        except s3_client.exceptions.ClientError as error:   
            error_code = error.response['Error']['Code']
            if error_code ==  "NoSuchLifecycleConfiguration":
             buckets_without_lifecycle.append(bucket_name)
            else:
                print(f"Warning!!: couldn't check {bucket_name}:{error_code}")
                pass
    return buckets_without_lifecycle

if __name__ == "__main__":

    session = boto3.Session(profile_name='cost_auditor')
    s3_client = session.client('s3')

    result = check_s3_lifecycle_policies(s3_client)
    print(result)