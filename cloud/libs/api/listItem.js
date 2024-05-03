/**
 * AppSync function: lists items in a DynamoDB table.
 * Find more samples and templates at https://github.com/aws-samples/aws-appsync-resolver-samples
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

import { util } from '@aws-appsync/utils';

export function request(ctx) {
    const { filter, limit = 20, nextToken } = ctx.args;
    return dynamoDBScanRequest({ filter, limit, nextToken });
}

export function response(ctx) {
    const { error, result } = ctx;
    if (error) {
        return util.appendError(error.message, error.type, result);
    }
    const { items = [], nextToken } = result;
    return { items, nextToken };
}

function dynamoDBScanRequest({ filter: f, limit, nextToken }) {
    const filter = f ? JSON.parse(util.transform.toDynamoDBFilterExpression(f)) : null;

    return { operation: 'Scan', filter, limit, nextToken };
}
