/* eslint-disable */
/**
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */
export const getWasteItem = /* GraphQL */ `
  query GetWasteItem($id: ID!) {
    getWasteItem(id: $id) {
      id
      filePath
      labels
      wasteType
    }
  }
`;
export const listWasteItem = /* GraphQL */ `
  query ListWasteItems(
    $filter: WasteItemFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listWasteItem(filter: $filter, limit: $limit, nextToken: $nextToken) {
      items {
        id
        filePath
        labels
        wasteType
      }
      nextToken
    }
  }
`;
export const getWasteMass = /* GraphQL */ `
  query GetWasteMass($id: ID!) {
    getWasteMass(id: $id) {
      wasteType
      mass
      id
    }
  }
`;
export const listWasteMass = /* GraphQL */ `
  query ListWasteMasses(
    $filter: WasteMassFilterInput
    $limit: Int
    $nextToken: String
  ) {
    listWasteMass(filter: $filter, limit: $limit, nextToken: $nextToken) {
      items {
        wasteType
        mass
        id
      }
      nextToken
    }
  }
`;
