import json
import logging

import boto3
import urllib3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    try:
        arn = event["SecretId"]
        token = event["ClientRequestToken"]
        client = boto3.client("secretsmanager")
        metadata = client.describe_secret(SecretId=arn)
        if not metadata["RotationEnabled"]:
            raise ValueError("Secret %s is not enabled for rotation" % arn)
        versions = metadata["VersionIdsToStages"]
        if token not in versions:
            raise ValueError(
                "Secret version %s has no stage for rotation of secret %s."
                % (token, arn)
            )
        if "AWSCURRENT" in versions[token]:
            logger.info(
                "Secret version %s already set as AWSCURRENT for secret %s."
                % (token, arn)
            )
            return
        if "AWSPENDING" not in versions[token]:
            raise ValueError(
                "Secret version %s not set as AWSPENDING for rotation of secret %s."
                % (token, arn)
            )
        step_handlers[event["Step"]](client, arn, token)
    except Exception as ex:
        logging.exception(
            ex, f"Exception processing event: {event} with context: {context}"
        )
        raise


def create_secret(client, arn, token):
    client.get_secret_value(SecretId=arn, VersionStage="AWSCURRENT")
    try:
        client.get_secret_value(
            SecretId=arn, VersionId=token, VersionStage="AWSPENDING"
        )
        logger.info("createSecret: Successfully retrieved secret for %s." % arn)
    except client.exceptions.ResourceNotFoundException:
        iot = boto3.client("iot")
        response = iot.create_keys_and_certificate(setAsActive=True)
        secret = {
            "certificateArn": response["certificateArn"],
            "certificateId": response["certificateId"],
            "certificate": response["certificatePem"],
            "publicKey": response["keyPair"]["PublicKey"],
            "privateKey": response["keyPair"]["PrivateKey"],
        }
        client.put_secret_value(
            SecretId=arn,
            ClientRequestToken=token,
            SecretString=json.dumps(secret),
            VersionStages=["AWSPENDING"],
        )
        logger.info(
            "createSecret: Successfully put secret for ARN %s and version %s."
            % (arn, token)
        )


def set_secret(client, arn, token):
    pass


def test_secret(client, arn, token):
    pass


def finish_secret(client, arn, token):
    metadata = client.describe_secret(SecretId=arn)
    current_version = None
    for version in metadata["VersionIdsToStages"]:
        if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
            current_version = version
            break
    if current_version == token:
        logger.info(
            "finishSecret: Version %s already marked as AWSCURRENT for %s"
            % (version, arn)
        )
        return
    old_value = json.loads(
        client.get_secret_value(SecretId=arn, VersionStage="AWSCURRENT")["SecretString"]
    )
    # Set the new cert as current
    client.update_secret_version_stage(
        SecretId=arn,
        VersionStage="AWSCURRENT",
        MoveToVersionId=token,
        RemoveFromVersionId=current_version,
    )
    logger.info(
        f"finishSecret: Successfully set AWSCURRENT stage to version {token} for secret {arn}"
    )
    # Signal Cloudformation if required
    logger.info(f"finishSecret: {old_value}")
    if "waitHandle" in old_value:
        logger.info(f'signalling: {old_value["waitHandle"]}')
        urllib3.PoolManager().request(
            "PUT",
            old_value["waitHandle"],
            headers={"Conent-Type": ""},
            body=json.dumps(
                {"Status": "SUCCESS", "UniqueId": "1", "Data": "", "Reason": ""}
            ).encode("utf-8"),
        )
    # Deactivate the old cert
    if "certificateId" in old_value:
        iot = boto3.client("iot")
        iot.update_certificate(
            certificateId=old_value["certificateId"], newStatus="INACTIVE"
        )


step_handlers = {
    "createSecret": create_secret,
    "setSecret": set_secret,
    "testSecret": test_secret,
    "finishSecret": finish_secret,
}
