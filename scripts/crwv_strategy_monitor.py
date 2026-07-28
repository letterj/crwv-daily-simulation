#!/usr/bin/env python3
"""
CRWV Daily Strategy Monitor
Simulates a $5k virtual capital options trading strategy.
"""

import json
import csv
from datetime import datetime, date
from pathlib import Path
from typing import List, Dict, Optional
import sys

# Add parent to path for imports
sys.path.append(str(Path(__file__).parent))
from lsm_american_put import price_put_lsm


STATE_FILE = Path("/home/workdir/artifacts/crwv_strategy_state.json")
LOG_FILE = Path("/home/workdir/artifacts/crwv_monitor_log.csv")
STARTING_CAPITAL = 5000.0
ENTRY_WINDOW_START = date(2026, 7, 29)
ENTRY_WINDOW_END = date(2026, 8, 31)


def load_state() -> Dict:
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {
        "cash": STARTING_CAPITAL,
        "equity": STARTING_CAPITAL,
        "realized_pnl": 0.0,
        "positions": [],
        "last_run": None,
    }


def save_state(state: Dict):
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def log_run(state: Dict, spot: float, premium: float, thesis: str, action: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    write_header = not LOG_FILE.exists()
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["timestamp", "spot", "premium", "thesis", "action", "cash", "equity", "realized_pnl"])
        writer.writerow([
            datetime.now().isoformat(),
            spot,
            premium,
            thesis,
            action,
            state["cash"],
            state["equity"],
            state["realized_pnl"],
        ])


def score_thesis(news_snippets: List[str]) -> str:
    text = " ".join(news_snippets).lower()
    debt_keywords = ["debt", "interest", "leverage", "financing", "coupon", "notes", "bond"]
    revenue_keywords = ["backlog", "contract", "revenue", "lease", "customer"]

    debt_score = sum(1 for k in debt_keywords if k in text)
    revenue_score = sum(1 for k in revenue_keywords if k in text)

    if debt_score > revenue_score:
        return "Strengthens"
    elif revenue_score > debt_score:
        return "Weakens"
    return "Neutral"


def is_entry_window_open(today: Optional[date] = None) -> bool:
    if today is None:
        today = date.today()
    return ENTRY_WINDOW_START <= today <= ENTRY_WINDOW_END


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CRWV Daily Strategy Monitor")
    parser.add_argument("--spot", type=float, required=True, help="Current spot price")
    parser.add_argument("--premium", type=float, required=True, help="Live OTM put mark price")
    parser.add_argument("--news", nargs="*", default=[], help="News snippets for thesis scoring")
    parser.add_argument("--days", type=int, default=25, help="Days to expiration")
    args = parser.parse_args()

    state = load_state()
    thesis = score_thesis(args.news) if args.news else "Neutral"

    # Generate LSM prices for a few strikes
    strikes = [args.spot * 0.92, args.spot * 0.88, args.spot * 0.85]
    lsm_prices = []
    for K in strikes:
        base, stress = price_put_lsm(args.spot, K, args.days)
        lsm_prices.append((K, base, stress))

    # Determine action
    entry_open = is_entry_window_open()
    if state["positions"]:
        action = "MANAGE EXISTING"
    elif entry_open:
        action = "ENTER"
    else:
        action = "HOLD / NO ACTION"

    # Print report
    print(f"\n=== CRWV Daily Simulation ({date.today()}) ===")
    print(f"Spot: ${args.spot:.2f} | Live put: ${args.premium:.2f}")
    print(f"Thesis: {thesis}")
    print(f"LSM prices (base/stress):")
    for K, base, stress in lsm_prices:
        print(f"  K={K:.1f} -> base ${base:.2f} / stress ${stress:.2f}")
    print(f"Open positions: {len(state['positions'])}")
    print(f"Cash/Equity: ${state['cash']:.2f} / ${state['equity']:.2f}")
    print(f"Realized PnL: ${state['realized_pnl']:.2f}")
    print(f"Recommended action: {action}")

    # Update state
    state["last_run"] = datetime.now().isoformat()
    save_state(state)
    log_run(state, args.spot, args.premium, thesis, action)
    print(f"\nState saved to {STATE_FILE}")
    print(f"Log appended to {LOG_FILE}")


if __name__ == "__main__":
    main()
