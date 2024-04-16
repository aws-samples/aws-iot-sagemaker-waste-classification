#!/usr/bin/env bash

#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: MIT-0

if [ -z "$2" ]; then
    echo "Usage: ./ci/fleet_provisioning_of_greengrass.sh <STACK_NAME> <AWS_REGION> <THING_NAME> <LOCATION> <THING_SERIAL_NO> <GREENGRASS_VERSION>"
    exit 1
else
  STACK_NAME="$1"
  AWS_REGION="$2"
  THING_NAME=$([ -z "$3" ] && echo "DemoWasteBin")
  LOCATION=$([ -z "$4" ] && echo "London")
  THING_SERIAL_NO=$([ -z "$5" ] && echo "W123")
  GG_VERSION=$([ -z "$6" ] && echo "2.11.2")
fi

mkdir -p ./build/certs/
curl -o ./build/certs/AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem

chmod 745 build
chmod 700 build/certs
chmod 644 build/certs/AmazonRootCA1.pem

# Retrieve provisioning certificates from secrets manager
SECRET_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$AWS_REGION" --query "Stacks[0].Outputs[?OutputKey=='CertificateSecret'].OutputValue" --output text)
SECRET=$(aws secretsmanager get-secret-value --secret-id "$SECRET_ARN" | jq -r '.SecretString')
jq --arg s "$SECRET" -jn '$s | fromjson | .certificate' > build/certs/cert.pem
jq --arg s "$SECRET" -jn '$s | fromjson | .privateKey' > build/certs/privateKey.pem


# Download the greengrass runtime and plugins
#GG_VERSION='2.4.0'
#GG_VERSION='2.5.4'
curl -s https://d2s8p88vqu9w66.cloudfront.net/releases/greengrass-$GG_VERSION.zip > build/greengrass-nucleus.zip
curl -s https://d2s8p88vqu9w66.cloudfront.net/releases/aws-greengrass-FleetProvisioningByClaim/fleetprovisioningbyclaim-latest.jar > build/aws.greengrass.FleetProvisioningByClaim.jar

DATA_ENDPOINT=$(aws iot describe-endpoint --endpoint-type iot:Data-ATS --output text)
CREDENTIALS_ENDPOINT=$(aws iot describe-endpoint --endpoint-type iot:CredentialProvider --output text)
TEMPLATE_NAME=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$AWS_REGION" --query "Stacks[0].Outputs[?OutputKey=='FleetProvisioningTemplate'].OutputValue" --output text)
IOT_CORE_ROLE_ALIAS=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --region "$AWS_REGION" --query "Stacks[0].Outputs[?OutputKey=='IoTCoreRoleAlias'].OutputValue" --output text)
ROOT='/greengrass/v2'

cat >build/config.yml <<EOF
---
services:
  aws.greengrass.Nucleus:
    version: $GG_VERSION
    configuration:
      awsRegion: $AWS_REGION
  aws.greengrass.FleetProvisioningByClaim:
    configuration:
      rootPath: $ROOT/
      awsRegion: $AWS_REGION
      iotDataEndpoint: $DATA_ENDPOINT
      iotCredentialEndpoint: $CREDENTIALS_ENDPOINT
      iotRoleAlias: $IOT_CORE_ROLE_ALIAS
      provisioningTemplate: $TEMPLATE_NAME
      claimCertificatePath: $ROOT/certs/cert.pem
      claimCertificatePrivateKeyPath: $ROOT/certs/privateKey.pem
      rootCaPath: $ROOT/certs/AmazonRootCA1.pem
      templateParameters:
        ThingName: $THING_NAME
        Location: $LOCATION
        SerialNumber: $THING_SERIAL_NO
EOF

cp ./fleet_provision.sh build/
chmod 755 ./build/fleet_provision.sh
