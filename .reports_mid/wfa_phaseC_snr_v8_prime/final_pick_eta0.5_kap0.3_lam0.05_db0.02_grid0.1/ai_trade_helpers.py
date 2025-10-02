import os, datetime as dt
# zoneinfo は Python 3.9+ の標準。古い環境では backports.zoneinfo を使う
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover
    try:
        from backports.zoneinfo import ZoneInfo  # pip install backports.zoneinfo
    except Exception as e:
        raise RuntimeError("zoneinfo が必要です。Python<3.9 なら: pip install backports.zoneinfo") from e

def to_pips(price_diff: float, instrument: str) -> float:
    """
    JPY絡みは 0.01 pip、その他は 0.0001 pip の簡易判定。
    """
    ins = instrument.upper()
    pip = 0.01 if ("_JPY" in ins or ins.startswith("JPY_")) else 0.0001
    return abs(float(price_diff)) / pip

def slip_pips_measured(fill_price: float, mid_at_submit: float, instrument: str) -> float:
    return to_pips(fill_price - mid_at_submit, instrument)

def parse_et_window_to_utc(env: str = "USE_SPREAD_P75", day: dt.date | None = None):
    """
    envに 'HH:MM-HH:MM_ET'（例 '16:55-17:10_ET'）を想定。
    返り値: (UTC開始時刻, UTC終了時刻) の dt.time タプル。未設定なら None。
    """
    spec = os.getenv(env)
    if not spec:
        return None
    spec = spec.strip()
    if not spec.endswith("_ET"):
        raise ValueError(f"{env} は '16:55-17:10_ET' の形で設定して下さい")
    hhmm1, hhmm2 = spec[:-3].split("-")
    day = day or dt.date.today()
    et = ZoneInfo("America/New_York")
    t1_et = dt.datetime.combine(day, dt.time.fromisoformat(hhmm1), et)
    t2_et = dt.datetime.combine(day, dt.time.fromisoformat(hhmm2), et)
    return (
        t1_et.astimezone(dt.timezone.utc).time(),
        t2_et.astimezone(dt.timezone.utc).time(),
    )

def use_p75_halfspread(now_utc: dt.time | None = None, env: str = "USE_SPREAD_P75") -> bool:
    """
    現在UTC時刻が p75 切替窓に入っているか？
    """
    win = parse_et_window_to_utc(env=env)
    if not win:
        return False
    now_utc = now_utc or dt.datetime.now(dt.timezone.utc).time()
    t1, t2 = win
    return t1 <= now_utc <= t2

def label_session(ts_utc):
    """
    'NY_ROLL'（16:55–17:10 ET）/ 'OTHER' を返す。
    pandas.Timestamp でも datetime でもOK（naiveはUTC扱い）。
    """
    # naive → aware(UTC)
    if getattr(ts_utc, "tzinfo", None) is None:
        if hasattr(ts_utc, "tz_localize"):  # pandas
            ts_utc = ts_utc.tz_localize("UTC")
        else:
            ts_utc = ts_utc.replace(tzinfo=dt.timezone.utc)
    # UTC -> America/New_York
    if hasattr(ts_utc, "tz_convert"):      # pandas
        et = ts_utc.tz_convert("America/New_York")
    else:
        et = ts_utc.astimezone(ZoneInfo("America/New_York"))
    h, m = int(et.hour), int(et.minute)
    in_roll = (h == 16 and m >= 55) or (h == 17 and m <= 10)
    return "NY_ROLL" if in_roll else "OTHER"

def should_cooldown(psr_n: float, turnover_rel: float, slip_ewma: float, slip_base: float,
                    psr_th: float = 0.10, turn_th: float = 1.5, slip_mult: float = 1.5) -> bool:
    """
    PSR×回転×滑りの簡易ガード。Trueならクールダウン。
    """
    weak_psr = psr_n < psr_th
    churny   = turnover_rel > turn_th
    slippy   = slip_ewma > slip_mult * slip_base
    return bool(weak_psr and (churny or slippy))

if __name__ == "__main__":
    print("Helpers loaded.")
    print("USE_SPREAD_P75:", os.getenv("USE_SPREAD_P75"))
    print("UTC window:", parse_et_window_to_utc())
    print("use_p75_halfspread(now)?", use_p75_halfspread())
    print("to_pips demo (USD_JPY, 0.012):", to_pips(0.012, "USD_JPY"))
    print("cooldown demo:", should_cooldown(0.08, 1.6, 0.9, 0.5))
