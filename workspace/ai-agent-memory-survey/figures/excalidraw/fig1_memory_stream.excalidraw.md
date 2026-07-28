---
excalidraw-plugin: parsed
tags: [excalidraw]
---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==

# Excalidraw Data

## Text Elements
LLM Agent
(decision loop) ^text-agent
Environment /
Tool / User ^text-env
Observation
(per step) ^text-obs
Memory Stream
(append-only list) ^text-stream
Importance Scorer
(LLM, score 1-10) ^text-scorer
Reflector
(higher-level abstractions) ^text-reflector
Retriever
recency x importance x relevance ^text-retriever
Working Context
(next prompt) ^text-ctx
observation / response ^text-edge-0
append ^text-edge-1
score each obs ^text-edge-2
attach score ^text-edge-3
periodic ^text-edge-4
abstract entries ^text-edge-5
next action ^text-edge-6
result ^text-edge-7
query ^text-edge-8
candidate set ^text-edge-9
top-k ^text-edge-10
conditioning ^text-edge-11

%%
## Drawing
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin/releases/tag/2.0.0",
  "elements": [
    {
      "id": "node-agent",
      "type": "rectangle",
      "x": 480.0,
      "y": 280.0,
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
          "id": "text-agent",
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
      "id": "text-agent",
      "type": "text",
      "x": 440.0,
      "y": 300.0,
      "width": 240.0,
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
      "text": "LLM Agent\n(decision loop)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-agent",
      "originalText": "LLM Agent\n(decision loop)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-env",
      "type": "rectangle",
      "x": 800.0,
      "y": 280.0,
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
      "seed": 590620972,
      "version": 1,
      "versionNonce": 525901257,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-env",
          "type": "text"
        },
        {
          "id": "arrow-0",
          "type": "arrow"
        },
        {
          "id": "arrow-6",
          "type": "arrow"
        },
        {
          "id": "arrow-7",
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
      "x": 760.0,
      "y": 300.0,
      "width": 240.0,
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
      "text": "Environment /\nTool / User",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-env",
      "originalText": "Environment /\nTool / User",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-obs",
      "type": "rectangle",
      "x": 640.0,
      "y": 60.0,
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
      "seed": 1581559893,
      "version": 1,
      "versionNonce": 220106708,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-obs",
          "type": "text"
        },
        {
          "id": "arrow-0",
          "type": "arrow"
        },
        {
          "id": "arrow-1",
          "type": "arrow"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-obs",
      "type": "text",
      "x": 614.4,
      "y": 80.0,
      "width": 211.2,
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
      "text": "Observation\n(per step)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-obs",
      "originalText": "Observation\n(per step)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-stream",
      "type": "rectangle",
      "x": 320.0,
      "y": 60.0,
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
      "seed": 1915941033,
      "version": 1,
      "versionNonce": 1171165723,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-stream",
          "type": "text"
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
          "id": "arrow-5",
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
      "id": "text-stream",
      "type": "text",
      "x": 246.4,
      "y": 80.0,
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
      "seed": 186699714,
      "version": 1,
      "versionNonce": 1268073013,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Memory Stream\n(append-only list)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-stream",
      "originalText": "Memory Stream\n(append-only list)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-scorer",
      "type": "rectangle",
      "x": 80.0,
      "y": 60.0,
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
      "seed": 906070221,
      "version": 1,
      "versionNonce": 68252794,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-scorer",
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
      "id": "text-scorer",
      "type": "text",
      "x": -8.0,
      "y": 80.0,
      "width": 336.0,
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
      "text": "Importance Scorer\n(LLM, score 1-10)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-scorer",
      "originalText": "Importance Scorer\n(LLM, score 1-10)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-reflector",
      "type": "ellipse",
      "x": 80.0,
      "y": 280.0,
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
      "seed": 469521478,
      "version": 1,
      "versionNonce": 499635469,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-reflector",
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
      "id": "text-reflector",
      "type": "text",
      "x": -17.599999999999994,
      "y": 300.0,
      "width": 355.2,
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
      "text": "Reflector\n(higher-level abstractions)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-reflector",
      "originalText": "Reflector\n(higher-level abstractions)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-retriever",
      "type": "rectangle",
      "x": 320.0,
      "y": 480.0,
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
      "seed": 56985562,
      "version": 1,
      "versionNonce": 1205264596,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-retriever",
          "type": "text"
        },
        {
          "id": "arrow-8",
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
      "id": "text-retriever",
      "type": "text",
      "x": 198.4,
      "y": 500.0,
      "width": 403.2,
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
      "text": "Retriever\nrecency x importance x relevance",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-retriever",
      "originalText": "Retriever\nrecency x importance x relevance",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-ctx",
      "type": "diamond",
      "x": 640.0,
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
        "type": 2
      },
      "seed": 1395616197,
      "version": 1,
      "versionNonce": 1506083911,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-ctx",
          "type": "text"
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
      "id": "text-ctx",
      "type": "text",
      "x": 580.8,
      "y": 500.0,
      "width": 278.4,
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
      "text": "Working Context\n(next prompt)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-ctx",
      "originalText": "Working Context\n(next prompt)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-0",
      "type": "arrow",
      "x": 800.0,
      "y": 310.0,
      "width": 0.0,
      "height": 220.0,
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
      "seed": 473392625,
      "version": 1,
      "versionNonce": 964669078,
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
          -220.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-env",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-obs",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-0",
      "type": "text",
      "x": 703.2,
      "y": 184.0,
      "width": 193.60000000000002,
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
      "text": "observation / response",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "observation / response",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-1",
      "type": "arrow",
      "x": 640.0,
      "y": 90.0,
      "width": 160.0,
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
          -160.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-obs",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-stream",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-1",
      "type": "text",
      "x": 533.6,
      "y": 74.0,
      "width": 52.800000000000004,
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
      "text": "append",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "append",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-2",
      "type": "arrow",
      "x": 320.0,
      "y": 90.0,
      "width": 80.0,
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
          -80.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-stream",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-scorer",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-2",
      "type": "text",
      "x": 218.39999999999998,
      "y": 74.0,
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
      "seed": 1499242942,
      "version": 1,
      "versionNonce": 907557513,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "score each obs",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "score each obs",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-3",
      "type": "arrow",
      "x": 240.0,
      "y": 90.0,
      "width": 80.0,
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
          80.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-scorer",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-stream",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-3",
      "type": "text",
      "x": 227.2,
      "y": 74.0,
      "width": 105.60000000000001,
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
      "text": "attach score",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "attach score",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-4",
      "type": "arrow",
      "x": 320.0,
      "y": 90.0,
      "width": 80.0,
      "height": 220.0,
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
          -80.0,
          220.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-stream",
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
      "id": "text-edge-4",
      "type": "text",
      "x": 244.8,
      "y": 184.0,
      "width": 70.4,
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
      "text": "periodic",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "periodic",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-5",
      "type": "arrow",
      "x": 240.0,
      "y": 310.0,
      "width": 80.0,
      "height": 220.0,
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
          80.0,
          -220.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-reflector",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-stream",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-5",
      "type": "text",
      "x": 209.6,
      "y": 184.0,
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
      "seed": 207696844,
      "version": 1,
      "versionNonce": 770902344,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "abstract entries",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "abstract entries",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-6",
      "type": "arrow",
      "x": 640.0,
      "y": 310.0,
      "width": 160.0,
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
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-agent",
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
      "id": "text-edge-6",
      "type": "text",
      "x": 671.6,
      "y": 294.0,
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
      "seed": 1296491778,
      "version": 1,
      "versionNonce": 568054228,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "next action",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "next action",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-7",
      "type": "arrow",
      "x": 800.0,
      "y": 310.0,
      "width": 160.0,
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
          -160.0,
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-env",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-agent",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-7",
      "type": "text",
      "x": 693.6,
      "y": 294.0,
      "width": 52.800000000000004,
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
      "text": "result",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "result",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-8",
      "type": "arrow",
      "x": 480.0,
      "y": 310.0,
      "width": 0.0,
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
          200.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-agent",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-retriever",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-8",
      "type": "text",
      "x": 458.0,
      "y": 394.0,
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
      "seed": 2089750183,
      "version": 1,
      "versionNonce": 1980614225,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "query",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "query",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-9",
      "type": "arrow",
      "x": 320.0,
      "y": 90.0,
      "width": 160.0,
      "height": 420.0,
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
          160.0,
          420.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-stream",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-retriever",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-9",
      "type": "text",
      "x": 342.8,
      "y": 284.0,
      "width": 114.4,
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
      "text": "candidate set",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "candidate set",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-10",
      "type": "arrow",
      "x": 480.0,
      "y": 510.0,
      "width": 160.0,
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
          0.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-retriever",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-ctx",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-10",
      "type": "text",
      "x": 538.0,
      "y": 494.0,
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
      "seed": 1328261054,
      "version": 1,
      "versionNonce": 1901493144,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "top-k",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "top-k",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-11",
      "type": "arrow",
      "x": 640.0,
      "y": 510.0,
      "width": 0.0,
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
          0.0,
          -200.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-ctx",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-agent",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-11",
      "type": "text",
      "x": 587.2,
      "y": 394.0,
      "width": 105.60000000000001,
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
      "text": "conditioning",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "conditioning",
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
