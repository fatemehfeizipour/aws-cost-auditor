import argparse
import boto3

from checks.unattached_ebs import check_unattached_volumes
from checks.idle_instances import check_idle_instances
from checks.s3_lifecycle import check_s3_lifecycle_policies
from checks.unused_eips import check_unused_eips
from report import print_report


def main():

    parser = argparse.ArgumentParser(
        description="Scan an AWS account for wasted/idle resources."
    )
    parser.add_argument(
        '--profile',
        default='cost-auditor',
        help="AWS CLI profile to use (default: cost-auditor)"
    )
    parser.add_argument(
        '--region',
        default='ca-central-1',
        help="AWS region to scan (default: ca-central-1)"
    )
    parser.add_argument(
        '--test-mode',
        action='store_true',
        help="Use a short lookback window (for testing idle-instance detection quickly)"
    )

    args = parser.parse_args()

    if args.test_mode:
        lookback_days = 0.05   # ~1.2 hours
        period = 300            # 5 minutes, matches basic monitoring's granularity
        print("Running in TEST MODE: short lookback window, not for real audits.")
    else:
        lookback_days = 14
        period = 86400

    session = boto3.Session(profile_name=args.profile, region_name=args.region)

    ec2_client = session.client('ec2')
    cloudwatch_client = session.client('cloudwatch')
    s3_client = session.client('s3')

    print(f"Starting the AWS cost auditor (profile: {args.profile}, region: {args.region}) ...")

    unattached_volumes = check_unattached_volumes(ec2_client)
    idle_instances = check_idle_instances(
        ec2_client, cloudwatch_client,
        lookback_days=lookback_days,
        period=period
    )
    buckets_without_lifecycle = check_s3_lifecycle_policies(s3_client)
    unused_eips = check_unused_eips(ec2_client)

    print_report(unattached_volumes, idle_instances, buckets_without_lifecycle, unused_eips)


if __name__ == "__main__":
    main()