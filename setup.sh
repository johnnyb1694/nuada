#!/bin/bash

echo "**** Running AWS Lambda Setup ****"
if [[ $# -eq 0 ]] ; then
    echo 'Please enter your bucket name as an additional argument i.e. `sh setup.sh {BUCKET_NAME}` (where {BUCKET_NAME} is your chosen bucket name)'
    exit 1
fi

echo "** Stage 1: Retrieving AWS credentials **"
AWS_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)

echo "** Stage 2: Packaging local lambda_function.py **"
cd data-upload
zip -r ../data-upload.zip lambda_function.py
cd ..

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
    --zip-file fileb://data-upload.zip \
    --handler lambda_function.lambda_handler \
    --timeout 60 \
    --output text >> setup.log





