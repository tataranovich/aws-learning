# Based on MCS-933

 - Create ECS cluster with 2 EC2 micro instances (create CloudFormation template from scratch)

 - Create IAM Role with permissions to create ECR repositories, push/pull permissions, manage ECS tasks and services and setup
Cloudformation stacks, ElasticCache instances setup, call corresponding AWS Lambda functions

 - Create ECR repo

 - Create EFS volume and mount it to /www/ in both instances