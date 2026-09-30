# forge-quilt — the cell kernel as an API

Cloudflare [Forge](https://github.com/cloudflare/forge) is a schema-first OpenAPI
generation pipeline. The Quilt cell kernel is currently hand-written in N languages and
kept in sync by discipline. This makes the kernel a **document** instead, which is Forge's
actual input — and which is the durable artifact regardless of how mature the generators get.

```
openapi.yaml      10 paths, 19 schemas, the kernel as OpenAPI 3.1
validate.py       10 structural checks
SYNERGY.md        what Forge changes, and where the synergy stops
```

```
python3 validate.py     # 10/10
```

`validate.py` exists because the first draft of `openapi.yaml` shipped with **every
`$ref` pointing at a `components:` section that did not exist yet** — a dangling reference
is a build failure several layers downstream, in someone else's language. So: all 25 refs
resolve, all 12 operations have an `operationId` and a 2xx, no schema is unreachable, the
canary is pinned, and the `Ternary` enum has no default (clamping would be how a
conservation law quietly stops conserving).

## What is in the spec, and why each thing is there

- **`/cells`, `/cells/{id}/bottles`, `/cells/{id}/state`** — the lifecycle. `receiveBottle`
  returns **422 with a `Refusal`** when γ+η leaves `{-1,0,+1}`, because a refusal that
  returns nothing is indistinguishable from an event that did not happen.
- **`/graph/links`, `/graph/tick`** — LINK is directed; TICK is the only thing that advances
  state, which is what makes a bottle sequence replayable.
- **`/witness/chain`, `/witness/verify`, `/witness/anchored-head`** — the chain, the
  **first** break (an auditor wants the earliest, not a count), and the external anchor.
  Without the anchor a chain detects accidental corruption and nothing else.
- **`/integrity/canary`** — the polyformalism contract as a pinned `const`, carrying
  `conformanceOnly: true` because FNV-1a is a **conformance** hash and using it for tamper
  evidence is a category error. The accent in the fixture is load-bearing.

## The claim this changes

The polyformalism claim goes from *"the same kernel in N languages, kept in sync by
discipline"* — which is N synchronisation hazards wearing one claim — to *"one spec, and the
ports are build artifacts."* The canary does not stop being the check; it stops being the
only thing between the ports and drift.
