"""
report.py - Formats and prints the audit findings from all four checks.
"""


def print_report(unattached_volumes, idle_instances, buckets_without_lifecycle, unused_eips):
    """
    Print a simple, one-line-per-resource report of everything flagged.
    """

    print("\n=== AWS Cost Auditor Report ===\n")

    print(f"-- Unattached EBS Volumes ({len(unattached_volumes)} found) --")
    if not unattached_volumes:
        print("  None found.")
    else:
        for volume in unattached_volumes:
            print(
                f"  {volume['volume_id']} | {volume['size_gb']} GB | "
                f"{volume['volume_type']} | {volume['availability_zone']} | "
                f"created {volume['create_time']}"
            )

    print(f"\n-- Idle EC2 Instances ({len(idle_instances)} found) --")
    if not idle_instances:
        print("  None found.")
    else:
        for instance in idle_instances:
            print(
                f"  {instance['instance_id']} | {instance['instance_type']} | "
                f"avg CPU {instance['avg_cpu_percent']}% over "
                f"{instance['days_checked']} datapoints | launched {instance['launch_time']}"
            )

    print(f"\n-- S3 Buckets Without Lifecycle Policies ({len(buckets_without_lifecycle)} found) --")
    if not buckets_without_lifecycle:
        print("  None found.")
    else:
        for bucket_name in buckets_without_lifecycle:
            print(f"  {bucket_name}")

    print(f"\n-- Unused Elastic IPs ({len(unused_eips)} found) --")
    if not unused_eips:
        print("  None found.")
    else:
        for ip in unused_eips:
            print(f"  {ip}")

    print()