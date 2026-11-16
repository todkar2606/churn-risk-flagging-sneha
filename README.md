# Churn Risk Flagging

This project implements a minimal v1 churn-risk flagging workflow for weekly login data.

## How to run

From the project root:

```bash
python starter_kit/churn_utils.py --input starter_kit/data/account_usage.json
```

Optional parameters:

- `--window` sets the comparison window (default: 4 weeks)
- `--threshold` sets the percentage drop cutoff (default: -30.0)

Example:

```bash
python starter_kit/churn_utils.py --input starter_kit/data/account_usage.json --threshold -25
```

## Output interpretation

The script evaluates each account using a four-week trend comparison:

- recent average = average of the last 4 weeks
- prior average = average of the 4 weeks before that
- percent change = ((recent - prior) / prior) * 100

An account is flagged when:

- there is at least 8 weeks of history (enough for two windows), and
- the decline is at least 30% or below the configured threshold.

This avoids false positives for brand-new accounts or accounts with very short histories.

## Known limitations

- This is intentionally simple and rule-based; it does not use seasonality or account-specific business context.
- It treats all accounts as equally likely to churn without adjusting for plan tier or customer tenure.
- For future iterations, I would add account-specific baselines, seasonality, and a richer explanatory narrative for CS outreach.
