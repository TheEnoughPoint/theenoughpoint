"""
Reproduce every US figure in "The Dip You Are Waiting For Turns Up About a Third
of the Time" — theenoughpoint.com/waiting-for-a-dip/

Run it and it will download the two public datasets itself, recompute the numbers
from scratch, and check them against what the article published. If a line prints
MISMATCH, we got something wrong and we would like to know.

    pip install pandas numpy requests xlrd
    python waiting-for-a-dip.py

What this is, precisely
  A standalone re-implementation, written to be published and read, not the internal
  pipeline that produced the article. It is deliberately one file with no local
  dependencies so you can run it without our setup. It reproduces every published US
  figure to within a rounding difference, which we checked before shipping it — and
  writing it caught a genuine error in our own reasoning (see test_rule below), which
  is rather the point of publishing it.

  Provided as is, with no warranty. Ours, and you are welcome to it: do what you like
  with the code. The datasets belong to their authors and carry their own terms.

Data, both free and public:
  Shiller (Yale)  http://www.econ.yale.edu/~shiller/data/ie_data.xls
  Ken French      https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/
                  F-F_Research_Data_Factors_CSV.zip

The rule being tested
  You hold cash. The moment the market closes X% below its highest point since you
  started waiting, you invest the lot. If that has not happened within 24 months,
  you invest anyway. We then compare where you end up 36 months after you started,
  against simply investing everything on day one.

  The 24-month deadline is not decoration. Without it the rule is undefined on the
  paths where the fall never arrives, and quietly dropping those paths would keep
  only the cases where waiting got its chance — which is how you accidentally prove
  anything you like.
"""

import io
import zipfile

import numpy as np
import pandas as pd
import requests

SHILLER = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"
FRENCH = ("https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
          "F-F_Research_Data_Factors_CSV.zip")
UA = {"User-Agent": "Mozilla/5.0 (reproduction script)"}

DEADLINE = 24     # months before you give up and buy anyway
HORIZON = 36      # months after the start at which we compare outcomes
DEPTHS = (5, 10, 15, 20)


