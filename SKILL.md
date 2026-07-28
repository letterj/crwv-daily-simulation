# CRWV Daily Bearish Put Simulation Skill

## Overview

This skill runs a full daily CRWV 30-day bearish put simulation every morning. It automatically skips weekends and US market holidays. All timing uses US Eastern Time.

The simulation fetches real Robinhood option prices and spot, pulls real news, auto-scores sentiment on the chip-backed debt thesis, runs LSM pricing, simulates virtual trades under $5,000 capital, and outputs the complete daily report with virtual P&L and recommended actions.

**No real trades are placed.**

## Simulation Period

- **Start date:** 28 July 2026
- **End date:** 26 September 2026 (60-day extended pilot test)
- **Daily run:** Every morning, automatically skipping weekends and US market holidays

## Components

### 1. lsm_american_put.py
Longstaff-Schwartz American put Monte Carlo pricer with base and stress volatility scenarios.

### 2. crwv_strategy_monitor.py
Daily simulator that:
- Loads virtual $5,000 capital from state
- Fetches live Robinhood quotes
- Pulls and auto-scores news on chip-backed debt thesis
- Runs LSM pricing
- Applies entry/exit rules
- Outputs daily report with virtual P&L
- Persists state and logs

## Usage

```bash
cd /home/workdir/.grok/skills/crwv-daily-simulation/scripts
python crwv_strategy_monitor.py
```

Or with explicit inputs:

```bash
python crwv_strategy_monitor.py --spot <live_spot> --premium <live_put_mark> --news "snippet1" "snippet2" ...
```

## State & Logs

- State: `/home/workdir/artifacts/crwv_strategy_state.json`
- Log: `/home/workdir/artifacts/crwv_monitor_log.csv`

## Thesis

Bearish on CRWV due to chip-backed debt concerns: rising interest expense, high leverage, large capex guidance versus revenue recognition timing.