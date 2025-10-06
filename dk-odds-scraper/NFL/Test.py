#!/usr/bin/env python3
"""
fill_nfl_schedule.py

Reads:
  - NFL_api_response.json (events + markets JSON)
  - nfl_schedule.xlsx (with columns: Rot, Game, Time, Spread, O/U)

Writes:
  - nfl_schedule_filled.xlsx

It matches by retail rot numbers in the JSON (participants[].metadata.retailRotNumber)
and fills Time (converted to US/Eastern by default), Spread and O/U when available.
The script is robust to a couple of common JSON shapes:
  1) Top-level list of events (each has participants, startEventDate, etc.)
  2) Dict with keys like {"events": [...], "markets": [...], "selections": [...]}
For spreads/totals, it looks for markets whose name or type includes "Spread" or "Total".
If not found, it leaves the cell blank.
"""

import json
import pandas as pd
from datetime import datetime, timezone
from pathlib import Path
import sys

try:
    import pytz  # for time zone conversion
except ImportError:
    pytz = None

# --------------- Config ---------------
INPUT_JSON = Path("NFL_api_response.json")
INPUT_XLSX = Path("nfl_schedule.xlsx")
OUTPUT_XLSX = Path("nfl_schedule_filled.xlsx")
TIMEZONE = "US/Eastern"   # change to your preferred tz (e.g., "America/Chicago")
# -------------------------------------


def _safe_parse_iso(dt_str: str):
    if not dt_str:
        return None
    s = dt_str.strip()
    # normalize different ISO formats (with or without Z, fractional seconds, etc.)
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        # fallback: drop fractional seconds if necessary
        if "." in s:
            base, rest = s.split(".", 1)
            rest = rest.split("+")[1] if "+" in rest else ""
            recons = base + "+00:00"
            try:
                return datetime.fromisoformat(recons)
            except Exception:
                return None
        return None


def _to_local(dt: datetime, tz_name: str) -> str:
    if not dt:
        return ""
    # ensure timezone aware
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # convert
    if pytz is None:
        # fallback: keep in UTC if pytz not available
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %I:%M %p UTC")
    try:
        tz = pytz.timezone(tz_name)
        loc = dt.astimezone(tz)
        return loc.strftime("%Y-%m-%d %I:%M %p")
    except Exception:
        return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %I:%M %p UTC")


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def collect_events(data):
    """
    Return dicts:
      by_event_id: eventId -> {"start": datetime, "participants": [participant objects]}
      by_rot: rot -> {"eventId": str, "teamName": str, "start": datetime}
    Supports two JSON shapes.
    """
    by_event_id = {}
    by_rot = {}

    # shape detection
    if isinstance(data, dict) and "events" in data:
        events_iter = data["events"]
    elif isinstance(data, list):
        events_iter = data
    else:
        # try to find list under known keys, else empty
        events_iter = data.get("Events") if isinstance(data, dict) else []

    for ev in events_iter or []:
        event_id = str(ev.get("id") or ev.get("eventId") or "")
        start = _safe_parse_iso(ev.get("startEventDate"))
        parts = ev.get("participants", []) or ev.get("Participants", [])
        by_event_id[event_id] = {"start": start, "participants": parts}

        for p in parts:
            meta = p.get("metadata", {}) or {}
            rot = str(meta.get("retailRotNumber") or "").strip()
            if rot:
                by_rot[rot] = {"eventId": event_id, "teamName": p.get("name", ""), "start": start}

    return by_event_id, by_rot


