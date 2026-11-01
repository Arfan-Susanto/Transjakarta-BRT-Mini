import csv, heapq, io, math, difflib
from pathlib import Path
from flask import Flask, jsonify, render_template, request, send_file
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
import networkx as nx

BASE = Path(__file__).parent
app = Flask(__name__)


def muat_graf():
    adj = {}
    with open(BASE / "data" / "jarak_halte_cleaned.csv", encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            u, v, w, k = r["dari"].strip(), r["ke"].strip(), float(r["jarak_m"]), str(r["rute"])
            adj.setdefault(u, {}); adj.setdefault(v, {})
            e = adj[u].get(v)
            if e:
                e["jarak"] = min(e["jarak"], w); e["koridor"].add(k)
            else:
                adj[u][v] = {"jarak": w, "koridor": {k}}
    return adj


ADJ = muat_graf()
HALTE = sorted(ADJ)


def rekon(par, a, b):
    p = [b]
    while p[-1] != a:
        p.append(par[p[-1]])
    return p[::-1]


def dfs(a, b):
    stack, par, seen, urut = [(a, None)], {}, set(), []
    while stack:
        n, induk = stack.pop()
        if n in seen:
            continue
        seen.add(n); par[n] = induk; urut.append(n)
        if n == b:
            return rekon(par, a, b), urut
        for t in sorted(ADJ[n], reverse=True):
            if t not in seen:
                stack.append((t, n))
    return None, urut


def dijkstra(a, b):
    dist = {n: math.inf for n in ADJ}; dist[a] = 0
    par, done, urut, pq = {a: None}, set(), [], [(0, a)]
    while pq:
        d, u = heapq.heappop(pq)
        if u in done:
            continue
        done.add(u); urut.append(u)
        if u == b:
            return rekon(par, a, b), urut
        for v, e in ADJ[u].items():
            nd = d + e["jarak"]
            if nd < dist[v]:
                dist[v] = nd; par[v] = u; heapq.heappush(pq, (nd, v))
    return None, urut


def ringkas(path, urut):
    seg = [{"dari": u, "ke": v, "koridor": "/".join(sorted(ADJ[u][v]["koridor"])),
            "km": round(ADJ[u][v]["jarak"] / 1000, 2)} for u, v in zip(path, path[1:])]
    total = sum(ADJ[u][v]["jarak"] for u, v in zip(path, path[1:]))
    pindah, cur = 0, None
    for u, v in zip(path, path[1:]):
        k = ADJ[u][v]["koridor"]
        if cur is None:
            cur = set(k)
        elif cur & k:
            cur &= k
        else:
            pindah += 1; cur = set(k)
    return {"path": path, "urutan": urut, "segmen": seg, "km": round(total / 1000, 2),
            "ruas": len(path) - 1, "pindah": pindah, "dikunjungi": len(urut)}


WARNA = {"2": "#2563EB", "4": "#9333EA", "5C": "#0D9488", "x": "#0f172a"}


def render_graf():
    G = nx.Graph()
    for u, t in ADJ.items():
        for v, d in t.items():
            if G.has_edge(u, v):
                G[u][v]["k"] |= d["koridor"]
            else:
                G.add_edge(u, v, k=set(d["koridor"]))
    pos = nx.kamada_kawai_layout(G, weight=None)
    W, H, DPI = 1200, 820, 100
    xs, ys = [p[0] for p in pos.values()], [p[1] for p in pos.values()]
    x0, x1, y0, y1 = min(xs) - .1, max(xs) + .1, min(ys) - .1, max(ys) + .1
    fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.axis("off")
    for u, v, d in G.edges(data=True):
        c = WARNA["x"] if len(d["k"]) > 1 else WARNA[next(iter(d["k"]))]
        ax.plot([pos[u][0], pos[v][0]], [pos[u][1], pos[v][1]], color=c, lw=2.2, solid_capstyle="round", zorder=1)
    hub = {n for n in G if len({k for m in G[n] for k in G[n][m]["k"]}) > 1}
    for n, (x, y) in pos.items():
        ax.scatter([x], [y], s=150 if n in hub else 70, c="#4ADE80" if n in hub else "white",
                   edgecolors="#1E3A8A", linewidths=1.8, zorder=3)
        ax.text(x, y + .03, n, fontsize=6.5, ha="center", va="bottom", color="#0f172a", zorder=4,
                path_effects=[pe.withStroke(linewidth=2.5, foreground="white")])
    buf = io.BytesIO(); fig.savefig(buf, format="png", dpi=DPI, transparent=True); plt.close(fig)
    px = {n: [round((x - x0) / (x1 - x0) * W, 1), round((1 - (y - y0) / (y1 - y0)) * H, 1)] for n, (x, y) in pos.items()}
    return buf.getvalue(), {"w": W, "h": H, "pos": px}


GRAF_PNG, GRAF_META = render_graf()


@app.get("/")
def index():
    return render_template("index.html", halte=HALTE, graf=GRAF_META)


@app.get("/graph.png")
def graph_png():
    return send_file(io.BytesIO(GRAF_PNG), mimetype="image/png")


@app.post("/api/rute")
def api_rute():
    d = request.get_json(silent=True) or {}
    a, b = (d.get("asal") or "").strip(), (d.get("tujuan") or "").strip()
    for n in (a, b):
        if n not in ADJ:
            s = difflib.get_close_matches(n, HALTE, n=3, cutoff=0.5)
            msg = f"Halte ‘{n}’ nggak ketemu." + (f" Maksud kamu: {', '.join(s)}?" if s else "")
            return jsonify(error=msg), 400
    out = {}
    for nama, fn in (("dijkstra", dijkstra), ("dfs", dfs)):
        path, urut = fn(a, b)
        out[nama] = ringkas(path, urut) if path else None
    if out["dijkstra"] and out["dfs"] and out["dijkstra"]["km"] > 0:
        out["dfs"]["lebih_persen"] = round((out["dfs"]["km"] - out["dijkstra"]["km"]) / out["dijkstra"]["km"] * 100, 1)
    return jsonify(out)


if __name__ == "__main__":
    app.run(debug=True)
