#!/usr/bin/env python3
"""
Longstaff-Schwartz Monte Carlo pricer for American put options.
Supports base and stress volatility scenarios.
"""

import numpy as np
from typing import Tuple, Optional


def lsm_american_put(
    S0: float,
    K: float,
    T: float,
    r: float = 0.05,
    sigma: float = 1.10,
    n_paths: int = 50000,
    n_steps: int = 50,
    seed: Optional[int] = None,
) -> float:
    """
    Price an American put option using Longstaff-Schwartz least-squares Monte Carlo.

    Args:
        S0: Current stock price
        K: Strike price
        T: Time to maturity in years
        r: Risk-free rate
        sigma: Volatility
        n_paths: Number of simulation paths
        n_steps: Number of time steps
        seed: Random seed for reproducibility

    Returns:
        Option price (present value)
    """
    if seed is not None:
        np.random.seed(seed)

    dt = T / n_steps
    discount = np.exp(-r * dt)

    # Simulate paths
    Z = np.random.randn(n_paths, n_steps)
    S = np.zeros((n_paths, n_steps + 1))
    S[:, 0] = S0

    for t in range(1, n_steps + 1):
        S[:, t] = S[:, t - 1] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z[:, t - 1])

    # Payoff at each time step
    payoff = np.maximum(K - S, 0)

    # Continuation value regression
    V = payoff[:, -1].copy()

    for t in range(n_steps - 1, 0, -1):
        itm = payoff[:, t] > 0
        if np.sum(itm) < 2:
            V = V * discount
            continue

        # Basis functions: 1, S, S^2
        S_itm = S[itm, t]
        A = np.vstack([np.ones_like(S_itm), S_itm, S_itm**2]).T
        coeffs = np.linalg.lstsq(A, V[itm] * discount, rcond=None)[0]
        continuation = np.dot(A, coeffs)

        exercise = payoff[itm, t]
        exercise_mask = exercise > continuation
        V[itm] = np.where(exercise_mask, exercise, V[itm] * discount)
        V[~itm] = V[~itm] * discount

    V = V * discount
    return float(np.mean(V))


def price_put_lsm(
    spot: float,
    strike: float,
    days_to_exp: int = 25,
    r: float = 0.05,
    sigma_base: float = 1.10,
    sigma_stress: float = 1.40,
) -> Tuple[float, float]:
    """
    Convenience wrapper that returns (base_price, stress_price).
    """
    T = days_to_exp / 365.0
    base = lsm_american_put(spot, strike, T, r, sigma_base, seed=42)
    stress = lsm_american_put(spot, strike, T, r, sigma_stress, seed=42)
    return base, stress


if __name__ == "__main__":
    # Example usage
    spot = 69.70
    strike = 64.1
    base, stress = price_put_lsm(spot, strike)
    print(f"Spot: {spot}, Strike: {strike}")
    print(f"Base price: {base:.2f}, Stress price: {stress:.2f}")
