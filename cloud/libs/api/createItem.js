/**
 * AppSync function: creates a new item in a DynamoDB table.
 * Find more samples and templates at https://github.com/aws-samples/aws-appsync-resolver-samples
 * 
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */



import { util } from '@aws-appsync/utils';

/**
 * Creates a new item in a DynamoDB table
 * @param ctx contextual information about the request
 */
export function request(ctx) {
    const { input: values } = ctx.arguments;
    const key = { id: util.autoId() };
    const condition = { id: { attributeExists: false } };
    console.log('--> create with requested values: ', values);
    return dynamodbPutRequest({ key, values, condition });
}

/**
 * Returns the result
 * @param ctx contextual information about the request
 */
export function response(ctx) {
    const { error, result } = ctx;
    if (error) {
        return util.appendError(error.message, error.type, result);
    }
    return ctx.result;
}

/**
 * Helper function to create a new item
 * @returns a PutItem request
 */
function dynamodbPutRequest({ key, values, condition: inCondObj }) {
    const condition = JSON.parse(util.transform.toDynamoDBConditionExpression(inCondObj));
    if (condition.expressionValues && !Object.keys(condition.expressionValues).length) {
        delete condition.expressionValues;
    }
    return {
        operation: 'PutItem',
        key: util.dynamodb.toMapValues(key),
        attributeValues: util.dynamodb.toMapValues(values),
        condition,
    };
}
