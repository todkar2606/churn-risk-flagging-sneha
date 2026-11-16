# Churn Risk Flagging — Solution Design

## Problem restatement

Vantage Retail Systems has a churn problem: accounts are only recognized as at risk after they announce they are not renewing. The goal is to detect accounts whose weekly login behavior is declining before that happens, so Customer Success can intervene early.

## Assumptions

I made four practical assumptions for a v1 product:

1. We only need a simple, explainable rule-based model at first. This is better than a complex model when the business problem is not yet fully specified.
2. A meaningful trend requires at least two comparison periods. In practice, that means at least 8 weeks of history for a 4-week window.
3. A customer is "at risk" when recent usage drops materially versus the previous period, not merely when usage is low in absolute terms. A decline of ~30% or more over the last month is a strong signal.
4. Very new accounts should not be flagged simply because they are small or still ramping up. We should treat them as "insufficient history" until enough data exists.

## Proposed approach

For each account, I compute the average weekly logins over the most recent 4 weeks and compare it to the average over the preceding 4 weeks:

- recent_avg = mean(last 4 weeks)
- prior_avg = mean(previous 4 weeks)
- trend_pct = ((recent_avg - prior_avg) / prior_avg) * 100

I flag an account when:

- the account has at least 8 weeks of history, and
- the trend is at or below a threshold such as -30%.

This is simple, transparent, and easy for the CS team to trust. It also works well with the available dataset because the sharply declining accounts stand out clearly while stable accounts do not.

## Trade-offs considered

I considered a more complex model using moving averages, change-point detection, or customer-specific baselines. Those approaches can be valuable, but they require more domain data and create more opaque reasoning. For a first pass, explicit threshold logic is easier to explain and defend in a customer conversation.

I also considered flagging anyone with a weak downward trend. That would create too many false alarms and reduce trust. The minimum-history rule and a relatively strong decline threshold make the signal more actionable.

## Why this works for the data

The provided dataset includes several accounts with obviously strong declines and others that are stable or growing. The rule identifies the severe drop-offs without flagging the newly created or short-lived accounts. This makes it useful for early outreach, while remaining conservative enough to avoid noisy false positives.

## Future work

With more time and better data, I would expand the model in several ways:

- add plan-tier and tenure-aware baselines
- account for seasonality and promotion cycles
- include a "confidence" score for each flag
- generate one-line explanations for Customer Success reps, such as "Logins fell 60% in the last month after several months of steady usage"

This would make the system more accurate and more operationally useful, but the current approach is a strong v1 that is easy to reason about and explain.
