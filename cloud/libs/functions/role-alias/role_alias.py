import logging

import boto3
import cfnresponse


def handler(event, context):
    logging.getLogger().setLevel(logging.INFO)
    logging.info(f"Processing event: {event} | with context: {context}")
    result, data, id = cfnresponse.FAILED, {}, None
    try:
        request_type = event["RequestType"]
        alias = event["ResourceProperties"]["Alias"]
        role = event["ResourceProperties"]["Role"]
        client = boto3.client("iot")
        if request_type == "Create":
            data = client.create_role_alias(roleAlias=alias, roleArn=role)
            id = data["roleAliasArn"]
        elif request_type == "Update":
            data = client.update_role_alias(roleAlias=alias, roleArn=role)
            id = data["roleAliasArn"]
        elif request_type == "Delete":
            data = client.delete_role_alias(roleAlias=alias)
        result = cfnresponse.SUCCESS
    except Exception as ex:
        logging.exception(ex)
    cfnresponse.send(event, context, result, data, id)
