# aai-demos
Collection of setup and demonstration scripts for the Architecting on AWS (AoA) module for the Instructor Candidate Assessment (ICA)

## Module 01: Management Console Tour

Demonstrate overview of AWS Console

- Explain top bar: Console home, searching for services, Cloud Shell, Region and Account ID
- Show homepage: Recently visited, cost and usage
- Open example service: EC2
    - Show the different functionalities (like how to launch EC2 servers or ASGs etc.)
    - Show affiliated/related services (Security groups, Load balancers etc.)
- Open example service: S3
    - Show buckets, create bucket functionality, ability to enter bucket and list items.
- Show billing and cost management
    - Talk about how AWS is pay-per-use and that you’re only charged for the time your services are in use (as compared to investing large amounts into physical infrastructure)

## Module 02: Creating an IAM User and an IAM Role

- In console, mention that IAM is a global service
- Create an IAM User with the `AmazonS3ReadOnlyAccess` AWS-managed policy
    - Set username as `demouser01`, password as `Testpassword123!`
    - Login as the IAM user (mention the different possible configurations like 2FA, access keys, management console access)
    - Demonstrate being able to access the S3 bucket, but not being able to upload objects.
    - Demonstrate still being able to upload objects from the root user account.
- IAM role: Demo how to attach policies to IAM roles.
    - Demonstrate how the Lambda function does not have permission to run the S3 command.
    - Then open the IAM role for the Lambda function and attach the `AmazonS3ReadOnlyAccess` AWS-managed policy to the Lambda function’s execution role.
    - Also mention that the Lambda function can’t be invoked from the IAM user since we didn’t grant it permissions.
        - Show the trust policy of the Lambda function role and mention that the trust policy allows only Lambda to use it (and you can’t just have someone assume the role of your Lambda function)

## Module 02: IAM Policies

- Create an IAM policy that grants read and write permissions to the `-development` bucket (can be found in `iam_policy.json`)
    - Call the policy `demo-policy`.
    - Update that IAM user to use our policy instead
    - Using the IAM user, show how you are able to access the `-development` bucket
    - However, you still can’t upload files into the `-finance` bucket.

## Module 03: Security Groups

Security group demo: Deploy EC2 instance with web application

- Add a security group rule to allow inbound traffic on port 80

Demonstrate stateful/stateless traffic restrictions using a security group and a NACL

