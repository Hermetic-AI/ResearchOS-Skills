---
excalidraw-plugin: parsed
tags: [excalidraw]
---
==⚠  Switch to EXCALIDRAW VIEW in the MORE OPTIONS menu of this document. ⚠==

# Excalidraw Data

## Text Elements
Long input /
large history ^text-input_left
Long input /
large history ^text-input_right
ROUTE A: Memory Engineering ^text-header_left
ROUTE B: Long-Context Training ^text-header_right
Pretrained LLM
(any off-the-shelf) ^text-llm_a
External Memory
(vector DB / KV cache /
paging / skills / schemas) ^text-mem
function-call paging
[MemGPT, Packer 2023] ^text-paging
retrieve / read /
manage cycle ^text-retrieve
Working Context
(retrieved snippets +
system prompt) ^text-ctx_a
Long-context data
(millions of tokens) ^text-data
Multi-stage RL
DPO -> GRPO/PPO
[LongAgent, Hu 2024] ^text-rl
Trained 7B LLM
(uses 128K directly) ^text-llm_b
Working Context
(model attends to
its own 128K) ^text-ctx_b
Trade-off:
A: flexible schema, slow paging
B: fast inference, no flexibility ^text-tradeoff
feeds ^text-edge-0
offloaded to ^text-edge-1
queries ^text-edge-2
page-in ^text-edge-3
top-k ^text-edge-4
assemble ^text-edge-5
training corpus ^text-edge-6
fine-tune ^text-edge-7
yields ^text-edge-8
one-pass ^text-edge-9
Route A ^text-edge-10
Route B ^text-edge-11

