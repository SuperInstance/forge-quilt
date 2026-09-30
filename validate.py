#!/usr/bin/env python3
"""
validate.py — does the spec actually hold together?

An OpenAPI document is consumed by a generator, not a human. A dangling $ref becomes a
build failure eight layers downstream, in someone else's language. So the checks are
structural, and the first one exists because I shipped a version with every $ref in it
pointing at nothing:

  1. every local $ref resolves
  2. every operation has an operationId (generators use them for method names)
  3. every operation has at least one success response
  4. every schema referenced by a path is reachable from components
  5. the canary is pinned, and the fixture is the accented one
"""
import sys, re, json
import yaml

doc = yaml.safe_load(open("openapi.yaml", encoding="utf-8"))
results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(f"  {'ok  ' if ok else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))

raw = open("openapi.yaml", encoding="utf-8").read()

# ---- 1. every local $ref resolves -------------------------------------------
refs = set(re.findall(r"\$ref:\s*'?(#/[^'\"]+)'?", raw))
def resolve(ref):
    node = doc
    for part in ref.lstrip("#/").split("/"):
        if not isinstance(node, dict) or part not in node: return False
        node = node[part]
    return True
dangling = sorted(r for r in refs if not resolve(r))
check(f"all {len(refs)} local $refs resolve", not dangling, "; ".join(dangling[:5]))

# ---- 2/3. operations ---------------------------------------------------------
ops = []
for path, item in doc["paths"].items():
    for method, op in item.items():
        if method in ("get","post","put","patch","delete"):
            ops.append((path, method, op))
missing_id = [f"{m.upper()} {p}" for p,m,o in ops if not o.get("operationId")]
check(f"all {len(ops)} operations have an operationId", not missing_id, "; ".join(missing_id[:4]))
no_ok = [f"{m.upper()} {p}" for p,m,o in ops
         if not any(str(c).startswith("2") for c in (o.get("responses") or {}))]
check(f"all {len(ops)} operations declare a 2xx response", not no_ok, "; ".join(no_ok[:4]))
dupes = [i for i in [o.get("operationId") for _,_,o in ops] if i]
check("operationIds are unique", len(dupes)==len(set(dupes)))

# ---- 4. schemas are reachable ------------------------------------------------
declared = set(doc["components"]["schemas"])
used = {r.split("/")[-1] for r in refs if r.startswith("#/components/schemas/")}
orphans = sorted(declared - used)
check("no schema is declared but unreachable", not orphans, ", ".join(orphans[:5]))

# ---- 5. the canary -----------------------------------------------------------
c = doc["components"]["schemas"]["Canary"]["properties"]
check("canary digest is pinned by const",
      c["digest"].get("const") == "024a555471370b18d", c["digest"].get("const",""))
check("the fixture is the ACCENTED one",
      c["fixture"].get("const") == "café Δ 日本語",
      repr(c["fixture"].get("const","")))
check("the spec says FNV is conformance-only, not tamper evidence",
      c["conformanceOnly"].get("const") is True)

# ---- 6. the ternary trap -----------------------------------------------------
t = doc["components"]["schemas"]["Ternary"]
check("Ternary is exactly {-1,0,+1} with no default",
      sorted(t["enum"]) == [-1,0,1] and "default" not in t)

# ---- 7. the no-deletion promise is stated where it binds ----------------------
check("CellId states that ids are never reused",
      "never reused" in doc["components"]["schemas"]["CellId"]["description"])

n = sum(1 for _,ok,_ in results if ok)
print(f"\n  {n}/{len(results)} checks pass")
json.dump([{"check":c_,"pass":ok,"detail":d} for c_,ok,d in results],
          open("validation.json","w"), indent=1)
sys.exit(0 if n==len(results) else 1)