- Initially, the traffic is not explicitly allowed or denied by NACL or security group
    - When we attempt to ping [`amazon.com`](http://amazon.com), we aren’t able to connect
    - Add security group rule (allow ICMP traffic) to allow all outbound traffic
- However, we still can’t ping/communicate to our other instance
    - Add security group rule to allow inbound ICMP traffic from the same security group
    - We can now perform our ping to our other instance
- Show NACLs and mention how the rules would be set up (but don’t need to demo)

## Module 04: Launching an EC2 Instance

- Launch EC2 instance — launch using the Amazon Linux 02
    - Can show searching for custom OS like Kali linux in the marketplace
    - Can show the different types of AMIs (Quickstart, custom, marketplace, community)
    - User Data: Set up user data and show the webpage deployed
        - [https://github.com/dvdg6566/aai-demos/blob/main/Module 4 - Compute/sample-userdata.sh](https://github.com/dvdg6566/aai-demos/blob/main/Module%204%20-%20Compute/sample-userdata.sh)
- Demonstrate accessing metadata commands
    - Now requires 2 requests, first to get the `api token` and then second to get the actual request using the API token.

```bash
curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/
curl -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/public-ipv4
```

## Module 04: AWS Lambda

Lambda: Demonstrate the creation and running of a Lambda function

- Show example Lambda usage graph (see: Singapore Zoo AWS Account) and IAM logs
- Show different configurations (time, memory, IAM role, triggers, layers)
- After executing the Lambda function, can show the CloudWatch logs in the `monitor` tab.

## Module 05: S3 and S3 Versioning

- Create an S3 bucket
    - Go through the console and show the different S3 features (i.e. resource policy, versioning, lifecycle policy, SSE-KMS, Replication)
    - Upload an object to the S3 bucket
    - Attempt to open the URL for one of the objects (this should fail and result in an error message being depicted)
- Demonstrate S3 versioning
    - Upload the new version, show the application updates and show the different versions visible in the S3 console.

## Module 06: DynamoDB

- Show a sample database with DynamoDB data (Use `codebreaker-submissions` table)
    - View an object in the database and demonstrate the kind of data types that are allowed (i.e. list, dictionary, string, datetime, etc.)
    - Show the secondary indexes and briefly mention how they act as supplementary keys for key-value lookups
- Show example DynamoDB usage graph

## Module 07: CloudWatch

- Create CloudWatch Dashboard of live application (Codebreaker)
    - Try to spread out with different services (DynamoDB, EC2, Lambda) and different types of graph (Pie chart, logs, line graph)
    - Line graph of concurrent Executions of `codebreaker-grading-v2`
    - Pie chart of CPU utilisation of `codebreaker` EC2 instance
    - Line graph of read/write capacity units of `codebreaker-submissions`
    - Line graph of errors across ALL lambda functions
    - Log group for `/aws/lambda/codebreaker-testcase-grader`

## Module 07: CloudTrail

- CloudTrail: Go to the console and go through the overall events
    - Open two of the events and discuss the agents (try to show one for management console and one that is programmatic)

## Module 08: CloudFormation

Main template: [aai-demos/Module 8 - Automation/template.yml at main · dvdg6566/aai-demos · GitHub](https://github.com/dvdg6566/aai-demos/blob/main/Module%208%20-%20Automation/template.yml)

- Demonstrate deploying a CloudFormation stack (Create CF stack in console)
    - Set the parameter ()
    - Show the CloudFormation console (where it show the event logs and the resources tabs)
    - Show the created S3 bucket.
    - Once the stack is complete, get the Elastic IP from the Outputs tab to show running application
- Once you’ve executed the main stack, launch the failstack `fail.yml`.
- This can be done during the deployment of the main CloudFormation stack has began, and the bucket is already created.
- Deployment should fail since the bucket called `AppName-070824-documents` already exists.
    - Show the logs and error message, then demonstrate rollback and deletion of all resources.
    - Intended error message: `demo-070824-documents already exists in stack <CFstack>`

## Module 09: Elastic Container Service

- Show ECR console and basic outline of container (Dockerfile, `app.py`)
- Create ECR Cluster
- Create task definition for webserver container task
    - Name: `webapp`
    - Image URI: `533267019286.dkr.ecr.ap-southeast-1.amazonaws.com/demo-repository:latest`
    - Port mapping from 8000 to port 8000
- Create ECR Service
    - Specify family `demo-family`
    - After creating the service, go to `configuration and networking` and show that the ECS is created with CloudFormation and features like network configuration and VPCs
    - ALLOW inbound traffic from `0.0.0.0` on port 8000 for the security group
- Go into the demoservice —> Tasks —> container details —> network bindings —>open address

## Module 10: VPC Endpoints

- Execute Lambda function: the function should timeout since it cannot make the required connection
- Create endpoint — have it automatically create entries in the route table, then show the generated route table
    - Select “AWS Services”
    - Managed `pl` prefix list — public IP addresses to interact with AWS services (regionally specific) [select the S3 one for gateway endpoint]
    - Select main route table
    - Select Full access policy (don’t need to configure endpoint policy)
        - Can use `aws:SourceVpce` condition in the policy
- Use Lambda function to display objects in the bucket

## Module 11: API Gateway + AWS Lambda

*Setup: Creates 2 AWS Lambda functions with different return values.* 

- Use API Gateway to invoke a Lambda function
- Go to API Gateway console and create a new HTTP API (mention the alternative options) called `demo-api-gateway`
    - Start without creating any routes or stages
- Create a route for `/home` and attach the integration to the home demonstration function
- Create route for `/side` and attach integration to the secondary demo function
    - Remember to create a NEW integration so the 2 don’t get mixed up
- Visit the default endpoint and show `/home` and `/side`
- If have time, can show Lambda in CloudWatch to show the Lambda functions being executed

## Module 11: State Machines

- Use production account and show the State Machine diagram for grading infrastructure
    - Highlight the logic flow areas (based on the Lambda response) as well as the Parallel processing areas in the diagram.
    - Mention that the diagram is generated based on the `asl (amazon states lang) json` file and is dynamically update to ease development.

## Module 12: CloudFront

*Setup: Create S3 bucket with `index.html` and `script.js`.*

*Remember to use incognito or the JavaScript may not render*

Create a CloudFront distribution

- Select the origin domain to be the created S3 bucket (`demo{prefix}`)
- Select origin access control settings (recommended) and create new OAC. When prompted, just leave the default settings.
    - OAC allows CloudFront to access the files in your S3 bucket while keeping the S3 bucket private.
- Enable redirect HTTP to HTTPS
- Don’t enable WAF
- While waiting for deploying, can go to settings and mention some of the features (i.e. by default Use all edge locations for best performance)
- Show the invalidations page (though don’t need to demo invalidation)