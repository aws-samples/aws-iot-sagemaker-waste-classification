/**
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

import { useState, useEffect } from "react";
import { API, graphqlOperation, Storage } from 'aws-amplify';
import { onCreateWasteItem, onUpdateWasteItem } from '../graphql/subscriptions';
import Header from "@cloudscape-design/components/header";
import Container from "@cloudscape-design/components/container";
import ColumnLayout from "@cloudscape-design/components/column-layout";
import Box from "@cloudscape-design/components/box";
import Table from "@cloudscape-design/components/table";
import Spinner from "@cloudscape-design/components/spinner";

const WasteItem = () => {
  const [wasteItem, setWasteItem] = useState({
    id: null,
    filePath: null,
    labels: null,
    wasteType: null,
  });
  const [imageUrl, setImageUrl] = useState();

  useEffect(() => {
    const createSubscriber = API.graphql(graphqlOperation(onCreateWasteItem)).subscribe({
      next: (data) => {
        const item = data.value.data.onCreateWasteItem;
        setWasteItem(item);
        fetchImage(item.filePath);
      }
    });

    const updateSubscriber = API.graphql(graphqlOperation(onUpdateWasteItem)).subscribe({
      next: (data) => {
        const item = data.value.data.onUpdateWasteItem;
        if (item.id === wasteItem.id) {
          setWasteItem({ ...item, labels: item.labels.map(l => JSON.parse(l)) });
        }
      }
    });

    return () => {
      createSubscriber.unsubscribe();
      updateSubscriber.unsubscribe();
    }
  }, [wasteItem]);

  const fetchImage = async (filePath) => {
    try {
      const fileAccessURL = await Storage.get(filePath, { expires: 60 });
      console.log(fileAccessURL);
      setImageUrl(fileAccessURL);
    } catch (err) { console.log(err) }
  }

  return (
    <ColumnLayout columns={3}>
      <Container
        header={
          <Header
            variant="h3"
          >
            Camera Image
          </Header>
        }
      >
        <Box
          textAlign="center"
        >
          {wasteItem.filePath ?
            <img src={imageUrl} style={{ width: "100%" }} alt="Camera Image" />
            :
            <Spinner size="large" />
          }
        </Box>
      </Container>
      <Container
        header={
          <Header
            variant="h3"
          >
            Waste Type
          </Header>
        }
      >
        <Box
          textAlign="center"
        >
          {wasteItem.wasteType ?
            <img src={"/" + wasteItem.wasteType + "Bin.png"} style={{ width: "55%" }} alt={wasteItem.wasteType} />
            :
            <Spinner size="large" />
          }
        </Box>
      </Container>
      <Container
        header={
          <Header
            variant="h3"
          >
            Image Labels
          </Header>
        }
      >
        <Box
          textAlign="center"
        >
          {wasteItem.labels ?
            <Table
              columnDefinitions={[
                {
                  id: "label",
                  header: "Label",
                  cell: item => item.Name
                },
                {
                  id: "confidence",
                  header: "Confidence (%)",
                  cell: item => <Box float="right">{item.Confidence}</Box>
                }
              ]}
              items={wasteItem.labels}
              sortingDisabled
              variant="embedded"
              empty={
                <Box
                  textAlign="center"
                >
                  <b>No data available</b>
                </Box>
              }
            />
            :
            <Spinner size="large" />
          }
        </Box>
      </Container>

    </ColumnLayout>
  );
}

export default WasteItem;
