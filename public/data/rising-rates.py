"""
Reproduce every computed figure in "Rates Are Rising Again. Does the Bull Market
Have to Break?" — theenoughpoint.com/rising-rates-bull-market/

Run it and it will download the two public datasets itself, recompute the numbers
from scratch, and check them against what the article published. If a line prints
MISMATCH, we got something wrong and we would like to know.

    pip install pandas numpy requests xlrd
    python rising-rates.py

What this is, precisely
  The same rule the article ran, in one file with no local dependencies, written
  to be read. It reproduces every published figure to within a rounding
  difference, which we checked before shipping it. Provided as is, with no
  warranty; the datasets belong to their authors and carry their own terms.

Data, both free and public:
  Shiller (Yale)  http://www.econ.yale.edu/~shiller/data/ie_data.xls
                  monthly prices, dividends and CPI from 1871
  FRED            https://fred.stlouisfed.org/graph/fredgraph.csv?id=GS10
                  monthly-average 10-year constant maturity yield from April 1953

The question being asked
  Take every month with a full year of data behind it and a full year ahead of
  it. Behind: did the 10-year yield rise or fall over the trailing 12 months,
  and what was CPI inflation over the same 12 months? Ahead: the next 12 months
  of US share total return, dividends reinvested, nominal and after inflation.
  Then sort.
"""

import io

import numpy as np
import pandas as pd
import requests

SHILLER = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GS10"
UA = {"User-Agent": "Mozilla/5.0 (reproduction script)"}


def shiller():
    """Monthly total-return index and CPI for US shares, 1871 onward."""
    raw = requests.get(SHILLER, headers=UA, timeout=180).content
    d = pd.read_excel(io.BytesIO(raw), sheet_name="Data", skiprows=7)
    cols = list(d.columns)
    cpi_col = next(c for c in cols if "CPI" in str(c))
    for c in ("Date", "P", "D"):
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d[cpi_col] = pd.to_numeric(d[cpi_col], errors="coerce")
    d = d.dropna(subset=["Date", "P"]).reset_index(drop=True)

    def to_ts(x):
        # Shiller writes 1871.01 for January and 1871.1 for October.
        y, m = f"{float(x):.2f}".split(".")
        m = int(m) if int(m) != 0 else 10
        return pd.Timestamp(int(y), min(max(m, 1), 12), 1) + pd.offsets.MonthEnd(0)

    d["date"] = d["Date"].map(to_ts)
    # Reinvest one twelfth of the annual dividend each month; stop where the
    # dividend column does rather than imputing zero at the tail.
    r = (d["P"] + d["D"] / 12.0) / d["P"].shift(1) - 1
    d["tr"] = (1 + r.fillna(0)).cumprod()
    d = d.loc[:d["D"].last_valid_index()]
    return d.set_index("date")[["tr", cpi_col]].rename(columns={cpi_col: "cpi"})


def fred_gs10():
    """Monthly-average 10-year constant maturity yield, April 1953 onward."""
    f = pd.read_csv(io.BytesIO(requests.get(FRED, headers=UA, timeout=180).content))
    f.columns = ["date", "y"]
    f["date"] = pd.to_datetime(f["date"]) + pd.offsets.MonthEnd(0)
    f["y"] = pd.to_numeric(f["y"], errors="coerce")
    return f.dropna().set_index("date")["y"]


def check(label, got, want, tol=0.6):
    ok = abs(got - want) <= tol
    print(f"  {'OK      ' if ok else 'MISMATCH'} {label:<52} got {got:7.1f}   published {want:7.1f}")
    return ok


