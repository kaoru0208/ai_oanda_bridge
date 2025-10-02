import csv, json, sys, math
from datetime import datetime, timezone
from ai_trade_helpers import slip_pips_measured, label_session

def parse_iso8601(s):
    try: dt = datetime.fromisoformat(s.replace("Z","+00:00"))
    except Exception: return None
    if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
    return dt

def quantile(x, q):
    if not x: return math.nan
    xs = sorted(x)
    if q <= 0: return xs[0]
    if q >= 1: return xs[-1]
    i = (len(xs)-1) * q
    lo, hi = int(math.floor(i)), int(math.ceil(i))
    if lo == hi: return xs[lo]
    w = i - lo
    return xs[lo]*(1-w) + xs[hi]*w

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--fills", required=True, help="CSV with fill_time_utc,instrument,mid_at_submit,fill_price")
    ap.add_argument("--base", type=float, default=0.5)
    ap.add_argument("--q", type=float, default=0.75, help="quantile in [0,1], e.g., 0.75 for p75, 0.5 for median")
    ap.add_argument("--out", default="slip_offsets.json")
    args = ap.parse_args()

    rows = []
    with open(args.fills, newline='') as f:
        r = csv.DictReader(f)
        for row in r:
            ts = parse_iso8601(row.get("fill_time_utc",""))
            if not ts: continue
            try:
                ins  = row["instrument"]
                mid  = float(row["mid_at_submit"])
                fill = float(row["fill_price"])
            except Exception:
                continue
            slip = slip_pips_measured(fill, mid, ins)
            sess = label_session(ts)
            rows.append((sess, slip))

    if not rows:
        print("no rows"); return 0

    offsets = {}
    for sess in {"NY_ROLL","OTHER"}:
        slips = [s for (ss,s) in rows if ss==sess]
        if slips:
            qv = quantile(slips, args.q)
            offsets[sess] = max(0.0, qv - args.base)

    out = {"base": args.base, "q": args.q, "offsets": offsets}
    with open(args.out,"w") as w: json.dump(out, w, indent=2)
    print(json.dumps(out, indent=2)); return 0

if __name__ == "__main__":
    sys.exit(main())