%%
## Drawing
```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://github.com/zsviczian/obsidian-excalidraw-plugin/releases/tag/2.0.0",
  "elements": [
    {
      "id": "node-input_left",
      "type": "rectangle",
      "x": 0.0,
      "y": 240.0,
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
      "seed": 1373158607,
      "version": 1,
      "versionNonce": 239081664,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-input_left",
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
      "id": "text-input_left",
      "type": "text",
      "x": -44.8,
      "y": 260.0,
      "width": 249.6,
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
      "text": "Long input /\nlarge history",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-input_left",
      "originalText": "Long input /\nlarge history",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-input_right",
      "type": "rectangle",
      "x": 0.0,
      "y": 720.0,
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
      "seed": 590620972,
      "version": 1,
      "versionNonce": 525901257,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-input_right",
          "type": "text"
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
      "id": "text-input_right",
      "type": "text",
      "x": -44.8,
      "y": 740.0,
      "width": 249.6,
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
      "text": "Long input /\nlarge history",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-input_right",
      "originalText": "Long input /\nlarge history",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-header_left",
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
      "seed": 1581559893,
      "version": 1,
      "versionNonce": 220106708,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-header_left",
          "type": "text"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-header_left",
      "type": "text",
      "x": 270.4,
      "y": 20.0,
      "width": 259.2,
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
      "text": "ROUTE A: Memory Engineering",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-header_left",
      "originalText": "ROUTE A: Memory Engineering",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-header_right",
      "type": "rectangle",
      "x": 320.0,
      "y": 480.0,
      "width": 160.0,
      "height": 60.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
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
          "id": "text-header_right",
          "type": "text"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-header_right",
      "type": "text",
      "x": 256.0,
      "y": 500.0,
      "width": 288.0,
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
      "text": "ROUTE B: Long-Context Training",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-header_right",
      "originalText": "ROUTE B: Long-Context Training",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-llm_a",
      "type": "rectangle",
      "x": 320.0,
      "y": 120.0,
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
          "id": "text-llm_a",
          "type": "text"
        },
        {
          "id": "arrow-0",
          "type": "arrow"
        },
        {
          "id": "arrow-2",
          "type": "arrow"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-llm_a",
      "type": "text",
      "x": 236.8,
      "y": 140.0,
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
      "seed": 63989048,
      "version": 1,
      "versionNonce": 201209006,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Pretrained LLM\n(any off-the-shelf)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-llm_a",
      "originalText": "Pretrained LLM\n(any off-the-shelf)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-mem",
      "type": "rectangle",
      "x": 640.0,
      "y": 120.0,
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
      "seed": 469521478,
      "version": 1,
      "versionNonce": 499635469,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-mem",
          "type": "text"
        },
        {
          "id": "arrow-1",
          "type": "arrow"
        },
        {
          "id": "arrow-3",
          "type": "arrow"
        },
        {
          "id": "arrow-4",
          "type": "arrow"
        }
      ],
      "updated": 1,
      "link": null,
      "locked": false
    },
    {
      "id": "text-mem",
      "type": "text",
      "x": 403.2,
      "y": 140.0,
      "width": 633.6,
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
      "text": "External Memory\n(vector DB / KV cache /\npaging / skills / schemas)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-mem",
      "originalText": "External Memory\n(vector DB / KV cache /\npaging / skills / schemas)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-paging",
      "type": "rectangle",
      "x": 640.0,
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
      "seed": 56985562,
      "version": 1,
      "versionNonce": 1205264596,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-paging",
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
      "id": "text-paging",
      "type": "text",
      "x": 518.4,
      "y": 340.0,
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
      "text": "function-call paging\n[MemGPT, Packer 2023]",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-paging",
      "originalText": "function-call paging\n[MemGPT, Packer 2023]",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-retrieve",
      "type": "rectangle",
      "x": 320.0,
      "y": 320.0,
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
        "type": 3
      },
      "seed": 1395616197,
      "version": 1,
      "versionNonce": 1506083911,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-retrieve",
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
      "id": "text-retrieve",
      "type": "text",
      "x": 256.0,
      "y": 340.0,
      "width": 288.0,
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
      "text": "retrieve / read /\nmanage cycle",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-retrieve",
      "originalText": "retrieve / read /\nmanage cycle",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-ctx_a",
      "type": "diamond",
      "x": 960.0,
      "y": 200.0,
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
      "seed": 473392625,
      "version": 1,
      "versionNonce": 964669078,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-ctx_a",
          "type": "text"
        },
        {
          "id": "arrow-5",
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
      "id": "text-ctx_a",
      "type": "text",
      "x": 790.4,
      "y": 220.0,
      "width": 499.2,
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
      "text": "Working Context\n(retrieved snippets +\nsystem prompt)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-ctx_a",
      "originalText": "Working Context\n(retrieved snippets +\nsystem prompt)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-data",
      "type": "rectangle",
      "x": 320.0,
      "y": 600.0,
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
      "seed": 1738238662,
      "version": 1,
      "versionNonce": 1866808230,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-data",
          "type": "text"
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
      "id": "text-data",
      "type": "text",
      "x": 217.6,
      "y": 620.0,
      "width": 364.8,
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
      "text": "Long-context data\n(millions of tokens)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-data",
      "originalText": "Long-context data\n(millions of tokens)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-rl",
      "type": "rectangle",
      "x": 640.0,
      "y": 600.0,
      "width": 160.0,
      "height": 60.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#ffc9c9",
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
      "boundElements": [
        {
          "id": "text-rl",
          "type": "text"
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
      "id": "text-rl",
      "type": "text",
      "x": 475.20000000000005,
      "y": 620.0,
      "width": 489.59999999999997,
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
      "text": "Multi-stage RL\nDPO -> GRPO/PPO\n[LongAgent, Hu 2024]",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-rl",
      "originalText": "Multi-stage RL\nDPO -> GRPO/PPO\n[LongAgent, Hu 2024]",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-llm_b",
      "type": "rectangle",
      "x": 640.0,
      "y": 800.0,
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
      "seed": 730682428,
      "version": 1,
      "versionNonce": 596724165,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-llm_b",
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
      "id": "text-llm_b",
      "type": "text",
      "x": 552.0,
      "y": 820.0,
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
      "seed": 333889689,
      "version": 1,
      "versionNonce": 462382782,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Trained 7B LLM\n(uses 128K directly)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-llm_b",
      "originalText": "Trained 7B LLM\n(uses 128K directly)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-ctx_b",
      "type": "diamond",
      "x": 960.0,
      "y": 700.0,
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
      "seed": 2055599410,
      "version": 1,
      "versionNonce": 1639591160,
      "isDeleted": false,
      "boundElements": [
        {
          "id": "text-ctx_b",
          "type": "text"
        },
        {
          "id": "arrow-9",
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
      "id": "text-ctx_b",
      "type": "text",
      "x": 814.4,
      "y": 720.0,
      "width": 451.2,
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
      "text": "Working Context\n(model attends to\nits own 128K)",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-ctx_b",
      "originalText": "Working Context\n(model attends to\nits own 128K)",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "node-tradeoff",
      "type": "rectangle",
      "x": 640.0,
      "y": 940.0,
      "width": 160.0,
      "height": 60.0,
      "angle": 0,
      "strokeColor": "#1e1e1e",
      "backgroundColor": "#fff3bf",
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
      "boundElements": [
        {
          "id": "text-tradeoff",
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
      "id": "text-tradeoff",
      "type": "text",
      "x": 355.2,
      "y": 960.0,
      "width": 729.6,
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
      "text": "Trade-off:\nA: flexible schema, slow paging\nB: fast inference, no flexibility",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "middle",
      "containerId": "node-tradeoff",
      "originalText": "Trade-off:\nA: flexible schema, slow paging\nB: fast inference, no flexibility",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-0",
      "type": "arrow",
      "x": 160.0,
      "y": 270.0,
      "width": 160.0,
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
          -120.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-input_left",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-llm_a",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-0",
      "type": "text",
      "x": 218.0,
      "y": 194.0,
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
      "seed": 1296491778,
      "version": 1,
      "versionNonce": 568054228,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "feeds",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "feeds",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-1",
      "type": "arrow",
      "x": 160.0,
      "y": 270.0,
      "width": 480.0,
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
          480.0,
          -120.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-input_left",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-mem",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-1",
      "type": "text",
      "x": 347.2,
      "y": 194.0,
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
      "seed": 1567087081,
      "version": 1,
      "versionNonce": 986607412,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "offloaded to",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "offloaded to",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-2",
      "type": "arrow",
      "x": 480.0,
      "y": 150.0,
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
          200.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-llm_a",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-paging",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-2",
      "type": "text",
      "x": 529.2,
      "y": 234.0,
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
      "seed": 2089750183,
      "version": 1,
      "versionNonce": 1980614225,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "queries",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "queries",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-3",
      "type": "arrow",
      "x": 640.0,
      "y": 350.0,
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
          -200.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-paging",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-mem",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-3",
      "type": "text",
      "x": 689.2,
      "y": 234.0,
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
      "seed": 1185498233,
      "version": 1,
      "versionNonce": 629595553,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "page-in",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "page-in",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-4",
      "type": "arrow",
      "x": 640.0,
      "y": 150.0,
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
          -160.0,
          200.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-mem",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-retrieve",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-4",
      "type": "text",
      "x": 538.0,
      "y": 234.0,
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
      "id": "arrow-5",
      "type": "arrow",
      "x": 480.0,
      "y": 350.0,
      "width": 480.0,
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
          480.0,
          -120.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-retrieve",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-ctx_a",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-5",
      "type": "text",
      "x": 684.8,
      "y": 274.0,
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
      "seed": 1239854304,
      "version": 1,
      "versionNonce": 412936599,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "assemble",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "assemble",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-6",
      "type": "arrow",
      "x": 160.0,
      "y": 750.0,
      "width": 160.0,
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
          160.0,
          -120.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-input_right",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-data",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-6",
      "type": "text",
      "x": 174.0,
      "y": 674.0,
      "width": 132.0,
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
      "text": "training corpus",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "training corpus",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-7",
      "type": "arrow",
      "x": 480.0,
      "y": 630.0,
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
      "seed": 489407816,
      "version": 1,
      "versionNonce": 1660151622,
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
        "elementId": "node-data",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-rl",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-7",
      "type": "text",
      "x": 520.4,
      "y": 614.0,
      "width": 79.2,
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
      "seed": 621455911,
      "version": 1,
      "versionNonce": 2115747111,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "fine-tune",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "fine-tune",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-8",
      "type": "arrow",
      "x": 640.0,
      "y": 630.0,
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
      "seed": 171351961,
      "version": 1,
      "versionNonce": 1836780820,
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
        "elementId": "node-rl",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-llm_b",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-8",
      "type": "text",
      "x": 693.6,
      "y": 714.0,
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
      "seed": 499914621,
      "version": 1,
      "versionNonce": 1860759514,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "yields",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "yields",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-9",
      "type": "arrow",
      "x": 800.0,
      "y": 830.0,
      "width": 160.0,
      "height": 100.0,
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
      "seed": 216898921,
      "version": 1,
      "versionNonce": 816314860,
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
          -100.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-llm_b",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-ctx_b",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-9",
      "type": "text",
      "x": 844.8,
      "y": 764.0,
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
      "seed": 596943773,
      "version": 1,
      "versionNonce": 973691210,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "one-pass",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "one-pass",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-10",
      "type": "arrow",
      "x": 960.0,
      "y": 230.0,
      "width": 160.0,
      "height": 740.0,
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
      "seed": 1365121944,
      "version": 1,
      "versionNonce": 1791238512,
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
          740.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-ctx_a",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-tradeoff",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-10",
      "type": "text",
      "x": 849.2,
      "y": 584.0,
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
      "seed": 783471137,
      "version": 1,
      "versionNonce": 349297013,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Route A",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "Route A",
      "lineHeight": 1.25,
      "baseline": 18
    },
    {
      "id": "arrow-11",
      "type": "arrow",
      "x": 960.0,
      "y": 730.0,
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
      "seed": 794957573,
      "version": 1,
      "versionNonce": 762938026,
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
          240.0
        ]
      ],
      "lastCommittedPoint": null,
      "startBinding": {
        "elementId": "node-ctx_b",
        "focus": 0,
        "gap": 2
      },
      "endBinding": {
        "elementId": "node-tradeoff",
        "focus": 0,
        "gap": 2
      },
      "startArrowhead": null,
      "endArrowhead": "arrow"
    },
    {
      "id": "text-edge-11",
      "type": "text",
      "x": 849.2,
      "y": 834.0,
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
      "seed": 449912920,
      "version": 1,
      "versionNonce": 1439190227,
      "isDeleted": false,
      "boundElements": [],
      "updated": 1,
      "link": null,
      "locked": false,
      "text": "Route B",
      "fontSize": 16,
      "fontFamily": 1,
      "textAlign": "center",
      "verticalAlign": "top",
      "containerId": null,
      "originalText": "Route B",
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
