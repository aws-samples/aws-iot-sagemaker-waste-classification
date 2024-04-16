/* eslint-disable */

export const createWasteItem = /* GraphQL */ `
  mutation CreateWasteItem(
    $input: CreateWasteItemInput!
  ) {
    createWasteItem(input: $input) {
      id
      filePath
      labels
      wasteType
    }
  }
`;
export const updateWasteItem = /* GraphQL */ `
  mutation UpdateWasteItem(
    $input: UpdateWasteItemInput!
  ) {
    updateWasteItem(input: $input) {
      id
      filePath
      labels
      wasteType
    }
  }
`;
export const deleteWasteItem = /* GraphQL */ `
  mutation DeleteWasteItem(
    $input: DeleteWasteItemInput!
  ) {
    deleteWasteItem(input: $input) {
      id
      filePath
      labels
      wasteType
    }
  }
`;
export const createWasteMass = /* GraphQL */ `
  mutation CreateWasteMass(
    $input: CreateWasteMassInput!
  ) {
    createWasteMass(input: $input) {
      wasteType
      mass
      id
    }
  }
`;
export const updateWasteMass = /* GraphQL */ `
  mutation UpdateWasteMass(
    $input: UpdateWasteMassInput!
  ) {
    updateWasteMass(input: $input) {
      wasteType
      mass
      id
    }
  }
`;
export const deleteWasteMass = /* GraphQL */ `
  mutation DeleteWasteMass(
    $input: DeleteWasteMassInput!
  ) {
    deleteWasteMass(input: $input) {
      wasteType
      mass
      id
    }
  }
`;
