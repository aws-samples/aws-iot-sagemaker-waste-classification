#!/usr/bin/env bash

#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: MIT-0

mkdir -p /greengrass/v2/
chmod 755 /greengrass/

mv -f certs/ /greengrass/v2/

rm -rf install/
unzip greengrass-nucleus.zip -d install/

sudo -E java -Droot="/greengrass/v2" -Dlog.store=FILE \
  -jar ./install/lib/Greengrass.jar \
  --trusted-plugin ./aws.greengrass.FleetProvisioningByClaim.jar \
  --init-config ./config.yml \
  --component-default-user root:root \
  --setup-system-service true
