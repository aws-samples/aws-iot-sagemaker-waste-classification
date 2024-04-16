/* eslint-disable */

export const onCreateWasteItem = /* GraphQL */ `
  subscription OnCreateWasteItem(
    $filter: WasteItemFilterInput
  ) {
    onCreateWasteItem(filter: $filter) {
      id
      filePath
      labels
      wasteType
    }
  }
`;
export const onUpdateWasteItem = /* GraphQL */ `
  subscription OnUpdateWasteItem(
    $filter: WasteItemFilterInput
  ) {
    onUpdateWasteItem(filter: $filter) {
      id
      filePath
      labels
      wasteType
    }
  }
`;
export const onDeleteWasteItem = /* GraphQL */ `
  subscription OnDeleteWasteItem(
    $filter: WasteItemFilterInput
  ) {
    onDeleteWasteItem(filter: $filter) {
      id
      filePath
      labels
      wasteType
    }
  }
`;
export const onCreateWasteMass = /* GraphQL */ `
  subscription OnCreateWasteMass(
    $filter: WasteMassFilterInput
  ) {
    onCreateWasteMass(filter: $filter) {
      wasteType
      mass
      id
    }
  }
`;
export const onUpdateWasteMass = /* GraphQL */ `
  subscription OnUpdateWasteMass(
    $filter: WasteMassFilterInput
  ) {
    onUpdateWasteMass(filter: $filter) {
      wasteType
      mass
      id
    }
  }
`;
export const onDeleteWasteMass = /* GraphQL */ `
  subscription OnDeleteWasteMass(
    $filter: WasteMassFilterInput
  ) {
    onDeleteWasteMass(filter: $filter) {
      wasteType
      mass
      id
    }
  }
`;
