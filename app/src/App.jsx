import { Amplify } from 'aws-amplify';
import { withAuthenticator } from '@aws-amplify/ui-react';
import { applyMode, Mode } from '@cloudscape-design/global-styles';
import '@aws-amplify/ui-react/styles.css';
import AppLayout from "@cloudscape-design/components/app-layout";
import ContentLayout from "@cloudscape-design/components/content-layout";
import SpaceBetween from "@cloudscape-design/components/space-between";
import Header from "@cloudscape-design/components/header";
import Button from "@cloudscape-design/components/button";
import HelpPanel from "@cloudscape-design/components/help-panel";
import WasteMass from "./components/WasteMass";
import WasteItem from "./components/WasteItem";

import awsExports from './aws-exports';
Amplify.configure(awsExports);
//applyMode(Mode.Dark);

// const prompts = [
//   "Place an Item under camera",
//   "Press the red button to take picture",
//   "Check the result on portal and LCD display"
// ];

const App = ({ signOut }) => {
  return (

    <AppLayout
      contentType="dashboard"
      navigationOpen
      navigationWidth={300}
      toolsOpen
      toolsWidth={500}
      navigation={
        <>
          <HelpPanel
            header={
              <Header
                variant="h6"
              >
                Demo Interaction Steps
              </Header>
            }>
            <div>
              <h5>Step 1 - Place an item under camera</h5>
              <div class="main" style={{ paddingLeft: "10px" }}>
                <img src="camera.jpg" style={{ width: '80%' }} />
              </div>

              <h5>Step 2 - Press red button to take a picture</h5>
              <div class="main" style={{ paddingLeft: "10px" }}>
                <img src="button.jpg" style={{ width: '80%' }} />
              </div>
              <h5>Step 3 - Check the result </h5>
              <div class="main" style={{ paddingLeft: "10px" }}>
                <img src="dashboard.png" style={{ width: '80%' }} />
              </div>
            </div>
          </HelpPanel>
        </>
      }
      tools={
        < HelpPanel
          header={
            < Header
              variant="h3"
            >
              <div class="main" style={{ paddingLeft: "100px" }}> Architecture</div>
            </Header >
          }
        >
          <div>
            <br></br>
            <br></br>

            <img src="recycle-demo-architecture.png" style={{ width: '100%' }} />
          </div>

        </HelpPanel >
      }
      content={
        < ContentLayout
          disableOverlap
          header={
            < Header
              variant="h1"
              color="blue"
              description="Creating a big diversion from landfill to recycle"
              actions={
                < Button onClick={signOut} > Sign out</Button >
              }
            >
              Sustainable Waste Management
            </Header >
          }
        >
          <SpaceBetween size="s">

            <WasteMass />
            <WasteItem />
          </SpaceBetween>
        </ContentLayout >
      }
    />
  );
}

export default withAuthenticator(App, { hideSignUp: true });
