---
excalidraw-plugin: parsed
tags: [excalidraw]
---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==

# Excalidraw Data

## Text Elements
Original Task ^text-task
Actor (LLM)
policy pi ^text-actor
Environment /
Tools ^text-env
Trajectory
s_0, a_0, s_1, a_1, ... ^text-traj
Evaluator (LLM)
scoring function ^text-evaluator
Success? ^text-decision
Self-Reflection
"what went wrong" ^text-reflector
Episodic Memory Buffer
(sliding window of reflections) ^text-memory
Next Attempt
(conditioned on memory) ^text-next
initial prompt ^text-edge-0
k recent reflections ^text-edge-1
action a_t ^text-edge-2
obs s_{t+1} ^text-edge-3
trajectory ^text-edge-4
rollout ^text-edge-5
score ^text-edge-6
yes ^text-edge-7
no ^text-edge-8
free-text reflection ^text-edge-9
retry loop ^text-edge-10
augmented prompt ^text-edge-11

%%
## Drawing
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin/releases/tag/2.0.0",
  "elements": [
    {
      "id": "node-task",
      "type": "rectangle",
      "x": 320.0,
      "y": 0.0,
      "width": 160.0,
      "height": 60.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1373158607,
      "version": 1,
      "versionNonce": 239081664,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-task",
          "type": "text"
        },
        {
          "id": "arrow-0",
          "type": "arrow"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-task",
      "type": "text",
      "x": 337.6,
      "y": 20.0,
      "width": 124.8,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 53710185,
      "version": 1,
      "versionNonce": 1592467582,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Original Task",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-task",
      "originalText": "Original Task",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-actor",
      "type": "rectangle",
      "x": 80.0,
      "y": 200.0,
      "width": 160.0,
      "height": 60.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#b2f2bb",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 590620972,
      "version": 1,
      "versionNonce": 525901257,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-actor",
          "type": "text"
        },
        {
          "id": "arrow-0",
          "type": "arrow"
        },
        {
          "id": "arrow-1",
          "type": "arrow"
        },
        {
          "id": "arrow-2",
          "type": "arrow"
        },
        {
          "id": "arrow-3",
          "type": "arrow"
        },
        {
          "id": "arrow-4",
          "type": "arrow"
        },
        {
          "id": "arrow-11",
          "type": "arrow"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-actor",
      "type": "text",
      "x": 59.2,
      "y": 220.0,
      "width": 201.6,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 479341424,
      "version": 1,
      "versionNonce": 299655413,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Actor (LLM)\npolicy pi",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-actor",
      "originalText": "Actor (LLM)\npolicy pi",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-env",
      "type": "rectangle",
      "x": 80.0,
      "y": 400.0,
      "width": 160.0,
      "height": 60.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffe066",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1581559893,
      "version": 1,
      "versionNonce": 220106708,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-env",
          "type": "text"
        },
        {
          "id": "arrow-2",
          "type": "arrow"
        },
        {
          "id": "arrow-3",
          "type": "arrow"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-env",
      "type": "text",
      "x": 68.8,
      "y": 420.0,
      "width": 182.4,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1453201079,
      "version": 1,
      "versionNonce": 1590571866,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Environment /\nTools",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-env",
      "originalText": "Environment /\nTools",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-traj",
      "type": "rectangle",
      "x": 360.0,
      "y": 400.0,
      "width": 160.0,
      "height": 60.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffffff",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1915941033,
      "version": 1,
      "versionNonce": 1171165723,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-traj",
          "type": "text"
        },
        {
          "id": "arrow-4",
          "type": "arrow"
        },
        {
          "id": "arrow-5",
          "type": "arrow"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-traj",
      "type": "text",
      "x": 276.8,
      "y": 420.0,
      "width": 326.4,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 186699714,
      "version": 1,
      "versionNonce": 1268073013,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Trajectory\ns_0, a_0, s_1, a_1, ...",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-traj",
      "originalText": "Trajectory\ns_0, a_0, s_1, a_1, ...",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-evaluator",
      "type": "diamond",
      "x": 360.0,
      "y": 200.0,
      "width": 160.0,
      "height": 60.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#fcc2d7",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 2
      },
      "seed": 906070221,
      "version": 1,
      "versionNonce": 68252794,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-evaluator",
          "type": "text"
        },
        {
          "id": "arrow-5",
          "type": "arrow"
        },
        {
          "id": "arrow-6",
          "type": "arrow"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-evaluator",
      "type": "text",
      "x": 286.4,
      "y": 220.0,
      "width": 307.2,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 63989048,
      "version": 1,
      "versionNonce": 201209006,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Evaluator (LLM)\nscoring function",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-evaluator",
      "originalText": "Evaluator (LLM)\nscoring function",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-decision",
      "type": "diamond",
      "x": 560.0,
      "y": 200.0,
      "width": 160.0,
      "height": 60.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffffff",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 2
      },
      "seed": 469521478,
      "version": 1,
      "versionNonce": 499635469,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-decision",
          "type": "text"
        },
        {
          "id": "arrow-6",
          "type": "arrow"
        },
        {
          "id": "arrow-7",
          "type": "arrow"
        },
        {
          "id": "arrow-8",
          "type": "arrow"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-decision",
      "type": "text",
      "x": 601.6,
      "y": 220.0,
      "width": 76.8,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1085242217,
      "version": 1,
      "versionNonce": 1292825379,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Success?",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-decision",
      "originalText": "Success?",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-reflector",
      "type": "ellipse",
      "x": 760.0,
      "y": 80.0,
      "width": 160.0,
      "height": 60.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#fcc2d7",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 2
      },
      "seed": 56985562,
      "version": 1,
      "versionNonce": 1205264596,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-reflector",
          "type": "text"
        },
        {
          "id": "arrow-8",
          "type": "arrow"
        },
        {
          "id": "arrow-9",
          "type": "arrow"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-reflector",
      "type": "text",
      "x": 681.6,
      "y": 100.0,
      "width": 316.8,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 427000597,
      "version": 1,
      "versionNonce": 1537640409,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Self-Reflection\n\"what went wrong\"",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-reflector",
      "originalText": "Self-Reflection\n\"what went wrong\"",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-memory",
      "type": "rectangle",
      "x": 760.0,
      "y": 320.0,
      "width": 160.0,
      "height": 60.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#d0bfff",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1395616197,
      "version": 1,
      "versionNonce": 1506083911,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-memory",
          "type": "text"
        },
        {
          "id": "arrow-1",
          "type": "arrow"
        },
        {
          "id": "arrow-9",
          "type": "arrow"
        },
        {
          "id": "arrow-10",
          "type": "arrow"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-memory",
      "type": "text",
      "x": 580.8,
      "y": 340.0,
      "width": 518.4,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1170252924,
      "version": 1,
      "versionNonce": 900911955,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Episodic Memory Buffer\n(sliding window of reflections)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-memory",
      "originalText": "Episodic Memory Buffer\n(sliding window of reflections)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-next",
      "type": "rectangle",
      "x": 560.0,
      "y": 480.0,
      "width": 160.0,
      "height": 60.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#a5d8ff",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 473392625,
      "version": 1,
      "versionNonce": 964669078,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-next",
          "type": "text"
        },
        {
          "id": "arrow-7",
          "type": "arrow"
        },
        {
          "id": "arrow-10",
          "type": "arrow"
        },
        {
          "id": "arrow-11",
          "type": "arrow"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-next",
      "type": "text",
      "x": 467.20000000000005,
      "y": 500.0,
      "width": 345.59999999999997,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1265438423,
      "version": 1,
      "versionNonce": 597409993,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Next Attempt\n(conditioned on memory)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-next",
      "originalText": "Next Attempt\n(conditioned on memory)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-0",
      "type": "arrow",
      "x": 320.0,
      "y": 30.0,
      "width": 80.0,
      "height": 200.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1738238662,
      "version": 1,
      "versionNonce": 1866808230,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -80.0,
          200.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-task",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-actor",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-0",
      "type": "text",
      "x": 218.39999999999998,
      "y": 114.0,
      "width": 123.20000000000002,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 13955984,
      "version": 1,
      "versionNonce": 1629526406,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "initial prompt",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "initial prompt",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-1",
      "type": "arrow",
      "x": 760.0,
      "y": 350.0,
      "width": 520.0,
      "height": 120.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1730483679,
      "version": 1,
      "versionNonce": 342865763,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -520.0,
          -120.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-memory",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-actor",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-1",
      "type": "text",
      "x": 412.0,
      "y": 274.0,
      "width": 176.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1499242942,
      "version": 1,
      "versionNonce": 907557513,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "k recent reflections",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "k recent reflections",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-2",
      "type": "arrow",
      "x": 80.0,
      "y": 230.0,
      "width": 160.0,
      "height": 200.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 730682428,
      "version": 1,
      "versionNonce": 596724165,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          160.0,
          200.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-actor",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-env",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-2",
      "type": "text",
      "x": 116.0,
      "y": 314.0,
      "width": 88.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 333889689,
      "version": 1,
      "versionNonce": 462382782,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "action a_t",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "action a_t",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-3",
      "type": "arrow",
      "x": 80.0,
      "y": 430.0,
      "width": 160.0,
      "height": 200.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 2055599410,
      "version": 1,
      "versionNonce": 1639591160,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          160.0,
          -200.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-env",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-actor",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-3",
      "type": "text",
      "x": 111.6,
      "y": 314.0,
      "width": 96.80000000000001,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 722831293,
      "version": 1,
      "versionNonce": 219494903,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "obs s_{t+1}",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "obs s_{t+1}",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-4",
      "type": "arrow",
      "x": 240.0,
      "y": 230.0,
      "width": 120.0,
      "height": 200.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 199170185,
      "version": 1,
      "versionNonce": 815887679,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          120.0,
          200.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-actor",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-traj",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-4",
      "type": "text",
      "x": 256.0,
      "y": 314.0,
      "width": 88.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 207696844,
      "version": 1,
      "versionNonce": 770902344,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "trajectory",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "trajectory",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-5",
      "type": "arrow",
      "x": 360.0,
      "y": 430.0,
      "width": 160.0,
      "height": 200.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1819980298,
      "version": 1,
      "versionNonce": 738639289,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          160.0,
          -200.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-traj",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-evaluator",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-5",
      "type": "text",
      "x": 409.2,
      "y": 314.0,
      "width": 61.60000000000001,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1296491778,
      "version": 1,
      "versionNonce": 568054228,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "rollout",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "rollout",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-6",
      "type": "arrow",
      "x": 520.0,
      "y": 230.0,
      "width": 40.0,
      "height": 0.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1733294784,
      "version": 1,
      "versionNonce": 93309106,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          40.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-evaluator",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-decision",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-6",
      "type": "text",
      "x": 518.0,
      "y": 214.0,
      "width": 44.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1567087081,
      "version": 1,
      "versionNonce": 986607412,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "score",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "score",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-7",
      "type": "arrow",
      "x": 560.0,
      "y": 230.0,
      "width": 160.0,
      "height": 280.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1151541059,
      "version": 1,
      "versionNonce": 268062141,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          160.0,
          280.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-decision",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-next",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-7",
      "type": "text",
      "x": 626.8,
      "y": 354.0,
      "width": 26.400000000000002,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 2089750183,
      "version": 1,
      "versionNonce": 1980614225,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "yes",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "yes",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-8",
      "type": "arrow",
      "x": 720.0,
      "y": 230.0,
      "width": 40.0,
      "height": 120.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 812896394,
      "version": 1,
      "versionNonce": 169222133,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          40.0,
          -120.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-decision",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-reflector",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-8",
      "type": "text",
      "x": 731.2,
      "y": 154.0,
      "width": 17.6,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1185498233,
      "version": 1,
      "versionNonce": 629595553,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "no",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "no",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-9",
      "type": "arrow",
      "x": 760.0,
      "y": 110.0,
      "width": 160.0,
      "height": 240.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1781132954,
      "version": 1,
      "versionNonce": 1349993688,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          160.0,
          240.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-reflector",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-memory",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-9",
      "type": "text",
      "x": 752.0,
      "y": 214.0,
      "width": 176.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1328261054,
      "version": 1,
      "versionNonce": 1901493144,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "free-text reflection",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "free-text reflection",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-10",
      "type": "arrow",
      "x": 760.0,
      "y": 350.0,
      "width": 40.0,
      "height": 160.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1850501473,
      "version": 1,
      "versionNonce": 776605305,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -40.0,
          160.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-memory",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-next",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-10",
      "type": "text",
      "x": 696.0,
      "y": 414.0,
      "width": 88.0,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1239854304,
      "version": 1,
      "versionNonce": 412936599,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "retry loop",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "retry loop",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-11",
      "type": "arrow",
      "x": 560.0,
      "y": 510.0,
      "width": 320.0,
      "height": 280.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 1513056505,
      "version": 1,
      "versionNonce": 149368554,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "points": [
        [
          0,
          0
        ],
        [
          -320.0,
          -280.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-next",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-actor",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-11",
      "type": "text",
      "x": 329.6,
      "y": 354.0,
      "width": 140.8,
      "height": 20.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "transparent",
      "fillStyle": "hachure",
      "strokeWidth": 1,
      "strokeStyle": "solid",
      "roughness": 1.0,
      "opacity": 100,
      "groupIds": [],
      "frameId": null,
      "roundness": {
        "type": 3
      },
      "seed": 98407117,
      "version": 1,
      "versionNonce": 1420052173,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "augmented prompt",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "augmented prompt",
      "lineHeight": 1.25,
      "baseline": 18
    }
  ],
  "appState": {
    "gridSize": null,
    "viewBackgroundColor": "#ffffff"
  },
  "files": {}
}
```
%%
