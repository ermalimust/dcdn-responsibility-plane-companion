#!/usr/bin/env python3
"""
Inter-coder reliability for the D0-D3 responsibility-plane rubric.

Usage:
    python compute_kappa.py coding_sheet_filled.csv
    python compute_kappa.py --selftest

Input CSV must have a header with columns: family, plane, and at least two
code columns whose names end in "_code" (e.g. coderA_code, coderB_code, ...).
Codes are D0/D1/D2/D3 (the leading 'D' is optional; 0/1/2/3 also accepted).

Stdlib only (no numpy/pandas). Reports:
  - exact and within-one-level percent agreement
  - Cohen's kappa: unweighted, linear-weighted, quadratic-weighted (2 coders)
  - bootstrap 95% CI for quadratic-weighted kappa
  - Krippendorff's ordinal alpha (any number of coders)
  - Fleiss' kappa + mean pairwise quadratic kappa (>= 3 coders)
  - confusion matrix and per-plane agreement
"""
import csv
import sys
import random
from itertools import combinations

CATS = [0, 1, 2, 3]            # D0..D3
K = len(CATS)


# ---------- parsing ----------
def parse_code(s):
    s = (s or "").strip().upper()
    if s == "":
        return None
    if s.startswith("D"):
        s = s[1:]
    try:
        v = int(s)
    except ValueError:
        raise ValueError("unparseable code: %r" % s)
    if v not in CATS:
        raise ValueError("code out of range D0..D3: %r" % s)
    return v


