import boto3
from datetime import datetime, timedelta, timezone

CPU_THRESHOLD_PERCENT = 5.0
LOOKBACK_DAYS = 14
PERIOD_SECONDS = 86400  # one datapoint per day

def check_idle_instances(ec2_client, cloudwatch_client, lookback_days=LOOKBACK_DAYS, period=PERIOD_SECONDS):

    """ 
    Scan running EC2 instances for low average CPU utilization
    over the lookback window, flagging likely idle-instances.
    Return a list of dicts with details on each idle instance.
    """

    idle_instances =[]

    paginator = ec2_client.get_paginator('describe_instances')
    page_iterator = paginator.paginate(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']}
        ]
    )
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(days=lookback_days)

    for page in page_iterator:
        for reservation in page['Reservations']:
            for instance in reservation['Instances']:

                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']

                metric_response = cloudwatch_client.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName='CPUUtilization',
                    Dimensions=[
                        {'Name': 'InstanceId', 'Value': instance_id}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=period,
                    Statistics=['Average']
                )

                datapoints = metric_response['Datapoints']

                if not datapoints:
                    # No metrics yet (e.g. instance launched very recently) - skip rather than flag
                    continue

                avg_cpu = sum(dp['Average'] for dp in datapoints) / len(datapoints)

                if avg_cpu < CPU_THRESHOLD_PERCENT:
                    instance_info = {
                        'instance_id': instance_id,
                        'instance_type': instance_type,
                        'avg_cpu_percent': round(avg_cpu,2),
                        'days_checked': len(datapoints),
                        'launch_time': instance['LaunchTime'],
                    }

                    idle_instances.append(instance_info)
    return idle_instances

# --- This part actually runs the check ---

if __name__ == "__main__":
    session = boto3.Session(profile_name = 'cost-auditor', region_name = 'ca-central-1')
    ec2_client = session.client('ec2')
    cloudwatch_client = session.client('cloudwatch')

    result = check_idle_instances(ec2_client, cloudwatch_client)
    print(result)