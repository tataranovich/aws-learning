#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
import time
import boto3
import botocore

vpcId = 'vpc-43524721'
subnetId = 'subnet-1d0c067f'

# Create EFS filesystem
efs = boto3.client('efs')
try:
    clientResponse = efs.create_file_system(CreationToken='ECSSharedData', PerformanceMode='generalPurpose')
    ecsFilesystemId = clientResponse['FileSystemId']
    print("Created EFS filesystem. FileSystemId:", ecsFilesystemId)
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == 'FileSystemAlreadyExists':
        clientResponse = efs.describe_file_systems(CreationToken='ECSSharedData')
        ecsFilesystemId = clientResponse['FileSystems'][0]['FileSystemId']
        print("EFS filesystem already exists. FileSystemId:", ecsFilesystemId)
    else:
        print("Unexpected error:", e)

# Wait until EFS filesystem will be ready (efs waiters are not available in boto3)
print("Waiting until EFS filesystem will be ready")
ecsFilesystemState = 'creating'
while ecsFilesystemState == 'creating':
    clientResponse = efs.describe_file_systems(CreationToken='ECSSharedData')
    ecsFilesystemState = clientResponse['FileSystems'][0]['LifeCycleState']
    time.sleep(5)

# Create EFS mount target
try:
    clientResponse = efs.create_mount_target(FileSystemId=ecsFilesystemId, SubnetId=subnetId)
    ecsMountTargetId = clientResponse['MountTargetId']
    ecsMountTargetIp = clientResponse['IpAddress']
    print("Created EFS mount target. MountTargetId: %s, IpAddress: %s" % (ecsMountTargetId, ecsMountTargetIp))
except botocore.exceptions.ClientError as e:
    if e.response['Error']['Code'] == 'MountTargetConflict':
        clientResponse = efs.describe_mount_targets(FileSystemId=ecsFilesystemId)
        ecsMountTargetId = clientResponse['MountTargets'][0]['MountTargetId']
        ecsMountTargetIp = clientResponse['MountTargets'][0]['IpAddress']
        print("EFS mount target already exists. MountTargetId: %s, IpAddress: %s" % (ecsMountTargetId, ecsMountTargetIp))
    else:
        print("Unexpected error:", e)
