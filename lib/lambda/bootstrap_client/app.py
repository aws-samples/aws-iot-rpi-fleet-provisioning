# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

import boto3
import json
import logging
import zipfile
import io

CERTS_FOLDER = 'aws-iot-fleet-provisioning/certs'
CERT_FILENAME = 'bootstrap-certificate.pem.crt'
KEY_FILENAME = 'bootstrap-private.pem.key'
CONFIG_LOCATION = 'aws-iot-fleet-provisioning/config.ini'

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')
iot_client = boto3.client('iot')


def get_iot_endpoint():
    result = iot_client.describe_endpoint(
        endpointType='iot:Data-ATS'
    )
    return result['endpointAddress']


def create_provisioning_client_config(provisioning_template_name):
    return f"""[SETTINGS]
# Set the path to the location containing your certificates (root, private, claim certificate)
SECURE_CERT_PATH = ./certs

# Specify the names for the root cert, provisioning claim cert, and the private key.
ROOT_CERT = root.ca.pem
CLAIM_CERT = {CERT_FILENAME}
SECURE_KEY = {KEY_FILENAME}

# Set the name of your IoT Endpoint
IOT_ENDPOINT = {get_iot_endpoint()}

# Include the name for the provisioning template that was created in IoT Core
PRODUCTION_TEMPLATE = {provisioning_template_name}
# TODO: Implement cert rotation
CERT_ROTATION_TEMPLATE = dummy-template-name
"""


def create_provisioning_client_archive(
    bootstrap_certificates,
    config,
    provisioning_artifacts_bucket_name,
    provisioning_client_bucket_name,
    provisioning_client_object_key,
    provisioning_client_archive_name,
):

    logger.info("Downloading client code")
    provisioning_client_object = s3_client.get_object(
        Bucket=provisioning_client_bucket_name,
        Key=provisioning_client_object_key,
    )

    with io.BytesIO(provisioning_client_object['Body'].read()) as tf:
        # rewind the file
        tf.seek(0)

        logger.info("Adding bootstrap certificates and configuration to client code")
        with zipfile.ZipFile(tf, mode='a') as zipf:
            zipf.writestr(f'{CERTS_FOLDER}/{CERT_FILENAME}',
                          bootstrap_certificates['certificatePem'])
            zipf.writestr(f'{CERTS_FOLDER}/{KEY_FILENAME}',
                          bootstrap_certificates['keyPair']['PrivateKey'])
            zipf.writestr(CONFIG_LOCATION, config)

        # rewind the file
        tf.seek(0)

        logger.info("Uploading client to s3")
        s3_client.put_object(
            Bucket=provisioning_artifacts_bucket_name,
            Key=provisioning_client_archive_name,
            Body=tf
        )


def create_provisioning_client(
    bootstrap_policy_name,
    provisioning_artifacts_bucket_name,
    provisioning_template_name,
    provisioning_client_bucket_name,
    provisioning_client_object_key,
    provisioning_client_archive_name,
):
    """
    1/ Create bootstrap certificates and provisioning client config
    2/ Download the provisioning client
    3/ Inject config and bootstrap certificates in provisioning client
    4/ Upload configured provisioning client to S3
    """
    logger.info("Generating bootstrap certificate")
    bootstrap_certificates = iot_client.create_keys_and_certificate(
        setAsActive=True,
    )

    logger.info("Attaching bootstrap policy to certificate")
    iot_client.attach_policy(
        policyName=bootstrap_policy_name,
        target=bootstrap_certificates['certificateArn'],
    )

    logger.info("Creating provisioning client config")
    config = create_provisioning_client_config(provisioning_template_name)

    logger.info(f"Creating provisioning client archive")
    create_provisioning_client_archive(
        bootstrap_certificates,
        config,
        provisioning_artifacts_bucket_name,
        provisioning_client_bucket_name,
        provisioning_client_object_key,
        provisioning_client_archive_name,
    )


def on_event(event, context):
    logger.info(f'New event {json.dumps(event, indent=2)}')

    bootstrap_policy_name = event['ResourceProperties']['BOOTSTRAP_POLICY_NAME']
    provisioning_artifacts_bucket_name = event['ResourceProperties']['PROVISIONING_ARTIFACTS_BUCKET_NAME']
    provisioning_template_name = event['ResourceProperties']['PROVISIONING_TEMPLATE_NAME']
    provisioning_client_bucket_name = event['ResourceProperties']['PROVISIONING_CLIENT_BUCKET_NAME']
    provisioning_client_object_key = event['ResourceProperties']['PROVISIONING_CLIENT_OBJECT_KEY']
    provisioning_client_archive_name = event['ResourceProperties']['PROVISIONING_CLIENT_ARCHIVE_NAME']

    request_type = event['RequestType']
    if request_type == 'Create' or request_type == 'Update':
        create_provisioning_client(
            bootstrap_policy_name,
            provisioning_artifacts_bucket_name,
            provisioning_template_name,
            provisioning_client_bucket_name,
            provisioning_client_object_key,
            provisioning_client_archive_name,
        )
    elif request_type == 'Delete':
        logger.info("Bootstrap config deletion")
        # We could remove the client from the bucket here
        pass
    else:
        raise Exception("Invalid request type: %s" % request_type)
