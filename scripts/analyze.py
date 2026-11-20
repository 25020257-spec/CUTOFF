#!/usr/bin/env python3
"""Thống kê + vẽ đồ thị từ results/raw_*.csv  ->  results/*.csv, results/*.md, results/fig_*.png
Dùng: python3 scripts/analyze.py
"""
import glob, os, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

R = "results"
BLUE, ORANGE, AQUA, INK, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#aaa", "axes.grid": True, "grid.color": "#e6e6e3",
                     "axes.titleweight": "bold", "figure.dpi": 130})

df = pd.concat([pd.read_csv(f) for f in sorted(glob.glob(f"{R}/raw_*.csv"))], ignore_index=True)
df["ms"] = df["nanos"] / 1e6
CUT = sorted(df.cutoff.unique())

def ci95(x):
    x = np.asarray(x); n = len(x)
    return stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / np.sqrt(n)

# ---------- 1. bảng tóm tắt theo (mode,type,n,cutoff) ----------
rows = []
for (m, t, n, c), g in df.groupby(["mode", "type", "n", "cutoff"]):
    rows.append(dict(mode=m, type=t, n=n, cutoff=c, runs=len(g), mean_ms=g.ms.mean(),
                     ci95_ms=ci95(g.ms), median_ms=g.ms.median(), std_ms=g.ms.std(ddof=1),
                     min_ms=g.ms.min()))
S = pd.DataFrame(rows)
S["rel_mean"] = S.groupby(["mode", "type", "n"]).mean_ms.transform(lambda x: x / x.min())
S["rel_median"] = S.groupby(["mode", "type", "n"]).median_ms.transform(lambda x: x / x.min())
S.to_csv(f"{R}/summary_all.csv", index=False, float_format="%.4f")

# ---------- 2. so sánh cặp với cutoff tốt nhất (paired theo file+round) ----------
def paired_vs_best(g):
    """g: dữ liệu 1 (mode,type,n). Trả về bảng chênh lệch ghép cặp so với cutoff có trung vị thấp nhất."""
    piv = g.pivot_table(index=["file", "round"], columns="cutoff", values="ms")
    best = piv.median().idxmin()
    out = []
    for c in piv.columns:
        d = (piv[c] - piv[best]).dropna()          # >0: chậm hơn best
        if c == best:
            out.append(dict(cutoff=c, best=best, diff_ms=0, lo=0, hi=0, p=np.nan, pct=0, tie=True)); continue
        h = ci95(d); p = stats.wilcoxon(d).pvalue
        out.append(dict(cutoff=c, best=best, diff_ms=d.mean(), lo=d.mean() - h, hi=d.mean() + h, p=p,
                        pct=100 * d.mean() / piv[best].mean(), tie=(d.mean() - h) <= 0))
    return pd.DataFrame(out)
P = []
for (m, t, n), g in df.groupby(["mode", "type", "n"]):
    r = paired_vs_best(g); r.insert(0, "n", n); r.insert(0, "type", t); r.insert(0, "mode", m); P.append(r)
P = pd.concat(P); P.to_csv(f"{R}/paired_vs_best.csv", index=False, float_format="%.5f")

# ---------- 3. bảng markdown cho báo cáo ----------
def md_table(mode, typ, n, cuts=None):
    s = S[(S["mode"] == mode) & (S.type == typ) & (S.n == n)].set_index("cutoff")
    p = P[(P["mode"] == mode) & (P.type == typ) & (P.n == n)].set_index("cutoff")
    best = int(p.best.iloc[0])
    L = ["| CUTOFF | Trung bình (ms) | ±CI95 | Trung vị (ms) | Độ lệch chuẩn | So với tốt nhất (%) | Phân biệt được? |",
         "|---:|---:|---:|---:|---:|---:|:--|"]
    for c in (cuts or CUT):
        r, q = s.loc[c], p.loc[c]
        flag = "**tốt nhất**" if c == best else ("không (CI chứa 0)" if q.tie else f"có (p={q.p:.1e})")
        L.append(f"| {c} | {r.mean_ms:.2f} | {r.ci95_ms:.2f} | {r.median_ms:.2f} | {r.std_ms:.2f} | {q.pct:+.1f} | {flag} |")
    return "\n".join(L)
