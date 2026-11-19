"""List FlyWire neurons (registered to JRC2018U) for each model cell type, as JSON.
usage: python -I list_neurons.py out.json
"""
import sys, json, base64, urllib.request

CLASSES = {  # model key: (VFB class id, max candidates)
    "orn_e": ("FBbt_00067046", 30), "orn_g": ("FBbt_00067063", 30),
    "pn_e": ("FBbt_00067369", 10), "pn_g": ("FBbt_00110882", 10),
    "lh": ("FBbt_00049286", 40),
    "kc_g": ("FBbt_00049828", 60), "kc_ab": ("FBbt_00100248", 60), "kc_apbp": ("FBbt_00049834", 60),
    "mbon_a": ("FBbt_00100246", 10), "mbon_v": ("FBbt_00100234", 10),
    "pam": ("FBbt_00100230", 20), "pam2": ("FBbt_00100231", 20), "pam3": ("FBbt_00111015", 20),
    "ppl_a": ("FBbt_00110320", 10), "ppl_ap": ("FBbt_00110321", 10),
    "lplc2": ("FBbt_00111763", 40), "lc10": ("FBbt_00111747", 40),
    "gf": ("FBbt_00004020", 10), "dna02": ("FBbt_00047573", 10),
    "grn": ("FBbt_00110887", 40),
}
Q = """MATCH (c:Class {short_form:$cls})<-[:SUBCLASSOF*0..4]-(:Class)<-[:INSTANCEOF]-(i:Individual)<-[:depicts]-(ch)-[r:in_register_with]->(tc)-[:depicts]->(t {short_form:'VFB_00101567'})
WHERE i.label CONTAINS 'FlyWire' RETURN DISTINCT i.short_form, i.label, r.folder[0] LIMIT $n"""
auth = base64.b64encode(b"neo4j:vfb").decode()
out = {}
for key, (cls, n) in CLASSES.items():
    body = json.dumps({"statements": [{"statement": Q, "parameters": {"cls": cls, "n": n}}]}).encode()
    req = urllib.request.Request("https://pdb.virtualflybrain.org/db/neo4j/tx/commit", data=body,
                                 headers={"Content-Type": "application/json", "Authorization": "Basic " + auth})
    d = json.load(urllib.request.urlopen(req, timeout=120))
    rows = [r["row"] for r in d["results"][0]["data"]] if d["results"] else []
    out[key] = [{"id": a, "label": b, "folder": c} for a, b, c in rows]
    print(key, len(rows), rows[0][1] if rows else d.get("errors"))
json.dump(out, open(sys.argv[1], "w"), indent=1)
