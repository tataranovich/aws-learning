#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from time import sleep
import boto3
from botocore.exceptions import ClientError

vpcId = 'vpc-43524721'
subnetId = 'subnet-1d0c067f'
instanceNumber = 2
namePrefix = 'Task3-'

ecsInstanceSecurityGroupName = namePrefix + 'InstanceSecurityGroup'
ecsMountTargetSecurityGroupName = namePrefix + 'MountTargetSecurityGroup'
ecsFileSystemName = namePrefix + 'FileSystem'
ecsClusterName = namePrefix + 'Cluster'
ecsLoadBalancerName = namePrefix + 'LoadBalancer'
ecsLaunchConfigurationName = namePrefix + 'LaunchConfiguration'
ecsAutoScalingGroupName = namePrefix + 'AutoScalingGroup'
ecsS3UserName = namePrefix + 'S3User'
ecsS3BucketName = namePrefix.lower() + 'bucket'
ecsDeployApplicationName = namePrefix + 'Application'
ecsRepositoryName = namePrefix.lower() + 'repository'

def ec2_create_security_group(group_name=None, description=None, vpc_id=None):
    client = boto3.client('ec2')
    security_group_id = None
    try:
        response = client.create_security_group(
            DryRun=False,
            GroupName=group_name,
            Description=description,
            VpcId=vpc_id
        )
        security_group_id = response['GroupId']
    except ClientError as e:
        if e.response['Error']['Code'] == 'InvalidGroup.Duplicate':
            response = client.describe_security_groups(
                 DryRun=False,
                 GroupNames=[group_name]
            )
            security_group_id = response['SecurityGroups'][0]['GroupId']
        else:
            print("Unknown error:", e)
    return security_group_id

def ec2_authorize_security_group_ingress(group_id=None, ip_protocol=None, from_port=None, to_port=None, cidr_ip=None):
    client = boto3.client('ec2')
    try:
        client.authorize_security_group_ingress(
            DryRun=False,
            GroupId=group_id,
            IpProtocol=ip_protocol,
            FromPort=from_port,
            ToPort=to_port,
            CidrIp=cidr_ip
        )
    except ClientError as e:
        if e.response['Error']['Code'] != 'InvalidPermission.Duplicate':
            print("Exception:", e)

def efs_create_filesystem(creation_token=None, performance_mode='generalPurpose'):
    client = boto3.client('efs')
    filesystem_id = None
    try:
        response = client.create_file_system(
            CreationToken=creation_token,
            PerformanceMode=performance_mode
        )
        filesystem_state = 'creating'
        while filesystem_state == 'creating':
            response = client.describe_file_systems(CreationToken=creation_token)
            filesystem_state = response['FileSystems'][0]['LifeCycleState']
            sleep(5)
        filesystem_id = response['FileSystems'][0]['FileSystemId']
    except ClientError as e:
        if e.response['Error']['Code'] == 'FileSystemAlreadyExists':
            response = client.describe_file_systems(CreationToken=creation_token)
            filesystem_id = response['FileSystems'][0]['FileSystemId']
        else:
            print("Unexpected error:", e)
    return filesystem_id

def efs_create_mount_target(filesystem_id=None, subnet_id=None, security_groups=[]):
    client = boto3.client('efs')
    mount_target_id = {}
    try:
        response = client.create_mount_target(
            FileSystemId=filesystem_id,
            SubnetId=subnet_id,
            SecurityGroups=security_groups
        )
        mount_target_state = 'creating'
        while mount_target_state == 'creating':
            response = client.describe_mount_targets(FileSystemId=filesystem_id)
            mount_target_state = response['MountTargets'][0]['LifeCycleState']
            sleep(5)
        mount_target_id['MountTargetId'] = response['MountTargets'][0]['MountTargetId']
        mount_target_id['IpAddress'] = response['MountTargets'][0]['IpAddress']
    except ClientError as e:
        if e.response['Error']['Code'] == 'MountTargetConflict':
            response = client.describe_mount_targets(FileSystemId=filesystem_id)
            mount_target_id['MountTargetId'] = response['MountTargets'][0]['MountTargetId']
            mount_target_id['IpAddress'] = response['MountTargets'][0]['IpAddress']
        else:
            print("Unexpected error:", e)
    return mount_target_id

print("Creating security group for ECS instances")
ecsInstanceSecurityGroupId = ec2_create_security_group(
    group_name=ecsInstanceSecurityGroupName,
    description='Security group for ECS instances',
    vpc_id=vpcId
)

print("Creating security group for EFS mount target")
ecsMountTargetSecurityGroupId = ec2_create_security_group(
    group_name=ecsMountTargetSecurityGroupName,
    description='Security group for EFS mount targets',
    vpc_id=vpcId
)

print("Authorizing security group ingress rules")
ec2_authorize_security_group_ingress(
    group_id=ecsInstanceSecurityGroupId,
    ip_protocol='tcp',
    from_port=22,
    to_port=22,
    cidr_ip='0.0.0.0/0'
)

ec2_authorize_security_group_ingress(
    group_id=ecsInstanceSecurityGroupId,
    ip_protocol='tcp',
    from_port=80,
    to_port=80,
    cidr_ip='0.0.0.0/0'
)

ec2_authorize_security_group_ingress(
    group_id=ecsMountTargetSecurityGroupId,
    ip_protocol='tcp',
    from_port=2049,
    to_port=2049,
    cidr_ip='172.31.0.0/16'
)

print("Creating EFS file system")
ecsEFSFileSystemId = efs_create_filesystem(creation_token=ecsFileSystemName)

