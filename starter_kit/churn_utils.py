"""
Utility functions for churn-risk flagging.

The original starter implementation was intentionally minimal and did not handle
short histories or noisy/partial datasets. This version keeps the same public API
while adding safe edge-case handling and a simple reporting workflow suitable for
v1 churn analysis.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean


def load_accounts(path):
    """Load account data from a JSON file and return the list of account records."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("accounts", [])


def compute_trend_pct(weekly_logins, window=4):
    """
    Compare the average of the most recent `window` weeks against the average of
    the `window` weeks before that. Returns a percentage change, where negative
    numbers mean declining usage.

    If there is not enough history to compare, this returns 0.0 instead of
    raising an error so callers can safely treat it as "not enough data".
    """
    if window <= 0:
        raise ValueError("window must be a positive integer")

    values = [float(v) for v in (weekly_logins or []) if v is not None]
    if len(values) < 2 * window:
        return 0.0

    recent = values[-window:]
    previous = values[-2 * window:-window]
    recent_avg = mean(recent)
    previous_avg = mean(previous)

    if previous_avg == 0:
        return 0.0
    return (recent_avg - previous_avg) / previous_avg * 100.0


def flag_at_risk(account, window=4, decline_threshold_pct=-30.0, min_history_weeks=8):
    """Return True if the account appears to be at risk of churn."""
    weekly_logins = account.get("weekly_logins", [])
    if len(weekly_logins) < max(min_history_weeks, 2 * window):
        return False

    trend = compute_trend_pct(weekly_logins, window)
    return trend <= decline_threshold_pct


def assess_account(account, window=4, decline_threshold_pct=-30.0, min_history_weeks=8):
    """Return a structured risk assessment for a single account."""
    weekly_logins = account.get("weekly_logins", [])
    history_length = len(weekly_logins)
    if history_length < max(min_history_weeks, 2 * window):
        return {
            "account_id": account.get("account_id", "unknown"),
            "account_name": account.get("account_name", "Unknown"),
            "flagged": False,
            "trend_pct": 0.0,
            "reason": "insufficient history to evaluate a usage trend",
        }

    trend = compute_trend_pct(weekly_logins, window)
    recent = weekly_logins[-window:]
    previous = weekly_logins[-2 * window:-window]
    recent_avg = mean(recent)
    previous_avg = mean(previous)

    flagged = trend <= decline_threshold_pct
    if flagged:
        reason = (
            f"usage dropped from {previous_avg:.1f} weekly logins on average "
            f"to {recent_avg:.1f} over the last {window} weeks "
            f"({trend:.1f}% change)"
        )
    else:
        reason = (
            f"usage remains stable; recent average is {recent_avg:.1f} versus "
            f"{previous_avg:.1f} in the prior period ({trend:.1f}% change)"
        )

    return {
        "account_id": account.get("account_id", "unknown"),
        "account_name": account.get("account_name", "Unknown"),
        "flagged": flagged,
        "trend_pct": trend,
        "reason": reason,
    }


def list_flagged_accounts(accounts, window=4, decline_threshold_pct=-30.0, min_history_weeks=8):
    """Return a sorted list of flagged accounts with explanation text."""
    flagged = []
    for account in accounts:
        assessment = assess_account(account, window, decline_threshold_pct, min_history_weeks)
        if assessment["flagged"]:
            flagged.append(assessment)

    flagged.sort(key=lambda entry: entry["trend_pct"])
    return flagged


def main():
    """CLI entry point for quick end-to-end evaluation against a JSON dataset."""
    parser = argparse.ArgumentParser(description="Flag churn-risk accounts from usage history.")
    parser.add_argument(
        "--input",
        type=str,
        default=str(Path(__file__).resolve().parent / "data" / "account_usage.json"),
        help="Path to the JSON file containing account usage history.",
    )
    parser.add_argument("--window", type=int, default=4, help="Lookback window in weeks.")
    parser.add_argument(
        "--threshold",
        type=float,
        default=-30.0,
        help="Percent drop threshold to flag an account as at risk.",
    )
    args = parser.parse_args()

    accounts = load_accounts(args.input)
    flagged = list_flagged_accounts(accounts, window=args.window, decline_threshold_pct=args.threshold)

    if not flagged:
        print("No accounts met the churn-risk threshold.")
        return

    print("Accounts flagged as at risk:")
    for item in flagged:
        print(f"- {item['account_id']} ({item['account_name']}): {item['reason']}")


if __name__ == "__main__":
    main()
