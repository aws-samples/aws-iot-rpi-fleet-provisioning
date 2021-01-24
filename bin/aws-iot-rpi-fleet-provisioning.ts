#!/usr/bin/env node
// Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
// SPDX-License-Identifier: Apache-2.0

import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { AwsIotRpiFleetProvisioningStack } from '../lib/aws-iot-rpi-fleet-provisioning-stack';

import { CONFIG } from '../lib/utils/constants';

const app = new cdk.App();
new AwsIotRpiFleetProvisioningStack(app, 'AwsIotRpiFleetProvisioningStack', {
    wifiPasswordSecretName: CONFIG.wifiPasswordSecretName,
    sshPublicKey: CONFIG.sshPublicKey,
    wifiCountry: CONFIG.wifiCountry,
    wifiSsid: CONFIG.wifiSsid,
});
