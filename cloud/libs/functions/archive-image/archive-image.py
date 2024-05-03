#Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#SPDX-License-Identifier: MIT-0

import boto3
from datetime import datetime
s3 = boto3.resource('s3')


def handler(event, context):

    now = datetime.now()

    newKey = "{}-{}-{}-{}-{}-{}-{}.jpg".format(
        now.year, now.month, now.day, now.hour, now.minute, now.second,
        "raw")

    BUCKET_NAME = event["detail"]["bucket"]["name"]
    KEY = event["detail"]["object"]["key"]

    Score = int(round(event["Score"]*100, 0))

    classified = event["classification"] + "/" + str(Score) + "/" + newKey

    s3.Object(BUCKET_NAME, classified).copy_from(
        CopySource={'Bucket': BUCKET_NAME, 'Key': KEY})

    # s3.Object(BUCKET_NAME, KEY).delete()

    return
