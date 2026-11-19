"""Vertex-clustering decimation of VFB OBJ meshes -> compact base64 JSON.
usage: python -I shrink.py <mesh_dir> <out.json>
"""
import sys, os, json, base64, struct, array

SRC, OUT = sys.argv[1], sys.argv[2]
# (file, label, cell size in microns)
MESHES = [
    ("brain", "Whole brain (JRC2018U template)", 6.0),
    ("AL", "Antennal lobe", 2.2), ("LH", "Lateral horn", 2.2),
    ("CA", "MB calyx", 2.0), ("PED", "MB peduncle", 2.0),
    ("aL", "MB α lobe", 2.0), ("apL", "MB α′ lobe", 2.0),
    ("bL", "MB β lobe", 2.0), ("bpL", "MB β′ lobe", 2.0), ("gL", "MB γ lobe", 2.0),
    ("ME", "Medulla", 4.5), ("LO", "Lobula", 3.5), ("LOP", "Lobula plate", 3.5),
    ("GNG", "Gnathal ganglia", 3.0),
]

def load(path):
    vs, fs = [], []
    with open(path) as f:
        for line in f:
            if line.startswith("v "):
                _, x, y, z = line.split()[:4]; vs.append((float(x), float(y), float(z)))
            elif line.startswith("f "):
                p = [int(t.split("/")[0]) - 1 for t in line.split()[1:]]
                for i in range(1, len(p) - 1): fs.append((p[0], p[i], p[i + 1]))
    return vs, fs

def cluster(vs, fs, cell):
    key2new, sums, remap = {}, [], []
    for x, y, z in vs:
        k = (int(x // cell), int(y // cell), int(z // cell))
        n = key2new.get(k)
        if n is None:
            n = len(sums); key2new[k] = n; sums.append([0.0, 0.0, 0.0, 0])
        s = sums[n]; s[0] += x; s[1] += y; s[2] += z; s[3] += 1
        remap.append(n)
    nv = [(s[0] / s[3], s[1] / s[3], s[2] / s[3]) for s in sums]
    seen, nf = set(), []
    for a, b, c in fs:
        a, b, c = remap[a], remap[b], remap[c]
        if a == b or b == c or a == c: continue
        key = tuple(sorted((a, b, c)))
        if key in seen: continue
        seen.add(key); nf.append((a, b, c))
    return nv, nf

loaded = {}
for name, _, _ in MESHES:
    loaded[name] = load(os.path.join(SRC, name + ".obj"))
# global bbox from whole brain + all regions
allv = [v for vs, _ in loaded.values() for v in vs]
lo = [min(v[i] for v in allv) for i in range(3)]
hi = [max(v[i] for v in allv) for i in range(3)]
out = {"bboxMin": lo, "bboxMax": hi, "units": "micrometres, JRC2018Unisex space", "meshes": []}
for name, label, cell in MESHES:
    vs, fs = loaded[name]
    nv, nf = cluster(vs, fs, cell)
    q = array.array("H")
    for v in nv:
        for i in range(3): q.append(int(round((v[i] - lo[i]) / (hi[i] - lo[i]) * 65535)))
    idx = array.array("H" if len(nv) < 65536 else "I")
    for f in nf: idx.extend(f)
    out["meshes"].append({"id": name, "label": label, "srcVerts": len(vs), "srcTris": len(fs),
        "verts": len(nv), "tris": len(nf), "idxType": idx.typecode,
        "pos": base64.b64encode(q.tobytes()).decode(), "idx": base64.b64encode(idx.tobytes()).decode()})
    print(f"{name:6s} {len(fs):7d} -> {len(nf):6d} tris")
with open(OUT, "w") as f: json.dump(out, f, separators=(",", ":"))
print("bytes", os.path.getsize(OUT), "bbox", lo, hi)