with open(f"{R}/tables.md", "w", encoding="utf-8") as f:
    for (m, t, n), _ in df.groupby(["mode", "type", "n"]):
        f.write(f"### {m} / {t} / n={n:,}\n\n{md_table(m, t, n)}\n\n")

# ---------- 4. bảng kết luận ----------
C = []
for (m, t, n), g in P.groupby(["mode", "type", "n"]):
    s = S[(S["mode"] == m) & (S.type == t) & (S.n == n)].set_index("cutoff")
    best = int(g.best.iloc[0]); ties = [int(c) for c in g[g.tie].cutoff]
    C.append(dict(mode=m, type=t, n=n, best_by_median=best, best_by_mean=int(s.mean_ms.idxmin()),
                  indistinguishable_from_best=f"{min(ties)}-{max(ties)}" if len(ties) > 1 else str(best),
                  n_ties=len(ties), rel_c1=s.loc[1, "mean_ms"] / s.mean_ms.min(),
                  rel_c7=s.loc[7, "mean_ms"] / s.mean_ms.min(), rel_c10=s.loc[10, "mean_ms"] / s.mean_ms.min(),
                  gain_vs_pure_pct=100 * (1 - s.mean_ms.min() / s.loc[1, "mean_ms"])))
C = pd.DataFrame(C); C.to_csv(f"{R}/conclusions.csv", index=False, float_format="%.4f")

# ---------- 5. gộp mọi n: trung bình hình học của thời gian tương đối (random) ----------
def pooled(mode):
    s = S[(S["mode"] == mode) & (S.type == "random")]
    return s.groupby("cutoff").rel_median.apply(lambda x: np.exp(np.log(x).mean()))
pool = pd.DataFrame({"boxed": pooled("boxed"), "prim": pooled("prim")}); pool.to_csv(f"{R}/pooled_random.csv", float_format="%.4f")

# ---------- đồ thị ----------
def xaxis(ax):
    ax.set_xscale("log", base=2); ax.set_xticks([1, 2, 4, 7, 10, 16, 32, 64, 128])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.set_xlabel("CUTOFF (kích thước đoạn tối đa dùng insertion sort)")
    for v, c in ((7, MUTED), (10, MUTED)): ax.axvline(v, color=c, lw=0.8, ls=":")

# Hình 1: thời gian tuyệt đối theo cutoff, 3 kích thước, boxed
fig, axs = plt.subplots(1, 3, figsize=(13, 3.8))
for ax, n in zip(axs, (10_000, 100_000, 1_000_000)):
    s = S[(S["mode"] == "boxed") & (S.type == "random") & (S.n == n)].sort_values("cutoff")
    ax.plot(s.cutoff, s.mean_ms, color=BLUE, lw=2, marker="o", ms=4)
    ax.fill_between(s.cutoff, s.mean_ms - s.ci95_ms, s.mean_ms + s.ci95_ms, color=BLUE, alpha=0.2, lw=0)
    b = s.loc[s.mean_ms.idxmin()]; ax.scatter([b.cutoff], [b.mean_ms], s=60, color=ORANGE, zorder=5)
    ax.annotate(f"min: {int(b.cutoff)}", (b.cutoff, b.mean_ms), textcoords="offset points", xytext=(6, 8), color=INK)
    ax.set_title(f"n = {n:,}"); ax.set_ylabel("thời gian (ms)"); xaxis(ax)
    lo, hi = s.mean_ms.min(), s.mean_ms.max(); ax.set_ylim(lo * 0.97, min(hi, lo * 1.4) * 1.03)
