# Forge and Quilt — the synergy, and where it stops

Read against [cloudflare/forge](https://github.com/cloudflare/forge) and the Cloudflare
launch post, with the first draft of the cell kernel as an OpenAPI 3.1 spec in
[`openapi.yaml`](openapi.yaml).

## First, the part the blog does not tell you

The launch post lists SDKs in TypeScript, Rust, Python, Go, PHP; plus CLIs, docs, MCP
servers, Cap'n Web specs, and Zod schemas. The repository says something narrower, and the
difference matters before anyone builds on it:

> *"It's still early-days for Forge and we're laser focused on the first Forge output, the
> cf CLI. Rest assured, in short order we'll be making it easier and easier for other
> targets (namely, TypeScript, Go, Python, Terraform, etc. …) but that will track in
> parallel to us releasing those targets for our own SDKs."*

What is in the repo today: the core engine (OpenAPI 3.x resolver, typed schema model,
**JSONPath overlays**, plugin lifecycle), a Fern-based docs engine, and nine SDK **wrapper**
packages for Cloudflare's own API (`cloudflare-forge-sdk-{ts,go,java,php,csharp,python,ruby,rust,swift}`).

So: **the engine is real and Apache-2.0. Arbitrary-spec generation into arbitrary
languages is the direction, not the shipped product.** MCP-server and multi-language
generation should be read as roadmap.

**This does not weaken the plan. It relocates the value.** The durable artifact is not a
generated SDK — generated code is disposable. It is **the spec**. That is worth writing
whether or not Forge ever becomes easy to point at your own OpenAPI document, and it is
worth writing precisely *because* the generators are young.

## The synergy that actually matters

**The polyformalism claim changes kind.**

Today the claim is: *the same kernel, hand-written in N languages, kept in sync by
discipline, verified by a canary.* That is **five synchronisation hazards wearing one
claim.** The canary is the only thing standing between the ports and drift, and it cannot
detect a port that was never run.

If the kernel is **specified** rather than implemented:

- the ports become build artifacts, not promises
- the canary becomes a **field in the spec** — `const "024a555471370b18d"` with
  `conformanceOnly: true` — inherited by every generated surface
- a port that drifts fails a **build**, not a review someone has to remember to do

The canary does not stop being the check. It stops being the *only* thing.

## The overlays are the part nobody expects

Forge's distinguishing primitive is **JSONPath-based overlays** on top of a resolved
OpenAPI document. That maps onto the fleet's hardest structural problem better than the
SDK generation does.

The fleet carries **two ecosystems that must stay separate** — the 24-repo polyformalism
substrate (six opcodes, C99) and the typed/cloud runtimes (different cell-kind
vocabularies) — plus **five adopted opcodes** on top of the six proved ones.

That is exactly the shape of an overlay: one base kernel, a small number of overlays that
add or hide operations, and a record of which overlay a given surface was built with. The
spec models the ecosystem split as a `Flavour` enum (`polyformalism` | `runtime`) rather
than as two documents, because **two documents would drift, and the whole point of keeping
them separate is that they do not share a vocabulary.**

## The MCP-server angle, and why it lands here specifically

The launch post's line is that AI agents are customers of generated APIs. The fleet's
consumers *are* LLM agents — Wesley the Mechanic, Snowball the Scout, and the rest.

A generated MCP server for the cell kernel means an agent can `BIND`, `LINK`, `EFFECT`,
`VIEW`, `TICK` a quilt without anyone hand-writing an integration per agent. That is a
genuine capability, and it is worth a prototype once the MCP target ships.

It is also worth being honest that this is the **most speculative** item here, because it
depends on the least-shipped part of Forge.

## The preview-build angle, which is a lesson from tonight

Forge generates **preview builds on every pull request**, with only the changed parts
highlighted. That is not a nice-to-have for this fleet. It is the mechanism that would have
caught two of tonight's defects before they merged:

- the `casey-digennaro` link in `browse.html` — a generated docs build resolves every link
- the `.gitignore` rule that read as correct and matched nothing — a build would have
  committed the file anyway and the diff would have shown it

Both were caught only by manual inspection, hours later, one of them on a **public
credential**. A preview build turns "someone has to remember" into "the pipeline refuses."

## Where the synergy stops — the honest part

**Forge generates surfaces. It does not generate semantics.** Specifically:

- **The canary is conformance, not integrity.** The spec says so in the schema
  (`conformanceOnly: true`) because it is the thing I got wrong tonight: I used FNV-1a for
  per-tensor tamper evidence and it is the wrong hash for that job. Generated SDKs inherit
  a conformance check, not a security one. Anything integrity-critical stays BLAKE2b-256.
- **The statistical half is not in the spec at all.** E-processes, the Ville bound, model
  versioning, the error budget — none of that is expressible as an OpenAPI operation. It
  is doctrine that the generated surfaces *carry* and cannot itself be generated.
- **The substrate still needs its own tests.** A generated SDK for `POST /cells/{id}/bottles`
  does not prove the cell conserves anything. The spec can state the rule; only running it
  checks it.
- **The spec is a commitment, and commitments rot.** A spec that drifts from the
  implementation is worse than no spec, because now there are two things to be wrong. It
  needs the same treatment the witness chain needs: a check that the implementation
  satisfies the document, run in CI.

## The one test worth running

Point Forge at `openapi.yaml` and see what comes out. Not because the output will be
production-ready — it will not, not yet — but because **the spec's fitness as a generator
input is an empirical question and I have been guessing at it.** If Forge chokes on
something, that is a finding about the spec, and the spec is the thing worth getting right.

The failure modes to watch for, in order of likelihood:
1. **The `oneOf: [null, integer]` on `Verdict.firstBreak`** — nullable unions are where
   generators most often produce a type that does not compile. If it breaks, a
   `firstBreak: {present: boolean, id: integer|null}` is uglier and safer.
2. **`contentEncoding: base64` on the bottle payload** — support varies.
3. **The reserved word `state`** appearing in a generated `state` field in a language where
   that is not reserved, and is in another.

## Order

1. **Keep the spec.** It is valid (10/10 structural checks) and it is the durable artifact.
2. **Run Forge at it** and treat the output as evidence about the spec.
3. **Add the e-process surface** as a separate concern — it is doctrine, not API.
4. **Wire a CI check** that the implementations satisfy the document, so the spec cannot
   quietly become fiction.

The strongest version of this is not "we adopted Forge." It is: **the fleet's central
architectural claim stopped being a habit and became an artifact that either builds or
does not.**
