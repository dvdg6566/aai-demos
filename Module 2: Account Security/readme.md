# Module Demonstration 2: Account Security

*S3 bucket as main access control indicator*

## Setup

*just use a Python script that can help generate the policies in JSON files*

- Create 2 S3 buckets named `-development` and `-finance`
- Upload default objects into the S3 buckets.
- Create a Lambda function that performs an audit by listing all the files in the various S3 buckets.

## Demonstrations

- Create an IAM User with the `AmazonS3ReadOnlyAccess`
    - Login as the IAM user (mention the different possible configurations like 2FA, access keys, management console access)
    - Demonstrate being able to access the S3 bucket, but not being able to upload objects.
    - Demonstrate still being able to upload objects from the root user account.
- IAM role: Demo how to attach policies to IAM roles.
    - Demonstrate how the Lambda function does not have permission to run the S3 command.
    - Then open the IAM role for the Lambda function and attach the `AmazonS3ReadOnlyAccess` role to the Lambda function.
    - Also mention that the Lambda function can’t be invoked from the IAM user since we didn’t grant it permissions.
- Create an IAM policy that grants read and write permissions to the `-development` bucket
    - Update that IAM user to use our policy instead
    - Assume that IAM user and show how you are able to access the `-development` bucket but not the `-finance` bucket.
- Resource-based policy
    - Attach a resource-based policy that only allows access to the bucket from the Lambda function.
    - We would no longer be able to access the S3 buckets’ contents from the IAM user account, but still be able to access the bucket contents by executing the Lambda function.
- If in organization, attach SCP to OU in organization
- Identity Federation???

## Cleanup

- Remove any IAM users, roles or policies that begin with `demo-`
- Remove any S3 buckets that begin with `demo-`
- Remove any AWS Lambda functions that begin with `demo-`