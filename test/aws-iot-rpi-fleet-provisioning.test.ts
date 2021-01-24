/*
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy of this
 * software and associated documentation files (the "Software"), to deal in the Software
 * without restriction, including without limitation the rights to use, copy, modify,
 * merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
 * INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
 * PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
 * HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

import * as cdk from '@aws-cdk/core';
import { AwsIotRpiFleetProvisioningStack, AwsIotRpiFleetProvisioningStackProps } from '../lib/aws-iot-rpi-fleet-provisioning-stack';
import { SynthUtils } from '@aws-cdk/assert';

test('snapshot test fleet provisioning stack', () => {
  const app = new cdk.App();

  const props: AwsIotRpiFleetProvisioningStackProps = {
    sshPublicKey: 'ssh-rsa ....',
    wifiCountry: 'US',
    wifiPasswordSecretName: 'RPI_WIFI_PASSWORD',
    wifiSsid: 'samplewifi',
  };

  const stack = new AwsIotRpiFleetProvisioningStack(app, 'TestStack', props);

  expect(SynthUtils.toCloudFormation(stack)).toMatchSnapshot();
});
