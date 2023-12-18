#!/bin/bash

echo "**** Running AWS Lambda Setup ****"
if [[ $# -eq 0 ]] ; then
    echo 'Please enter your bucket name as an additional argument i.e. `sh setup.sh {BUCKET_NAME}` (where {BUCKET_NAME} is your chosen bucket name)'
    exit 1
fi

echo "** Stage 1: Retrieving AWS credentials **"
AWS_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)

echo "** Stage 2: Packaging 'data-upload' functionality **"
cd ./nuada/data-upload
zip -r ../../lambda-data-upload.zip lambda_function.py
cd ../..

echo "** Stage 3: Creating S3 bucket with alias "$1" **"
aws s3api create-bucket --bucket $1 --create-bucket-configuration LocationConstraint=us-east-2 --output text > setup.log

echo "** Stage 4: Creating relevant policy (permissions) for AWS Lambda **"
aws iam create-policy --policy-name lambda-s3-policy --policy-document file://aws/policy.json --output text >> setup.log

echo "** Stage 5: Creating relevant role for AWS Lambda **"
aws iam create-role --role-name lambda-s3-role --assume-role-policy-document file://aws/trust-policy.json --output text >> setup.log

echo "** Stage 6: Attaching policy (permissions) to newly created role **"
aws iam attach-role-policy --role-name lambda-s3-role --policy-arn arn:aws:iam:$AWS_REGION:$AWS_ID:policy/lambda-s3-policy --output text >> setup.log

echo "** Stage 7: Sleeping 10 seconds to allow policy to attach to role **"
sleep 10s

echo "** Stage 8: Creating Lambda function **"
aws lambda create-function --function-name nuada-data-upload \
    --runtime python3.10 \
    --role arn:aws:iam:$AWS_REGION:$AWS_ID:role/lambda-s3-role \
    --zip-file fileb://lambda-data-upload.zip \
    --handler lambda_function.lambda_handler \
    --timeout 60 \
    --output text >> setup.log

echo "** Stage 9: Creating event rule to schedule execution of Lambda expression on a regular basis **"
aws events put-rule --name nuada-data-upload-schedule \
    --schedule-expression 'rate(30 minutes)' \
    --output text >> setup.log

echo "** Stage 10: Attaching Lambda function to event **"
aws lambda add-permission --function-name nuada-data-upload \
    --statement-id nuada-schedule \
    --action lambda:InvokeFunction \
    --principal events.amazonws.com \
    --source-arn arn:aws:events:$AWS_REGION:$AWS_ID:rule/nuada-data-upload-schedule \
    --output text >> setup.log

echo "** Stage 11: Assigning function target to rule **"
aws events put-targets --rule nuada-data-upload-schedule \
    --targets file://aws/targets.json \
    --output text >> setup.log

    





