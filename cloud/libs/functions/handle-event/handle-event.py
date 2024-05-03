#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: MIT-0

import json
import os
import requests
from requests_aws4auth import AWS4Auth


def get_rekognition_max_confidence_labels(event):
    result = []
    label_confidences = []
    obj = {}
    max = 70
    label_count = 4

    for label in event["rekognition"]["Labels"]:
        # poor logic.. need to improve later
        obj["Name"] = label["Name"]
        obj["Confidence"] = label["Confidence"]
        label_confidences.append(json.dumps(obj))

        if int(round(label["Confidence"], 0)) > max and label_count > 0:
            label_count = label_count - 1
            result.append(json.dumps(obj))
    return label_confidences if result is None else result


def handler(event, context):
    print(json.dumps(event))
    auth_token = AWS4Auth(
        os.environ["AWS_ACCESS_KEY_ID"],
        os.environ["AWS_SECRET_ACCESS_KEY"],
        os.environ["APPSYNC_REGION"],
        "appsync",
        session_token=os.environ["AWS_SESSION_TOKEN"],
    )
    if "rekognition" not in event:
        # print("===CreateItem======")
        image_name = event["detail"]["object"]["key"]
        image_name = image_name[len("public/"):]
        data = {
            "operationName": "createWasteItem",
            "query": "mutation createWasteItem($createWasteIteminput: CreateWasteItemInput!) { createWasteItem(input: $createWasteIteminput) { id filePath labels wasteType } }",
            "variables": {
                "createWasteIteminput": {
                    "filePath": image_name
                }
            },
        }

    else:
        # print("===UpdateItem=======")

        # label_confidences = [
        #     json.dumps(
        #         {"Name": label["Name"], "Confidence": label["Confidence"]})
        #     for label in event["rekognition"]["Labels"]
        # ]

        label_confidences = get_rekognition_max_confidence_labels(event)

        # print("label_confidences:", label_confidences)

        data = {
            "operationName": "getWasteMass",
            "query": "query getWasteMass($id: ID!) { getWasteMass(id: $id) { id mass } }",
            "variables": {
                "id": event["classification"]
            }
        }

        response = requests.post(
            url=os.environ["APPSYNC_ENDPOINT"],
            auth=auth_token,
            data=json.dumps(data),
            timeout=30,
        )
        binEventCount = response.json()["data"]["getWasteMass"]["mass"]
        # print("GetMass:", binEventCount)

        data = {
            "operationName": "updateWasteMass",
            "query": "mutation updateWasteMass($updateWasteMassinput: UpdateWasteMassInput!) { updateWasteMass(input: $updateWasteMassinput) { id wasteType mass } }",
            "variables": {
                "updateWasteMassinput": {
                    "id": event["classification"],
                    "wasteType": event["classification"],
                    "mass": binEventCount + 1
                }
            }
        }

        response = requests.post(
            url=os.environ["APPSYNC_ENDPOINT"],
            auth=auth_token,
            data=json.dumps(data),
            timeout=30,
        )
        binEventCount = response.json()["data"]["updateWasteMass"]["mass"]
        # binEventCount = response.json()
        # print("updateWasteMass:", binEventCount)

        data = {
            "operationName": "updateWasteItem",
            "query": "mutation updateWasteItem($updateWasteIteminput: UpdateWasteItemInput!) { updateWasteItem(input: $updateWasteIteminput) { id filePath labels wasteType } }",
            "variables": {
                "updateWasteIteminput": {
                    "id": event["id"],
                    "labels": label_confidences,
                    "wasteType": event["classification"]
                }
            }
        }

    response = requests.post(
        url=os.environ["APPSYNC_ENDPOINT"],
        auth=auth_token,
        data=json.dumps(data),
        timeout=30,
    )

    # print("input data:", data)
    # print("appsync-response", response.json())

    if data["operationName"] == "createWasteItem":
        event["id"] = response.json()["data"]["createWasteItem"]["id"]

    return event
