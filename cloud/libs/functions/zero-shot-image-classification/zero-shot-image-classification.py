import os
import json
import boto3
from botocore.client import Config
iot_data_client = boto3.client('iot-data')

# grab environment variables
ENDPOINT_NAME = os.environ['INFEREENCE_ENDPOINT_NAME']
REGION_NAME = os.environ['S3_BUCKET_REGION']

client = boto3.client('sagemaker-runtime')
s3 = boto3.client('s3', region_name=REGION_NAME,
                  config=Config(s3={'addressing_style': 'path'}))


def predict(payload):
    response = client.invoke_endpoint(
        EndpointName=ENDPOINT_NAME,
        Body=payload,
        ContentType='application/json')

    response = json.loads(response['Body'].read().decode('utf-8'))

    return response


def invoke_hgf_model(event):

    BUCKET_NAME = event["detail"]["bucket"]["name"]
    KEY = event["detail"]["object"]["key"]

    rekognition_labels = [
        label["Name"]
        for label in event["rekognition"]["Labels"]
    ]

    url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': KEY
        },
        ExpiresIn=604800
    )

    data = {
        "inputs": url,
        "parameters": {'candidate_labels': ["organic", "landfill", "recycle"]}
    }

    payload = json.dumps(data).encode('utf-8')
    response = predict(payload)
    classification = get_item_max_confidence(response)

    labels = {}
    labels['candidate_labels'] = rekognition_labels
    data = {
        "inputs": url,
        "parameters": labels
    }
    payload = json.dumps(data).encode('utf-8')
    response = predict(payload)
    item_label = get_item_max_confidence(response)

    # response = client.invoke_endpoint(
    #     EndpointName=ENDPOINT_NAME,
    #     Body=payload,
    #     ContentType='application/json')

    # response = json.loads(response['Body'].read().decode('utf-8'))

    return classification, item_label


def get_item_max_confidence(payload):
    result = {}
    max = 0
    for item in payload:
        if item['score'] > max:
            max = item['score']
            result['Name'] = item["label"]
            result['Score'] = item['score']
    return result


def updateShadowTopic(result):

    payload = {"state": {
        "desired": {
            "classification": result
        }
    }
    }
    payload = json.dumps(payload).encode('utf-8')
    # client.update_thing_shadow(thingName='DemoWasteBin',payload=payload)
    iot_data_client.publish(topic='$aws/things/DemoWasteBin/shadow/update',
                            qos=0, payload=payload)


def handler(event, context):

    classification, item_label = invoke_hgf_model(event)

    # print("classification:", classification)
    # print("item_label:", item_label)

    event["classification"] = classification["Name"]
    event["Score"] = classification["Score"]
    event["Item"] = item_label["Name"]
    event["Score"] = item_label["Score"]

    updateShadowTopic(event["classification"])

    # result = {}
    # max = 0
    # for item in response:
    #     print("item", item)
    #     if item['score'] > max:
    #         max = item['score']
    #         result[item['label']] = item['score']

    return event