print("Creating EFS mount target")
ecsMountTargetId = efs_create_mount_target(
    filesystem_id=ecsEFSFileSystemId,
    subnet_id=subnetId,
    security_groups=[
        ecsMountTargetSecurityGroupId
    ])

print("Creating ECS cluster")
ecs = boto3.client('ecs')
try:
    response = ecs.create_cluster(clusterName=ecsClusterName)
except ClientError as e:
    print(e)

print("Creating load balancer")
elb = boto3.client('elb')
try:
    response = elb.create_load_balancer(
        LoadBalancerName=ecsLoadBalancerName,
        Listeners=[
            {
                'Protocol' : 'tcp',
                'LoadBalancerPort' : 80,
                'InstanceProtocol' : 'tcp',
                'InstancePort' : 80
            }
        ],
        Subnets=[
            subnetId
        ],
        SecurityGroups=[
            ecsInstanceSecurityGroupId
        ]
    )
except ClientError as e:
    print(e)

autoscale = boto3.client('autoscaling')
ec2_user_data = """#!/bin/bash
mkdir /www
echo '{ip_address}:/ /www nfs4 _netdev,nfsvers=4.1,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2 0 2' >> /etc/fstab
mount /www
chown centos:centos /www
echo ECS_CLUSTER={cluster_name} >>/etc/ecs/ecs.config
ln -s /etc/ssl/certs/ca-bundle.crt /etc/ssl/ca-bundle.pem
service docker start
chkconfig docker on
usermod -aG docker centos
service amazon-ecs start
chkconfig amazon-ecs on
yum install -y ruby
curl -o /tmp/install https://aws-codedeploy-us-west-2.s3.amazonaws.com/latest/install
ruby /tmp/install auto
""".format(ip_address=ecsMountTargetId['IpAddress'], cluster_name=ecsClusterName)

print("Creating launch configuration")
try:
    autoscale.create_launch_configuration(
        LaunchConfigurationName=ecsLaunchConfigurationName,
        InstanceType='t2.micro',
        ImageId='ami-a08b3dc0',
        KeyName='awsdev',
        SecurityGroups=[
            ecsInstanceSecurityGroupId
        ],
        IamInstanceProfile='ECSInstanceRole',
        UserData=ec2_user_data
    )
except ClientError as e:
    if e.response['Error']['Code'] != 'AlreadyExists':
        print("Exception:", e)

print("Creating auto-scaling group")
try:
    autoscale.create_auto_scaling_group(
        AutoScalingGroupName=ecsAutoScalingGroupName,
        LaunchConfigurationName=ecsLaunchConfigurationName,
        MinSize=1,
        MaxSize=instanceNumber,
        DesiredCapacity=instanceNumber,
        LoadBalancerNames=[
            ecsLoadBalancerName
        ],
        VPCZoneIdentifier=subnetId
    )
except ClientError as e:
    if e.response['Error']['Code'] != 'AlreadyExists':
        print(e)

print("Creating S3 bucket")
s3 = boto3.resource('s3')
try:
    s3.Bucket(ecsS3BucketName).create(
        ACL='private',
        CreateBucketConfiguration={'LocationConstraint': 'us-west-2'}
    )
except ClientError as e:
    if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
        print(e)

print("Creating S3 user")
iam = boto3.resource('iam')
try:
    response = iam.User(ecsS3UserName).create()
except ClientError as e:
    if e.response['Error']['Code'] != 'EntityAlreadyExists':
        print(e)

print("Granting GET, PUT, DELETE to S3 user")
ecsS3UserPolicy = '''{
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::%s"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::%s/*"
            ]
        }
    ]
}''' % (ecsS3BucketName, ecsS3BucketName)

try:
    iam.User(ecsS3UserName).create_policy(
        PolicyName=namePrefix + 'S3Policy',
        PolicyDocument=ecsS3UserPolicy
    )
except ClientError as e:
    print(e)

print("Creating deploy application")
codedeploy = boto3.client('codedeploy')
try:
    codedeploy.create_application(applicationName=ecsDeployApplicationName)
except ClientError as e:
    if e.response['Error']['Code'] != 'ApplicationAlreadyExistsException':
        print(e)

print("Creating deployment group")
try:
    codedeploy.create_deployment_group(
        applicationName=ecsDeployApplicationName,
        deploymentGroupName='Staging',
        deploymentConfigName='CodeDeployDefault.OneAtATime',
        autoScalingGroups=[
            ecsAutoScalingGroupName
        ],
        serviceRoleArn='arn:aws:iam::410538873633:role/CodeDeployServiceRole',
        autoRollbackConfiguration={
            'enabled': False
        }
    )
except ClientError as e:
    if e.response['Error']['Code'] != 'DeploymentGroupAlreadyExistsException':
        print(e)

print("Deploying application")
try:
    codedeploy.create_deployment(
        applicationName=ecsDeployApplicationName,
        deploymentGroupName='Staging',
        revision={
            'revisionType': 'S3',
            's3Location': {
                'bucket': 'task3-bucket',
                'key': 'sample-application.zip',
                'bundleType': 'zip'
            }
        },
        deploymentConfigName='CodeDeployDefault.OneAtATime',
        ignoreApplicationStopFailures=False,
        autoRollbackConfiguration={
            'enabled': False
        },
        updateOutdatedInstancesOnly=False
    )
except ClientError as e:
    print(e)

print("Creating ECR repository")
ecr = boto3.client('ecr')
try:
    ecr.create_repository(repositoryName=ecsRepositoryName)
except ClientError as e:
    if e.response['Error']['Code'] != 'RepositoryAlreadyExistsException':
        print(e)
