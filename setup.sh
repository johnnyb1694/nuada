#!/bin/bash

echo "**** Running AWS Lambda Setup ****"
if [[ $# -eq 0 ]] ; then
    echo 'Please enter your bucket name as an additional argument i.e. `sh setup.sh {BUCKET_NAME}` (where {BUCKET_NAME} is your chosen bucket name)'
    exit 1
fi

echo "** Stage 0: Preliminary stage to configure virtual environment for deployment **"
cd ./venv/lib/python3.10/site-packages
zip -rq ../../../../staging/lambda-data-upload.zip .
cd ../../../..

echo "** Stage 1: Retrieving AWS credentials **"
AWS_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)

echo "** Stage 2: Packaging 'data-upload' functionality **"
cd ./data-upload
zip ../staging/lambda-data-upload.zip staging lambda_function.py
cd ..

echo "** Stage 3: Creating S3 bucket with alias "$1" **"
aws s3api create-bucket --bucket $1 --create-bucket-configuration LocationConstraint=us-east-2 --output text > logs/setup.log

echo "** Stage 4: Creating relevant policy (permissions) for AWS Lambda **"
aws iam create-policy --policy-name lambda-s3-policy --policy-document file://aws/policy.json --output text >> logs/setup.log

echo "** Stage 5: Creating relevant role for AWS Lambda **"
aws iam create-role --role-name lambda-s3-role --assume-role-policy-document file://aws/trust-policy.json --output text >> logs/setup.log

echo "** Stage 6: Attaching policy (permissions) to newly created role **"
aws iam attach-role-policy --role-name lambda-s3-role --policy-arn arn:aws:iam:$AWS_REGION:$AWS_ID:policy/lambda-s3-policy --output text >> logs/setup.log

echo "** Stage 7: Sleeping 10 seconds to allow policy to attach to role **"
sleep 10s

echo "** Stage 8: Creating Lambda function **"
aws lambda create-function --function-name nuada-data-upload \
    --runtime python3.10 \
    --role arn:aws:iam::$AWS_ID:role/lambda-s3-role \
    --zip-file fileb://staging/lambda-data-upload.zip \
    --handler lambda_function.lambda_handler \
    --timeout 60 \
    --output text >> logs/setup.log

rm -r staging/lambda-data-upload.zip

echo "** Stage 9: Adding API key(s) as Lambda environment variables **"
aws lambda update-function-configuration --function-name nuada-data-upload \
    --environment Variables="{SOURCE_KEY_NYT=$SOURCE_KEY_NYT}" \
    --output text >> logs/setup.log

# echo "** Stage 10: Creating event rule to schedule execution of Lambda expression on a regular basis **"
# aws events put-rule --name nuada-data-upload-schedule \
#   --schedule-expression 'rate(30 minutes)' \
#   --output text >> logs/setup.log

# echo "** Stage 11: Attaching Lambda function to event **"
# aws lambda add-permission --function-name nuada-data-upload \
#    --statement-id nuada-schedule \
#    --action lambda:InvokeFunction \
#    --principal events.amazonws.com \
#    --source-arn arn:aws:events:$AWS_REGION:$AWS_ID:rule/nuada-data-upload-schedule \
#    --output text >> logs/setup.log

#echo "** Stage 12: Assigning function target to rule **"
# aws events put-targets --rule nuada-data-upload-schedule \
#    --targets file://aws/targets.json \
#    --output text >> logs/setup.log

    





