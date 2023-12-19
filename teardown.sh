#!/bin/bash

echo "**** Running AWS Lambda Setup ****"
if [[ $# -eq 0 ]] ; then
    echo 'Please enter your bucket name as an additional argument i.e. `sh setup.sh {BUCKET_NAME}` (where {BUCKET_NAME} is your chosen bucket name)'
    exit 1
fi

AWS_ID=$(aws sts get-caller-identity --query Account --output text)

echo "** Stage 1: Removing Lambda function & associated scheduling **"
aws lambda delete-function --function-name nuada-data-upload --output text > logs/teardown.log
aws events remove-targets --rule nuada-data-upload-schedule --ids "1" --output text >>  logs/teardown.log
aws events delete-rule --name nuada-data-upload-schedule --output text >> logs/teardown.log

echo "** Stage 2: Deleting associated IAM role and attached policy **"
aws iam detach-role-policy --role-name AWSLambdaS3Role --policy-arn arn:aws:iam::$AWS_ID:policy/AWSLambdaS3Access --output text >> logs/teardown.log
aws iam delete-role --role-name AWSLambdaS3Role --output text >> logs/teardown.log
aws iam delete-policy --policy-arn arn:aws:iam::$AWS_ID:policy/AWSLambdaS3Access --output text >> logs/teardown.log

echo "** Stage 3: Deleting bucket "$1""
aws s3 rm s3://$1 --recursive --output text >> logs/teardown.log
aws s3api delete-bucket --bucket $1 --output text >> logs/teardown.log

echo "** Stage 4: Removing local configuration / logging files **"
rm ./aws/targets.json
rm ./logs/setup.log
