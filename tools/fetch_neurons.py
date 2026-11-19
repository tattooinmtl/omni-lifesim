"""Download FlyWire skeletons (SWC, JRC2018U space) from VFB, pick N per brain side per cell type,
prune and resample them, and write compact base64 JSON for the page.
usage: python -I fetch_neurons.py neuron_list.json brain-meshes.json swc_dir out.json
"""
import sys, os, json, math, base64, array, urllib.request
from concurrent.futures import ThreadPoolExecutor

LIST, MESHES, SWC_DIR, OUT = sys.argv[1:5]
QUOTA = {"orn_e": 2, "orn_g": 2, "pn_e": 1, "pn_g": 1, "lh": 2, "kc_g": 5, "kc_ab": 5, "kc_apbp": 5,
         "mbon_a": 1, "mbon_v": 1, "pam": 1, "pam2": 1, "pam3": 1, "ppl_a": 1, "ppl_ap": 1,
         "lplc2": 3, "lc10": 2, "gf": 1, "dna02": 1, "grn": 2}
STEP, PRUNE = 3.0, 8.0  # resample spacing and minimum twig length, microns
cands = json.load(open(LIST))
mb = json.load(open(MESHES)); lo, hi = mb["bboxMin"], mb["bboxMax"]
midx = (lo[0] + hi[0]) / 2
os.makedirs(SWC_DIR, exist_ok=True)

def fetch(c):
    path = os.path.join(SWC_DIR, c["id"] + ".swc")
    if not os.path.exists(path):
        url = c["folder"].replace("http://", "https://") + "volume.swc"
        req = urllib.request.Request(url, headers={"User-Agent": "omni-lifesim-fetch/1.0"})
        data = urllib.request.urlopen(req, timeout=120).read()
        open(path, "wb").write(data)
    return path

def parse(path):
    nodes = {}
    for line in open(path, errors="ignore"):
        if not line.strip() or line.startswith("#"): continue
        t = line.split()
        nodes[int(t[0])] = (float(t[2]), float(t[3]), float(t[4]), int(t[6]))
    return nodes

def simplify(nodes):
    kids = {k: [] for k in nodes}
    roots = []
    for k, (_, _, _, p) in nodes.items():
        if p in nodes: kids[p].append(k)
        else: roots.append(k)
    root = max(roots, key=lambda r: sum(1 for _ in walk(r, kids)))  # biggest connected tree
    d = lambda a, b: math.dist(nodes[a][:3], nodes[b][:3])
    # prune short twigs (one pass)
    dead = set()
    for k in list(nodes):
        if kids[k] or k == root: continue
        length, cur = 0.0, k
        while True:
            p = nodes[cur][3]
            if p not in nodes: break
            length += d(cur, p); cur = p
            if len(kids[cur]) > 1 or cur == root: break
            if length > PRUNE: break
        if length < PRUNE and len(kids.get(cur, [])) > 1:
            c = k
            while c != cur: dead.add(c); c = nodes[c][3]
    # resample: keep root, branch points, leaves, and a node every STEP microns
    keep_pts, keep_par, keep_dist = [], [], []
    stack = [(root, -1, 0.0, 0.0)]  # node, kept parent index, path dist since kept, total dist
    while stack:
        k, kp, acc, tot = stack.pop()
        live = [c for c in kids[k] if c not in dead]
        if kp == -1 or len(live) != 1 or acc >= STEP:
            keep_pts.append(nodes[k][:3]); keep_par.append(kp); keep_dist.append(tot)
            kp, acc = len(keep_pts) - 1, 0.0
        for c in live:
            step = d(k, c); stack.append((c, kp, acc + step, tot + step))
    return keep_pts, keep_par, keep_dist

def walk(r, kids):
    st = [r]
    while st:
        k = st.pop(); yield k; st.extend(kids[k])

chosen = []
for key, quota in QUOTA.items():
    got = {"a": 0, "b": 0}
    pool = cands.get(key, [])
    for c in pool:
        if got["a"] >= quota and got["b"] >= quota: break
        try: nodes = parse(fetch(c))
        except Exception as e: print("skip", c["id"], e); continue
        if len(nodes) < 10: continue
        pts, par, dist = simplify(nodes)
        sx = pts[0][0]  # root: soma for most FlyWire skeletons
        side = "a" if sx < midx else "b"  # 'a' = smaller template x, same split as the region meshes
        if got[side] >= quota: continue
        got[side] += 1
        chosen.append({"key": key, "side": side, "id": c["id"], "label": c["label"], "pts": pts, "par": par, "dist": dist})
    print(f"{key:8s} a={got['a']} b={got['b']} of {len(pool)}")

allp = [p for n in chosen for p in n["pts"]]
nlo = [min(p[i] for p in allp) for i in range(3)]; nhi = [max(p[i] for p in allp) for i in range(3)]
out = {"bboxMin": nlo, "bboxMax": nhi, "source": "FlyWire skeletons via Virtual Fly Brain, JRC2018Unisex space", "neurons": []}
tot = 0
for n in chosen:
    q = array.array("H")
    for p in n["pts"]:
        for i in range(3): q.append(int(round((p[i] - nlo[i]) / (nhi[i] - nlo[i]) * 65535)))
    par = array.array("H", [65535 if x < 0 else x for x in n["par"]])
    md = max(n["dist"]) or 1
    dist = array.array("B", [int(x / md * 255) for x in n["dist"]])
    tot += len(n["pts"])
    out["neurons"].append({"key": n["key"], "side": n["side"], "id": n["id"], "label": n["label"], "n": len(n["pts"]),
                           "pos": base64.b64encode(q.tobytes()).decode(), "par": base64.b64encode(par.tobytes()).decode(),
                           "dist": base64.b64encode(dist.tobytes()).decode()})
json.dump(out, open(OUT, "w"), separators=(",", ":"))
print("neurons", len(chosen), "points", tot, "bytes", os.path.getsize(OUT), "bbox", nlo, nhi, "mesh bbox", lo, hi)
