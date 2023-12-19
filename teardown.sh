#!/bin/bash

echo "**** Running AWS Lambda Setup ****"
if [[ $# -eq 0 ]] ; then
    echo 'Please enter your bucket name as an additional argument i.e. `sh setup.sh {BUCKET_NAME}` (where {BUCKET_NAME} is your chosen bucket name)'
    exit 1
fi

echo "** Stage 1: Removing Lambda function **"
aws lambda delete-function --function-name nuada-data-upload --output text > logs/teardown.log