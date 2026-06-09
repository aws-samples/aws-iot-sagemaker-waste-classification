/**
 * Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
 * SPDX-License-Identifier: MIT-0
 */

import { useState, useEffect } from "react";
import { generateClient } from 'aws-amplify/api';
import { listWasteMass } from '../graphql/queries';
import { onCreateWasteMass, onUpdateWasteMass, onDeleteWasteMass } from '../graphql/subscriptions';
import BarChart from "@cloudscape-design/components/bar-chart";
import PieChart from "@cloudscape-design/components/pie-chart";
import Header from "@cloudscape-design/components/header";
import Container from "@cloudscape-design/components/container";
import Box from "@cloudscape-design/components/box";

const colourMappings = {
  landfill: "black",
  organic: "blue",
  recycle: "green"
}

const client = generateClient();

const WasteMass = () => {
  const [wasteMass, setWasteMass] = useState([]);

  useEffect(() => {
    fetchMasses();
  }, [])

  useEffect(() => {
    const createSubscriber = client.graphql({ query: onCreateWasteMass }).subscribe({
      next: () => { fetchMasses(); }
    });

    const updateSubscriber = client.graphql({ query: onUpdateWasteMass }).subscribe({
      next: () => { fetchMasses(); }
    });

    const deleteSubscriber = client.graphql({ query: onDeleteWasteMass }).subscribe({
      next: () => { fetchMasses(); }
    });

    return () => {
      createSubscriber.unsubscribe();
      updateSubscriber.unsubscribe();
      deleteSubscriber.unsubscribe();
    }
  }, [wasteMass]);

  const fetchMasses = async () => {
    try {
      const massData = await client.graphql({ query: listWasteMass })
      const masses = massData.data.listWasteMass.items
      setWasteMass(masses);
    } catch (err) {
      console.log('error fetching masses');
      console.log(err);
    }
  }

  return (
    <Container
      header={
        <Header
          variant="h2"
        >
          A Mountain of positive impact
        </Header>
      }
    >
      <div>
        <BarChart
          series={wasteMass.map(item => (
            {
              title: "Count",
              type: "bar",
              color: colourMappings[item.wasteType],
              data: [
                {
                  x: item.wasteType,
                  y: item.mass,
                },
              ]
            }
          ))}
          hideFilter
          hideLegend
          height={230}
          stackedBars
          xScaleType="categorical"
          empty={
            <Box
              textAlign="center"
            >
              <b>No data available</b>
            </Box>
          }
        />
      </div>
    </Container>
  );
}

export default WasteMass;
