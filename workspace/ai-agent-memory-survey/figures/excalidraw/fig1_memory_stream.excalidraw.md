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
      "x": 470.0,
      "y": 278.2,
      "width": 180.0,
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
      "x": 488.0,
      "y": 290.0,
      "width": 144.0,
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
      "x": 799.6,
      "y": 278.2,
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
      "x": 817.6,
      "y": 290.0,
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
      "x": 649.2,
      "y": 58.2,
      "width": 141.6,
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
      "x": 667.2,
      "y": 70.0,
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
      "x": 295.6,
      "y": 58.2,
      "width": 208.79999999999998,
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
      "x": 313.6,
      "y": 70.0,
      "width": 172.79999999999998,
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
      "x": 0.4000000000000057,
      "y": 58.2,
      "width": 199.2,
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
      "x": 18.400000000000006,
      "y": 70.0,
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
      "x": 12.400000000000006,
      "y": 278.2,
      "width": 295.2,
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
      "x": 30.400000000000006,
      "y": 290.0,
      "width": 259.2,
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
      "x": 228.4,
      "y": 478.2,
      "width": 343.2,
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
      "x": 246.4,
      "y": 490.0,
      "width": 307.2,
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
      "x": 589.5,
      "y": 459.12,
      "width": 261.0,
      "height": 101.76,
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
      "x": 648.0,
      "y": 490.0,
      "width": 144.0,
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
      "x": 856.8727272727273,
      "y": 278.2,
      "width": 113.74545454545455,
      "height": 156.39999999999998,
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
          -113.74545454545455,
          -156.39999999999998
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
      "x": 717.7900746622201,
      "y": 182.7890366092944,
      "width": 184.79999999999998,
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
      "seed": 1265438423,
      "version": 1,
      "versionNonce": 597409993,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "observation / response",
      "fontSize": 14,
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
      "x": 649.2,
      "y": 90.0,
      "width": 144.80000000000007,
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
          -144.80000000000007,
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
      "x": 551.5999999999999,
      "y": 67.60000000000001,
      "width": 50.4,
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
      "text": "append",
      "fontSize": 14,
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
      "x": 295.6,
      "y": 90.0,
      "width": 96.00000000000003,
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
          -48.0,
          -15.36
        ],
        [
          -96.00000000000003,
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
      "x": 188.8,
      "y": 64.82,
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
      "seed": 1499242942,
      "version": 1,
      "versionNonce": 907557513,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "score each obs",
      "fontSize": 14,
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
      "x": 199.6,
      "y": 90.0,
      "width": 96.00000000000003,
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
          48.00000000000003,
          24.960000000000008
        ],
        [
          96.00000000000003,
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
      "x": 197.20000000000002,
      "y": 100.38000000000001,
      "width": 100.8,
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
      "text": "attach score",
      "fontSize": 14,
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
      "x": 365.3090909090909,
      "y": 121.80000000000001,
      "width": 171.5384013920738,
      "height": 157.24353460940097,
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
          -110.92816623354102,
          51.175623081968666
        ],
        [
          -171.5384013920738,
          157.24353460940097
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
      "x": 228.1573278047184,
      "y": 171.22260831378884,
      "width": 67.2,
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
      "text": "periodic",
      "fontSize": 14,
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
      "x": 193.7706895170171,
      "y": 279.043534609401,
      "width": 171.5384013920738,
      "height": 157.24353460940097,
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
          126.65251969448116,
          -34.02178294276129
        ],
        [
          171.5384013920738,
          -157.24353460940097
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
      "x": 237.98462935185972,
      "y": 218.5978463652158,
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
      "seed": 207696844,
      "version": 1,
      "versionNonce": 770902344,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "abstract entries",
      "fontSize": 14,
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
      "x": 650.0,
      "y": 310.0,
      "width": 149.60000000000002,
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
          74.79999999999995,
          23.93599999999998
        ],
        [
          149.60000000000002,
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
      "x": 678.5999999999999,
      "y": 319.86799999999994,
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
      "seed": 1296491778,
      "version": 1,
      "versionNonce": 568054228,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "next action",
      "fontSize": 14,
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
      "x": 799.6,
      "y": 310.0,
      "width": 149.60000000000002,
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
          -74.80000000000007,
          -38.896000000000015
        ],
        [
          -149.60000000000002,
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
      "x": 699.5999999999999,
      "y": 273.052,
      "width": 50.4,
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
      "text": "result",
      "fontSize": 14,
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
      "x": 534.56,
      "y": 341.8,
      "width": 109.11999999999995,
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
          -109.11999999999995,
          136.39999999999998
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
      "x": 449.1610530010178,
      "y": 392.32884240081427,
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
      "seed": 2089750183,
      "version": 1,
      "versionNonce": 1980614225,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "query",
      "fontSize": 14,
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
      "x": 400.0,
      "y": 121.8,
      "width": 0.0,
      "height": 356.4,
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
          0.0,
          356.4
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
      "x": 332.79999999999995,
      "y": 290.2,
      "width": 109.2,
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
      "text": "candidate set",
      "fontSize": 14,
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
      "x": 571.6,
      "y": 510.0,
      "width": 17.899999999999977,
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
          17.899999999999977,
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
      "x": 559.55,
      "y": 512.8000000000001,
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
      "seed": 1328261054,
      "version": 1,
      "versionNonce": 1901493144,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "top-k",
      "fontSize": 14,
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
      "x": 688.9734352001121,
      "y": 471.21679400014017,
      "width": 103.53343520011208,
      "height": 129.41679400014016,
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
          -103.53343520011208,
          -129.41679400014016
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
      "x": 596.6456645990384,
      "y": 388.83723940088436,
      "width": 100.8,
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
      "text": "conditioning",
      "fontSize": 14,
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