def shiller_total_return():
    """Monthly total-return index for US shares, 1871 onward."""
    # Note: Yale serves this file over plain HTTP, so it arrives unauthenticated.
    # Nothing here disables certificate checking - an earlier draft of this script
    # passed verify=False, which did nothing on an http:// URL and would have been a
    # bad habit to publish. If you would rather not fetch it, download the .xls in a
    # browser and point pd.read_excel at the local copy.
    raw = requests.get(SHILLER, headers=UA, timeout=120).content
    d = pd.read_excel(io.BytesIO(raw), sheet_name="Data", skiprows=7)
    for c in ("Date", "P", "D"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    # Drop months with no dividend figure rather than imputing zero. Shiller leaves
    # D blank for the most recent months, and filling those with 0 would understate
    # the total return there. Costs three months at the tail and keeps the series honest.
    d = d.dropna(subset=["Date", "P", "D"]).reset_index(drop=True)

    def to_ts(x):
        # Shiller writes 1871.01 for January and 1871.1 for October.
        y, m = f"{float(x):.2f}".split(".")
        m = int(m) if int(m) != 0 else 10
        return pd.Timestamp(int(y), min(max(m, 1), 12), 1) + pd.offsets.MonthEnd(0)

    d["date"] = d["Date"].map(to_ts)
    # Reinvest one twelfth of the annual dividend each month.
    r = (d["P"] + d["D"].fillna(0) / 12.0) / d["P"].shift(1) - 1
    return pd.Series((1 + r.fillna(0)).cumprod().values, index=d["date"].values).dropna()


def bill_rate():
    """Monthly one-month Treasury bill return, 1926 onward."""
    z = zipfile.ZipFile(io.BytesIO(requests.get(FRENCH, headers=UA, timeout=120).content))
    rows = []
    for line in z.read(z.namelist()[0]).decode("utf-8", "replace").split("\n"):
        p = [x.strip() for x in line.split(",")]
        if len(p) >= 5 and p[0].isdigit() and len(p[0]) == 6:
            try:
                rows.append((p[0], float(p[4]) / 100))
            except ValueError:
                pass
    f = pd.DataFrame(rows, columns=["ym", "rf"]).drop_duplicates("ym")
    f["date"] = pd.to_datetime(f.ym, format="%Y%m") + pd.offsets.MonthEnd(0)
    return f.set_index("date").rf.sort_index()


def test_rule(prices, cash=None, drop=0.15, deadline=DEADLINE, horizon=HORIZON):
    """Returns (waiting won %, fall arrived %, median wait, n, waiting won GIVEN it arrived %).

    That last one has to be counted properly rather than derived. Waiting can also
    win on paths where the fall never came — you bought at the deadline and the
    price happened to be kinder than day one. Dividing the overall win rate by the
    arrival rate ignores those and can exceed 100%, which is how this script caught
    an error in our own first draft of it.
    """
    v = prices.values
    c = None if cash is None else cash.values
    waited_won, arrived, waits, won_and_arrived = [], [], [], 0
    for i in range(len(v) - horizon):
        peak, hit = v[i], None
        for t in range(1, deadline + 1):
            peak = max(peak, v[i + t])
            if v[i + t] <= peak * (1 - drop):
                hit = t
                break
        t_buy = hit if hit is not None else deadline
        interest = 1.0 if c is None else float(np.prod(1 + c[i:i + t_buy]))
        day_one = v[i + horizon] / v[i]
        waiting = interest * (v[i + horizon] / v[i + t_buy])
        won = waiting > day_one
        waited_won.append(won)
        arrived.append(hit is not None)
        if hit is not None:
            waits.append(hit)
            won_and_arrived += won
    n_arr = sum(arrived)
    return (np.mean(waited_won) * 100, np.mean(arrived) * 100,
            float(np.median(waits)), len(waited_won),
            won_and_arrived / n_arr * 100 if n_arr else float("nan"))


def check(label, got, want, tol=0.6):
    ok = abs(got - want) <= tol
    print(f"  {'OK      ' if ok else 'MISMATCH'} {label:<46} got {got:6.1f}   published {want:6.1f}")
    return ok


if __name__ == "__main__":
    print("Downloading Shiller and French data...\n")
    px = shiller_total_return()
    rf = bill_rate()
    print(f"Shiller: {px.index[0].date()} to {px.index[-1].date()}  ({len(px)} months)")
    print(f"French bill rate: {rf.index[0].date()} to {rf.index[-1].date()}\n")

    print("1. HOW OFTEN THE FALL ARRIVED, and how long you waited  (1871-2023, cash at 0%)")
    published_arrival = {5: 81.1, 10: 53.3, 15: 35.5, 20: 22.0}
    published_wait = {5: 7, 10: 10, 15: 12, 20: 13}
    ok = True
    for dp in DEPTHS:
        won, arr, wait, n, cond = test_rule(px, None, dp / 100)
        ok &= check(f"{dp}% fall arrived within 2 years", arr, published_arrival[dp])
        ok &= check(f"{dp}% median wait, months", wait, published_wait[dp], tol=0.5)

    print("\n2. HOW OFTEN WAITING BEAT BUYING ON DAY ONE  (1871-2023, cash at 0%)")
    published_won = {5: 42.5, 10: 35.5, 15: 32.2, 20: 25.4}
    for dp in DEPTHS:
        won, arr, wait, n, cond = test_rule(px, None, dp / 100)
        ok &= check(f"waiting won, {dp}% rule", won, published_won[dp])
    print(f"  (start months used: {n:,})")

    print("\n3. THE SAME, GIVING THE CASH THE REAL BILL RATE  (1926-2023)")
    j = pd.concat([px.rename("p"), rf.rename("c")], axis=1, join="inner").dropna()
    published_cash = {5: 46.4, 10: 37.8, 15: 34.4, 20: 29.6}
    published_zero = {5: 41.0, 10: 32.5, 15: 28.7, 20: 22.7}
    for dp in DEPTHS:
        w_cash = test_rule(j.p, j.c, dp / 100)[0]
        w_zero = test_rule(j.p, None, dp / 100)[0]
        ok &= check(f"waiting won with real interest, {dp}% rule", w_cash, published_cash[dp])
        ok &= check(f"waiting won at 0% on same years, {dp}% rule", w_zero, published_zero[dp])

    print("\n4. WHEN THE FALL DID ARRIVE, DID WAITING PAY?  (1871-2023, cash at 0%)")
    published_cond = {5: 52.4, 10: 65.7, 15: 84.2, 20: 89.5}
    for dp in DEPTHS:
        cond = test_rule(px, None, dp / 100)[4]
        ok &= check(f"waiting paid given the fall came, {dp}% rule", cond,
                    published_cond[dp])

    print("\n" + ("ALL FIGURES REPRODUCED." if ok else
                  "SOMETHING DID NOT MATCH — please tell us."))
