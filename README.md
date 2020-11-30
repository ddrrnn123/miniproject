# mini-project

## Project Domain
This project used webgme to implement the Petri-Net Design Studio. This studio create a petri-net with finite places, transitions, and arcs. Places are used to store tokens. Transition are used to transfer tokens from source places (inplace) to target places (outplace). Arcs are the links between places and transitions to achieve sending. With different designs, the nets have four different classifications, which are Free-choice petri-net, state machine, marked graph, and workflow net. 

## Project usage
Petri-Net is a low-level model, which is used to describe systems. It can quickly express concurrency, conflict, and causality, etc. For instance, the team [statebox]( statebox.org/) have plans to generate Rholang programs directly with Petri-Nets. The places can represent states, conditions, or resources. The transitions can be actions. The tokens can represent that the places have amounts of resources and these resources can be transfered to other with the action named "fire". 

In this studio, a project seed with the Petri-Net metamodel has already created. You can design your example using "composition" tab and create a simulator in "Demo" tab. In "Demo", you can click buttons to see the net classification and refresh the net. You can drag or click the components in the graph for interaction.

The main codes are in 
(1)src/plugins/ModelicaCodeGenerator/ModelicaCodeGenerator/__init__.py\
(2)src/visualizers/panels/Demo/DemoControl.js\
(3)src/visualizers/widgets/Demo/DemoWidget.js

(1) Get the information from the metamodel example and check the classification. Send all the information to simulator through messages.\
(2) Create bottons to display the classification and refresh the simulor; Receive the messages and organize the information.\
(3) Design the interaction and draw the network.

## Installation
1. Install the mini-project following:
- [NodeJS](https://nodejs.org/en/) (LTS recommended)
- [MongoDB](https://www.mongodb.com/)

2. Download and Install [Git](https://git-scm.com/downloads) and [Python](https://www.python.org/downloads/).

3. Download the source code and go to the main folder in Terminal.

3. In terminal, install webgme \
  `npm install -g webgme-cli`\
  `python -m pip install webgme-bindings`\
  `npm install webgme-bindings --save`


## Start modeling
1. fire up the server\
  `node ./app.js`
  
2. Go to the listening [webpage](localhost:8888). Open the seed object.


## other issues
1. Due to my system which contains python2 and python3. I've change the line 28 in MIC/src/plugins/ModelicaCodeGenerator/ModelicaCodeGenerator.js from "python" to "python3".
2. The token display should use jointjs@2.2.0.


## Model the network.
### Use default examples
In the seed object. Go to the "Composition" tab. There are already four networks you can use with the classifications on their names.

### Create a new network
If you want to create your network, drag a "Petri-Net" from the left workspace to the main sheet. You can change the name of this network. Then, double click the network to go to the inside sheet. You can drag places and transitions to this sheet and create arcs between places and transitions. All places should be set up markings with non-zero numbers.

### Create a simulator
Click "Demo" to create a simulator for this network. Click "Search" button on the top to see the classification. Click the "Refresh" button to reset the network. Click each transition to fire tokens. If the transition reaches a deadlock, this transition will become gray and freezed. Then, there is an alert to notify you. 







