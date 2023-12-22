#!/bin/bash

echo "**** Stage I: Configuring 'data-upload' resources in AWS ****"
if [[ $# -eq 0 ]] ; then
    echo 'Please enter your bucket name as an additional argument i.e. `sh setup.sh {BUCKET_NAME}` (where {BUCKET_NAME} is your chosen bucket name)'
    exit 1
fi

trap remove_staging_files EXIT
remove_staging_files() {
    rm -r staging/*.zip > /dev/null 2>&1
}

echo "** Step 0: Preliminary stage to configure virtual environment for deployment(s) **"
cd ./venv/lib/python3.10/site-packages
zip -rq ../../../../staging/lambda-data-upload.zip .
zip -rq ../../../../staging/lambda-data-transfer.zip .
cd ../../../..

echo "** Step 1: Retrieving AWS credentials **"
AWS_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=$(aws configure get region)

echo "** Step 2: Packaging Lambda function(s) **"
cd ./src
zip ../staging/lambda-data-upload.zip nuada lambda_upload.py
zip ../staging/lambda-data-transfer.zip nuada lambda_transfer.py
cd ..

echo "** Step 3: Creating S3 bucket with alias "$1" **"
aws s3api create-bucket --bucket $1 --create-bucket-configuration LocationConstraint=us-east-2 --output text > logs/setup.log

echo "** Step 4: Creating relevant policy (permissions) for AWS Lambda **"
aws iam create-policy --policy-name AWSLambdaS3Access --policy-document file://aws/policy.json --output text >> logs/setup.log

echo "** Step 5: Creating relevant role for AWS Lambda **"
aws iam create-role --role-name AWSLambdaS3Role --assume-role-policy-document file://aws/trust-policy.json --output text >> logs/setup.log

echo "** Step 6: Attaching policy (permissions) to newly created role **"
aws iam attach-role-policy --role-name AWSLambdaS3Role --policy-arn arn:aws:iam::$AWS_ID:policy/AWSLambdaS3Access --output text >> logs/setup.log

echo "** Step 7: Sleeping 10 seconds to allow policy to attach to role **"
sleep 10s

echo "** Step 8: Creating Lambda function (for 'data upload' purposes) **"
aws lambda create-function --function-name nuada-data-upload \
    --runtime python3.10 \
    --role arn:aws:iam::$AWS_ID:role/AWSLambdaS3Role \
    --zip-file fileb://staging/lambda-data-upload.zip \
    --handler lambda_upload.lambda_handler \
    --timeout 60 \
    --output text >> logs/setup.log

echo "** Step 9: Adding API key(s) as Lambda environment variables **"
aws lambda update-function-configuration --function-name nuada-data-upload \
    --environment Variables="{SOURCE_KEY_NYT=$SOURCE_KEY_NYT}" \
    --output text >> logs/setup.log

echo "** Step 10: Creating event rule to schedule execution of Lambda expression on a regular basis (9am on the first Monday of each month) **"
aws events put-rule --name nuada-data-upload-schedule \
    --schedule-expression 'cron(0 9 ? * 2#1 *)' \ 
    --output text >> logs/setup.log

echo "** Step 11: Attaching Lambda function to event **"
aws lambda add-permission --function-name nuada-data-upload \
    --statement-id nuada-schedule \
    --action lambda:InvokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:$AWS_REGION:$AWS_ID:rule/nuada-data-upload-schedule \
    --output text >> logs/setup.log

echo "** Step 12: Assigning targeted Lambda function (i.e. data upload) to rule **"
echo '[
        {
            "Id": "1",
            "Arn": "arn:aws:lambda:'$AWS_REGION':'$AWS_ID':function:nuada-data-upload"
        }
      ]' > ./aws/targets.json
aws events put-targets --rule nuada-data-upload-schedule \
    --targets file://aws/targets.json \
    --output text >> logs/setup.log

echo "** Step 13: Creating Lambda function (for 'data transfer' purposes) **"
aws lambda create-function --function-name nuada-data-transfer \
    --runtime python3.10 \
    --role arn:aws:iam::$AWS_ID:role/AWSLambdaS3Role \
    --zip-file fileb://staging/lambda-data-transfer.zip \
    --handler lambda_transfer.lambda_handler \
    --timeout 60 \
    --output text >> logs/setup.log

echo "** Step 14: Adding permissions for S3 to invoke data transfer function **"
aws lambda add-permission --function-name nuada-data-transfer \
    --principal s3.amazonaws.com \
    --statement-id nuada-trigger \
    --action lambda:InvokeFunction \
    --source-arn arn:aws:s3:::$1 \
    --source-account $AWS_ID \
    --output text >> logs.setup.log

echo "** Step 15: Setting up S3 trigger for the invocation of the data transfer function **"
echo '{
        "LambdaFunctionConfigurations": [
            {
                "Id": "DataTransferEventConfiguration",
                "LambdaFunctionArn": "arn:aws:lambda:'$AWS_REGION':'$AWS_ID':function:nuada-data-transfer",
                "Events": [ "s3:ObjectCreated:Put" ]
            }
        ]
      }' > ./aws/notification.json
aws s3api put-bucket-notification-configuration --bucket $1 \
    --notification-configuration file://aws/notification.json \
    --output text >> logs/setup.log


    