fig.suptitle("Mergesort (Integer[]) - thời gian trung bình ± CI95 theo CUTOFF, dữ liệu ngẫu nhiên", y=1.02, fontweight="bold")
fig.tight_layout(); fig.savefig(f"{R}/fig1_time_vs_cutoff_boxed.png", bbox_inches="tight"); plt.close(fig)

# Hình 2: thời gian tương đối (trung vị / trung vị nhỏ nhất) cho cả 3 n + gộp, boxed vs prim
fig, axs = plt.subplots(1, 2, figsize=(11, 3.9), sharey=True)
cols = {10_000: AQUA, 100_000: ORANGE, 1_000_000: BLUE}
for ax, mode, ttl in zip(axs, ("boxed", "prim"), ("Integer[] (đối tượng, so sánh qua compareTo)", "int[] (kiểu nguyên thuỷ)")):
    for n, col in cols.items():
        s = S[(S["mode"] == mode) & (S.type == "random") & (S.n == n)].sort_values("cutoff")
        ax.plot(s.cutoff, s.rel_median, color=col, lw=1.8, marker="o", ms=3, label=f"n = {n:,}")
    ax.set_title(ttl, fontsize=10); xaxis(ax); ax.set_ylim(0.95, 1.35)
    ax.legend(frameon=False, loc="upper left")
axs[0].set_ylabel("trung vị / trung vị nhỏ nhất (1.0 = tốt nhất)")
fig.tight_layout(); fig.savefig(f"{R}/fig2_relative_boxed_vs_prim.png", bbox_inches="tight"); plt.close(fig)

# Hình 3: chênh lệch ghép cặp so với cutoff tốt nhất (boxed, n=1e6 và 1e5) - vùng "không phân biệt được"
fig, axs = plt.subplots(1, 2, figsize=(11, 3.8))
for ax, n in zip(axs, (100_000, 1_000_000)):
    p = P[(P["mode"] == "boxed") & (P.type == "random") & (P.n == n)].sort_values("cutoff")
    best = int(p.best.iloc[0]); ax.set_title(f"n = {n:,} (so với CUTOFF = {best})")
    m = S[(S["mode"] == "boxed") & (S.type == "random") & (S.n == n)].set_index("cutoff").mean_ms
    scale = 100 / m[best]
    ax.errorbar(p.cutoff, p.diff_ms * scale, yerr=[(p.diff_ms - p.lo) * scale, (p.hi - p.diff_ms) * scale],
                fmt="o", color=BLUE, ecolor=BLUE, capsize=2, ms=4)
    ax.axhline(0, color=INK, lw=0.8); ax.set_ylabel("chậm hơn tốt nhất (%) ± CI95 ghép cặp"); xaxis(ax)
    ax.set_ylim(-3, 30)
fig.tight_layout(); fig.savefig(f"{R}/fig3_paired_diff.png", bbox_inches="tight"); plt.close(fig)

# Hình 4: độ nhạy theo kiểu dữ liệu (boxed, extra, n=1e6 & 1e5) + random
fig, axs = plt.subplots(1, 2, figsize=(11, 3.9), sharey=False)
typ_style = {"random": (BLUE, "ngẫu nhiên"), "fewdistinct": (ORANGE, "10 giá trị khác nhau"),
             "nearlysorted": (AQUA, "gần như đã sắp"), "reversed": ("#6250d6", "giảm dần")}
for ax, n in zip(axs, (100_000, 1_000_000)):
    for t, (col, lab) in typ_style.items():
        s = S[(S["mode"] == "boxed") & (S.type == t) & (S.n == n)].sort_values("cutoff")
        if len(s): ax.plot(s.cutoff, s.rel_median, color=col, lw=1.8, marker="o", ms=3, label=lab)
    ax.set_title(f"n = {n:,}"); ax.set_ylabel("trung vị / trung vị nhỏ nhất"); xaxis(ax); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(f"{R}/fig4_data_types.png", bbox_inches="tight"); plt.close(fig)

print(C.to_string()); print(pool.round(3).to_string())