if __name__ == "__main__":
    print("Downloading Shiller and FRED data...\n")
    sh = shiller()
    ys = fred_gs10()
    print(f"Shiller: {sh.index[0].date()} to {sh.index[-1].date()}")
    print(f"FRED GS10: {ys.index[0].date()} to {ys.index[-1].date()}\n")

    d = pd.concat([sh, ys.rename("y")], axis=1, join="inner")
    d["dy12"] = d["y"] - d["y"].shift(12)
    d["infl12"] = d["cpi"] / d["cpi"].shift(12) - 1
    d["fwd12"] = d["tr"].shift(-12) / d["tr"] - 1
    d["fwd12_real"] = (d["tr"].shift(-12) / d["tr"]) / (d["cpi"].shift(-12) / d["cpi"]) - 1
    d = d.dropna(subset=["dy12", "fwd12"])
    # The article ran April 1954 to June 2022 starts. If the datasets have been
    # extended since, pin the window so the checks stay like-for-like.
    d = d.loc[:pd.Timestamp("2022-06-30")]
    print(f"Usable start months: {len(d)} ({d.index[0].date()} to {d.index[-1].date()})\n")

    ok = True
    up, down = d[d.dy12 > 0], d[d.dy12 < 0]

    print("1. NEXT 12 MONTHS AFTER THE 10-YEAR ROSE / FELL (nominal)")
    ok &= check("months with the yield higher, count", len(up), 434, tol=2)
    ok &= check("median next-12m return, yield higher, %", up.fwd12.median() * 100, 11.9)
    ok &= check("positive share, yield higher, %", (up.fwd12 > 0).mean() * 100, 73.7)
    ok &= check("median next-12m return, yield lower, %", down.fwd12.median() * 100, 13.6)
    ok &= check("positive share, yield lower, %", (down.fwd12 > 0).mean() * 100, 80.3)

    print("\n2. THE 2x2: DIRECTION x TRAILING INFLATION (real, after inflation)")
    cells = [("rising + inflation under 4%", up[up.infl12 < 0.04], 74.5, 8.7),
             ("rising + inflation 4%+", up[up.infl12 >= 0.04], 56.1, 4.4),
             ("falling + inflation under 4%", down[down.infl12 < 0.04], 80.9, 13.5),
             ("falling + inflation 4%+", down[down.infl12 >= 0.04], 53.7, 5.2)]
    for lab, g, want_pos, want_med in cells:
        gr = g.fwd12_real.dropna()
        ok &= check(f"{lab}: beat inflation, %", (gr > 0).mean() * 100, want_pos)
        ok &= check(f"{lab}: median real, %", gr.median() * 100, want_med)

    print("\n3. CALENDAR YEARS WITH THE 10-YEAR UP >= 0.5pp DEC-DEC")
    full = pd.concat([sh, ys.rename("y")], axis=1, join="inner")
    dec = full[full.index.month == 12].dropna(subset=["y", "tr"])
    rows = []
    for i in range(1, len(dec)):
        rows.append((dec.index[i].year,
                     dec.y.iloc[i] - dec.y.iloc[i - 1],
                     dec.tr.iloc[i] / dec.tr.iloc[i - 1] - 1))
    rising_years = [r for r in rows if r[1] >= 0.5 and r[0] <= 2022]
    losers = sorted(y for y, _, tr in rising_years if tr <= 0)
    ok &= check("rising-rate years, count", len(rising_years), 21, tol=0)
    ok &= check("of which positive, count", sum(1 for r in rising_years if r[2] > 0), 15, tol=0)
    want_losers = [1969, 1974, 1977, 1981, 1987, 2022]
    same = losers == want_losers
    print(f"  {'OK      ' if same else 'MISMATCH'} losing years: {losers} vs published {want_losers}")
    ok &= same

    print("\n4. THE EPISODES (total return between month-ends, dividends reinvested)")
    def window(a, b):
        return (sh.loc[pd.Timestamp(b), "tr"] / sh.loc[pd.Timestamp(a), "tr"] - 1) * 100
    ok &= check("Dec 1962 to Dec 1968 (the sixties), %", window("1962-12-31", "1968-12-31"), 104.7, tol=1.5)
    ok &= check("calendar 2013, %", window("2012-12-31", "2013-12-31"), 29.7, tol=1.5)
    ok &= check("calendar 1994, %", window("1993-12-31", "1994-12-31"), 0.5, tol=1.5)
    ok &= check("calendar 2022, %", window("2021-12-31", "2022-12-31"), -15.0, tol=1.5)
    ok &= check("Jul 2016 to Nov 2018, %", window("2016-07-31", "2018-11-30"), 32.6, tol=1.5)
    ok &= check("Jul 2020 to Jun 2023, %", window("2020-07-31", "2023-06-30"), 41.7, tol=1.5)
    ok &= check("10-year yield, Dec 1962, %", ys.loc[pd.Timestamp("1962-12-31")], 3.86, tol=0.05)
    ok &= check("10-year yield, Dec 1968, %", ys.loc[pd.Timestamp("1968-12-31")], 6.03, tol=0.05)

    print("\n5. THE LONG SHADOW (Dec 1965 to Dec 1981)")
    tr = window("1965-12-31", "1981-12-31") / 100
    cpi = sh.loc[pd.Timestamp("1981-12-31"), "cpi"] / sh.loc[pd.Timestamp("1965-12-31"), "cpi"]
    ok &= check("nominal total return, %", tr * 100, 152.7, tol=2)
    ok &= check("real total return, %", ((1 + tr) / cpi - 1) * 100, -14.5, tol=1.5)

    print("\n6. MONTHS MOST LIKE AUGUST 2026 (10-year at 4-5% and higher than a year earlier)")
    band = d[(d.y >= 4) & (d.y <= 5) & (d.dy12 > 0)]
    ok &= check("count of such months", len(band), 85, tol=1)
    ok &= check("median next-12m return, %", band.fwd12.median() * 100, 9.4)
    ok &= check("positive share, %", (band.fwd12 > 0).mean() * 100, 77.6)

    print("\n" + ("ALL FIGURES REPRODUCED." if ok else
                  "SOMETHING DID NOT MATCH — please tell us."))