def load(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit("empty CSV")
    code_cols = [c for c in rows[0].keys() if c and c.endswith("_code")]
    if len(code_cols) < 2:
        raise SystemExit("need >= 2 columns ending in _code; found: %s" % code_cols)
    units = []          # list of (family, plane, [codes...]) ; codes may be None
    for r in rows:
        codes = [parse_code(r.get(c, "")) for c in code_cols]
        units.append((r.get("family", ""), r.get("plane", ""), codes))
    return code_cols, units


# ---------- weighted Cohen's kappa (2 raters) ----------
def weight(i, j, scheme):
    if scheme == "unweighted":
        return 1.0 if i == j else 0.0
    if scheme == "linear":
        return 1.0 - abs(i - j) / (K - 1)
    if scheme == "quadratic":
        return 1.0 - ((i - j) ** 2) / ((K - 1) ** 2)
    raise ValueError(scheme)


def cohen_kappa(pairs, scheme):
    """pairs: list of (a, b) integer code pairs (no missing)."""
    n = len(pairs)
    if n == 0:
        return float("nan")
    O = [[0.0] * K for _ in range(K)]
    for a, b in pairs:
        O[a][b] += 1.0
    row = [sum(O[i][j] for j in range(K)) for i in range(K)]
    col = [sum(O[i][j] for i in range(K)) for j in range(K)]
    po = sum(weight(i, j, scheme) * O[i][j] for i in range(K) for j in range(K)) / n
    pe = sum(weight(i, j, scheme) * row[i] * col[j] for i in range(K) for j in range(K)) / (n * n)
    if abs(1.0 - pe) < 1e-12:
        return 1.0
    return (po - pe) / (1.0 - pe)


def bootstrap_ci(pairs, scheme="quadratic", B=5000, seed=12345, alpha=0.05):
    rng = random.Random(seed)
    n = len(pairs)
    if n == 0:
        return (float("nan"), float("nan"))
    vals = []
    for _ in range(B):
        sample = [pairs[rng.randrange(n)] for _ in range(n)]
        k = cohen_kappa(sample, scheme)
        if k == k:  # not nan
            vals.append(k)
    vals.sort()
    lo = vals[int((alpha / 2) * len(vals))]
    hi = vals[min(len(vals) - 1, int((1 - alpha / 2) * len(vals)))]
    return (lo, hi)


# ---------- Fleiss' kappa (>=2 raters, fixed raters per unit) ----------
def fleiss_kappa(units_codes):
    """units_codes: list of lists of codes (no missing), same length per unit."""
    rows = [u for u in units_codes if all(c is not None for c in u)]
    if not rows:
        return float("nan")
    m = len(rows[0])
    N = len(rows)
    p = [0.0] * K
    Pbar_terms = []
    for u in rows:
        counts = [0] * K
        for c in u:
            counts[c] += 1
        for k in range(K):
            p[k] += counts[k]
        Pi = (sum(c * c for c in counts) - m) / (m * (m - 1))
        Pbar_terms.append(Pi)
    total = N * m
    p = [x / total for x in p]
    Pbar = sum(Pbar_terms) / N
    Pe = sum(x * x for x in p)
    if abs(1 - Pe) < 1e-12:
        return 1.0
    return (Pbar - Pe) / (1 - Pe)


# ---------- Krippendorff's ordinal alpha ----------
def krippendorff_alpha_ordinal(units_codes):
    """units_codes: list of lists of codes; None allowed (missing)."""
    # coincidence matrix
    o = [[0.0] * K for _ in range(K)]
    for u in units_codes:
        vals = [c for c in u if c is not None]
        mu = len(vals)
        if mu < 2:
            continue
        for a in range(mu):
            for b in range(mu):
                if a != b:
                    o[vals[a]][vals[b]] += 1.0 / (mu - 1)
    nc = [sum(o[c][k] for k in range(K)) for c in range(K)]
    n = sum(nc)
    if n < 2:
        return float("nan")

    def delta(c, k):
        if c == k:
            return 0.0
        lo, hi = (c, k) if c < k else (k, c)
        s = sum(nc[g] for g in range(lo, hi + 1)) - (nc[c] + nc[k]) / 2.0
        return s * s

    Do = sum(o[c][k] * delta(c, k) for c in range(K) for k in range(K))
    De = sum(nc[c] * nc[k] * delta(c, k) for c in range(K) for k in range(K))
    if abs(De) < 1e-12:
        return 1.0
    return 1.0 - (n - 1) * Do / De


# ---------- reporting ----------
def report(code_cols, units):
    ncoders = len(code_cols)
    complete = [(fam, pl, cs) for (fam, pl, cs) in units if all(c is not None for c in cs)]
    print("Coders: %d  (%s)" % (ncoders, ", ".join(code_cols)))
    print("Units (cells): %d total, %d fully coded" % (len(units), len(complete)))
    print()

    if not complete:
        print("No fully-coded cells found. Fill the *_code columns "
              "(D0/D1/D2/D3) for every row, then re-run.")
        return

    if ncoders == 2:
        pairs = [(cs[0], cs[1]) for (_, _, cs) in complete]
        n = len(pairs)
        exact = sum(1 for a, b in pairs if a == b) / n
        within1 = sum(1 for a, b in pairs if abs(a - b) <= 1) / n
        print("Exact agreement:       %.1f%% (%d/%d)" % (100 * exact, sum(1 for a, b in pairs if a == b), n))
        print("Within-one-level:      %.1f%% (%d/%d)" % (100 * within1, sum(1 for a, b in pairs if abs(a - b) <= 1), n))
        print()
        for sch in ("unweighted", "linear", "quadratic"):
            print("Cohen's kappa (%-10s): %+.3f" % (sch, cohen_kappa(pairs, sch)))
        lo, hi = bootstrap_ci(pairs, "quadratic")
        print("  quadratic-weighted 95%% CI (bootstrap): [%.3f, %.3f]" % (lo, hi))
        print()
        print("Krippendorff ordinal alpha: %+.3f" % krippendorff_alpha_ordinal([list(cs) for (_, _, cs) in units]))
        print()
        print("Confusion matrix (rows=%s, cols=%s):" % (code_cols[0], code_cols[1]))
        M = [[0] * K for _ in range(K)]
        for a, b in pairs:
            M[a][b] += 1
        print("        " + "  ".join("D%d" % k for k in range(K)))
        for i in range(K):
            print("   D%d  " % i + "  ".join("%2d" % M[i][j] for j in range(K)))
    else:
        allcodes = [list(cs) for (_, _, cs) in complete]
        print("Fleiss' kappa: %+.3f" % fleiss_kappa(allcodes))
        pk = [cohen_kappa([(u[i], u[j]) for u in allcodes], "quadratic")
              for i, j in combinations(range(ncoders), 2)]
        print("Mean pairwise quadratic-weighted Cohen's kappa: %+.3f" % (sum(pk) / len(pk)))
        print("Krippendorff ordinal alpha: %+.3f" % krippendorff_alpha_ordinal([list(cs) for (_, _, cs) in units]))

    # per-plane exact agreement (2 coders)
    if ncoders == 2:
        print()
        print("Per-plane exact agreement:")
        planes = {}
        for fam, pl, cs in complete:
            planes.setdefault(pl, []).append(cs[0] == cs[1])
        for pl, hits in planes.items():
            print("   %-12s %d/%d" % (pl, sum(hits), len(hits)))


def selftest():
    # 1) perfect agreement -> kappa = 1, alpha = 1
    perfect = [(i % K, i % K) for i in range(30)]
    assert abs(cohen_kappa(perfect, "quadratic") - 1.0) < 1e-9, "perfect quad kappa"
    assert abs(cohen_kappa(perfect, "unweighted") - 1.0) < 1e-9, "perfect unw kappa"
    assert abs(krippendorff_alpha_ordinal([[a, b] for a, b in perfect]) - 1.0) < 1e-9, "perfect alpha"
    # 2) systematic off-by-one disagreement: quadratic kappa > unweighted kappa
    offbyone = [(i % (K - 1), i % (K - 1) + 1) for i in range(30)]
    kq = cohen_kappa(offbyone, "quadratic")
    ku = cohen_kappa(offbyone, "unweighted")
    assert kq > ku, "weighting should reward near-misses (%.3f vs %.3f)" % (kq, ku)
    # 3) Fleiss perfect
    assert abs(fleiss_kappa([[i % K] * 3 for i in range(30)]) - 1.0) < 1e-9, "fleiss perfect"
    print("selftest OK: perfect agreement -> kappa=alpha=1; quadratic rewards near-misses (kq=%.3f > ku=%.3f)" % (kq, ku))


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--selftest":
        selftest()
    elif len(sys.argv) == 2:
        report(*load(sys.argv[1]))
    else:
        print(__doc__)
        sys.exit(1)
