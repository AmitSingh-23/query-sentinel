"""Privacy release gate for numeric statistics entering AI prompts with differential privacy budgeting.

Every numeric aggregate that goes into an AI-facing payload (row-count estimates, distinct counts, workload
frequencies) MUST pass through `release_aggregate`. Until differential privacy is enabled (QS_FEATURE_DP) this is
the identity function; with DP on it returns a Laplace-noised value and charges the privacy budget.
Trusted local validation (planner, HypoPG, sandbox) never uses this function and keeps exact values.
"""
from __future__ import annotations

from typing import Any


def release_aggregate(name: str, value: float | None, *, sensitivity: float = 1.0,
                      lower: float = 0.0, upper: float | None = None, scope: str = "global",
                      accountant: Any = None) -> Any:
    if value is None:
        return None
    from app import feature_flags
    if feature_flags.enabled("dp"):
        from app.dp import dp_release
        return dp_release(name, float(value), sensitivity=sensitivity, lower=lower, upper=upper, scope=scope,
                          accountant=accountant)
    return value
