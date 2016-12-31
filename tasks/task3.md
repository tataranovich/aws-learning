# Task 3

## python 2.7 + boto3

Use boto3 to create AWS resources below:

 1. ECS-cluster (minimum 2 instances).
 2. Load Balancer for the cluster from step 1.
 3. S3 bucket and user for it. (Get, Delete, Put object permissions)
 4. Implement deployment process for any simple application, please use CodeDeploy AWS service. 

## Optional

 - Use AWS Lambda service for deployment.
 - Create generic deployment template. (Jinja engine)
 - ECR for storing your images if you are going to create Docker containers for your application.
 - Create EFS volume and mount on each instance from cluster.

## Note 

Do not use Cloud Formation service.