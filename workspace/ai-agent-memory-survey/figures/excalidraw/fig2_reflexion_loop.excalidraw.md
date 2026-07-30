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
      "x": 319.6,
      "y": 4.5,
      "width": 160.8,
      "height": 51.0,
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
      "x": 89.2,
      "y": 198.2,
      "width": 141.6,
      "height": 63.6,
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
      "x": 107.2,
      "y": 210.0,
      "width": 105.6,
      "height": 40.0,
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
      "x": 79.6,
      "y": 398.2,
      "width": 160.8,
      "height": 63.6,
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
      "x": 97.6,
      "y": 410.0,
      "width": 124.8,
      "height": 40.0,
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
      "x": 311.6,
      "y": 398.2,
      "width": 256.79999999999995,
      "height": 63.6,
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
      "x": 329.6,
      "y": 410.0,
      "width": 220.79999999999998,
      "height": 40.0,
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
      "x": 302.54,
      "y": 179.12,
      "width": 274.91999999999996,
      "height": 101.76,
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
      "x": 363.2,
      "y": 210.0,
      "width": 153.6,
      "height": 40.0,
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
      "x": 553.0,
      "y": 189.2,
      "width": 174.0,
      "height": 81.60000000000001,
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
      "x": 740.4,
      "y": 78.2,
      "width": 199.2,
      "height": 63.6,
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
      "x": 758.4,
      "y": 90.0,
      "width": 163.2,
      "height": 40.0,
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
      "x": 673.2,
      "y": 318.2,
      "width": 333.59999999999997,
      "height": 63.6,
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
      "x": 691.2,
      "y": 330.0,
      "width": 297.59999999999997,
      "height": 40.0,
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
      "x": 511.6,
      "y": 478.2,
      "width": 256.79999999999995,
      "height": 63.6,
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
      "x": 529.6,
      "y": 490.0,
      "width": 220.79999999999998,
      "height": 40.0,
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
      "x": 369.4,
      "y": 55.5,
      "width": 171.23999999999998,
      "height": 142.7,
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
          -171.23999999999998,
          142.7
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
      "x": 216.9136765642275,
      "y": 107.37041187707307,
      "width": 117.6,
      "height": 17.5,
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
      "fontSize": 14,
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
      "x": 673.2,
      "y": 320.56470588235294,
      "width": 442.40000000000003,
      "height": 78.07058823529411,
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
          -442.40000000000003,
          -78.07058823529411
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
      "x": 370.189695207254,
      "y": 259.32113892359985,
      "width": 168.0,
      "height": 17.5,
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
      "fontSize": 14,
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
      "x": 160.0,
      "y": 261.8,
      "width": 0.0,
      "height": 136.39999999999998,
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
          -21.824000000000012,
          68.19999999999999
        ],
        [
          0.0,
          136.39999999999998
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
      "x": 99.388,
      "y": 320.2,
      "width": 84.0,
      "height": 17.5,
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
      "fontSize": 14,
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
      "x": 160.0,
      "y": 398.2,
      "width": 0.0,
      "height": 136.39999999999998,
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
          35.464,
          -68.19999999999999
        ],
        [
          0.0,
          -136.39999999999998
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
      "x": 139.232,
      "y": 320.2,
      "width": 92.39999999999999,
      "height": 17.5,
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
      "fontSize": 14,
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
      "x": 204.52,
      "y": 261.8,
      "width": 190.96,
      "height": 136.39999999999998,
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
          190.96,
          136.39999999999998
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
      "x": 250.67639875913937,
      "y": 330.45304173720484,
      "width": 84.0,
      "height": 17.5,
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
      "fontSize": 14,
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
      "x": 440.0,
      "y": 398.2,
      "width": 0.0,
      "height": 117.32,
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
          0.0,
          -117.32
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
      "x": 423.20000000000005,
      "y": 329.73999999999995,
      "width": 58.8,
      "height": 17.5,
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
      "fontSize": 14,
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
      "x": 577.46,
      "y": 230.0,
      "width": 24.460000000000036,
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
          -24.460000000000036,
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
      "x": 544.23,
      "y": 207.6,
      "width": 42.0,
      "height": 17.5,
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
      "fontSize": 14,
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
      "x": 640.0,
      "y": 270.8,
      "width": 0.0,
      "height": 207.39999999999998,
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
          0.0,
          207.39999999999998
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
      "x": 614.8,
      "y": 364.7,
      "width": 25.2,
      "height": 17.5,
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
      "fontSize": 14,
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
      "x": 678.1677419354838,
      "y": 207.09935483870967,
      "width": 115.04416605127801,
      "height": 69.02649963076675,
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
          115.04416605127801,
          -69.02649963076675
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
      "x": 733.7724714795097,
      "y": 173.59051588730435,
      "width": 16.8,
      "height": 17.5,
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
      "fontSize": 14,
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
      "x": 840.0,
      "y": 141.8,
      "width": 0.0,
      "height": 176.39999999999998,
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
          0.0,
          176.39999999999998
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
      "x": 743.4,
      "y": 220.2,
      "width": 168.0,
      "height": 17.5,
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
      "fontSize": 14,
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
      "x": 800.25,
      "y": 381.8,
      "width": 120.5,
      "height": 96.39999999999998,
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
          -120.5,
          96.39999999999998
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
      "x": 690.1288424008143,
      "y": 410.3610530010178,
      "width": 84.0,
      "height": 17.5,
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
      "fontSize": 14,
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
      "x": 585.4857142857143,
      "y": 478.2,
      "width": 370.97142857142853,
      "height": 216.39999999999998,
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
          -370.97142857142853,
          -216.39999999999998
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
      "x": 339.1487749216035,
      "y": 349.3163858486797,
      "width": 134.4,
      "height": 17.5,
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
      "fontSize": 14,
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