def collect_markets(data):
    """
    Return per-event basic pricing hints for spread/total if present:
      spreads[eventId] -> {"home": {"line": x, "price": y}, "away": {...}} (best-effort)
      totals[eventId]  -> {"over": {"line": x, "price": y}, "under": {...}} (best-effort)
    Works with DraftKings-like structures where markets live under "markets" and selections nested,
    but also tries to extract when markets are mixed at top-level.
    """
    # Gather a flat list of markets
    if isinstance(data, dict) and "markets" in data:
        markets_iter = data["markets"]
    elif isinstance(data, list):
        # Some feeds include markets mixed with events; filter those with "marketType" or "name"
        markets_iter = [m for m in data if m.get("marketType") or m.get("name")]
    else:
        markets_iter = []

    spreads = {}
    totals = {}

    def is_spread(mname, mtype):
        text = f"{mname} {mtype}".lower()
        return ("spread" in text) or ("point spread" in text)

    def is_total(mname, mtype):
        text = f"{mname} {mtype}".lower()
        return ("total" in text) or ("over/under" in text) or ("o/u" in text)

    # Some feeds have no selections inline; we still handle if selections exist under market["selections"]
    for m in markets_iter:
        event_id = str(m.get("eventId") or "")
        mname = m.get("name", "")
        mtype = (m.get("marketType") or {}).get("name", "")
        # get selections if inline; otherwise skip (we don't have a separate selections json here)
        sels = m.get("selections") or []

        if is_spread(mname, mtype):
            for s in sels:
                out = (s.get("outcome") or "").lower()
                line = s.get("line") or s.get("handicap") or s.get("points")
                price = s.get("oddsDecimal") or s.get("oddsAmerican") or s.get("price")
                if event_id not in spreads:
                    spreads[event_id] = {}
                if "home" in out:
                    spreads[event_id]["home"] = {"line": line, "price": price}
                elif "away" in out:
                    spreads[event_id]["away"] = {"line": line, "price": price}
                else:
                    # Sometimes outcomes are team names with +/-
                    sel_name = (s.get("name") or "").lower()
                    if "over" in sel_name or "under" in sel_name:
                        # belongs to totals, not spreads
                        pass
                    else:
                        # naive: store first two we see
                        role = "home" if "home" in sel_name else ("away" if "away" in sel_name else ("sel1" if "sel1" not in spreads[event_id] else "sel2"))
                        spreads[event_id][role] = {"line": line, "price": price}

        if is_total(mname, mtype):
            for s in sels:
                sel_name = (s.get("name") or s.get("outcome") or "").lower()
                line = s.get("line") or s.get("handicap") or s.get("points")
                price = s.get("oddsDecimal") or s.get("oddsAmerican") or s.get("price")
                if event_id not in totals:
                    totals[event_id] = {}
                if "over" in sel_name:
                    totals[event_id]["over"] = {"line": line, "price": price}
                elif "under" in sel_name:
                    totals[event_id]["under"] = {"line": line, "price": price}

    return spreads, totals


def main():
    if not INPUT_JSON.exists():
        print(f"ERROR: {INPUT_JSON} not found.")
        sys.exit(1)
    if not INPUT_XLSX.exists():
        print(f"ERROR: {INPUT_XLSX} not found.")
        sys.exit(1)

    data = load_json(INPUT_JSON)

    by_event_id, by_rot = collect_events(data)
    spreads, totals = collect_markets(data)

    # Load Excel
    df = pd.read_excel(INPUT_XLSX)

    # Normalize Rot to string for mapping; do not disturb blank rows
    def norm_rot(x):
        try:
            return str(int(x)).strip()
        except Exception:
            try:
                return str(x).strip()
            except Exception:
                return ""

    rot_series = df.get("Rot")
    if rot_series is None:
        raise KeyError("Expected a 'Rot' column in the Excel file.")

    # Fill Time by mapping rot -> event start
    times = []
    spreads_col = []
    totals_col = []

    for rot in rot_series:
        key = norm_rot(rot)
        if not key or key not in by_rot:
            times.append("")
            spreads_col.append("")
            totals_col.append("")
            continue

        ev = by_rot[key]
        start_local = _to_local(ev["start"], TIMEZONE)

        # Spread formatting: prefer home team line if available; otherwise any
        ev_spread = spreads.get(ev["eventId"], {})
        spread_line = ""
        if ev_spread:
            # pick the selection that corresponds to this rot/team if possible
            # (home rot is usually even, away odd; but we just fill a single text for the row)
            # We display like: -3.5 or +3.5 (no price to keep sheet clean)
            if "home" in ev_spread and "away" in ev_spread:
                # choose the one matching the team for this rot by comparing names
                spread_line = str(ev_spread.get("home", {}).get("line") or "")
            else:
                # fallback: first available
                first = next(iter(ev_spread.values()))
                spread_line = str((first or {}).get("line") or "")

        # Total formatting: show "O 44.5 / U 44.5" or just the line if only one side seen
        ev_total = totals.get(ev["eventId"], {})
        total_line = ""
        if ev_total:
            over_line = ev_total.get("over", {}).get("line")
            under_line = ev_total.get("under", {}).get("line")
            if over_line and under_line:
                total_line = f"O {over_line} / U {under_line}"
            else:
                total_line = str(over_line or under_line or "")

        times.append(start_local)
        spreads_col.append(spread_line)
        totals_col.append(total_line)

    # Write back
    if "Time" in df.columns:
        df["Time"] = times
    else:
        df.insert(df.columns.get_loc("Game") + 1, "Time", times)

    if "Spread" in df.columns:
        df["Spread"] = spreads_col
    else:
        df["Spread"] = spreads_col

    if "O/U" in df.columns:
        df["O/U"] = totals_col
    else:
        df["O/U"] = totals_col

    df.to_excel(OUTPUT_XLSX, index=False)
    print(f"✅ Wrote {OUTPUT_XLSX.resolve()}")
    print("Tip: If Time is still blank, double-check that your JSON has startEventDate and that the Rot numbers match the JSON participants.metadata.retailRotNumber.")
    print("      You can also change TIMEZONE in the script if you'd like a different display tz.")


if __name__ == "__main__":
    main()
