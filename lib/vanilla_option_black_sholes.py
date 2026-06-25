from datetime import date
from enum import IntEnum
from math import exp, log, sqrt
from statistics import NormalDist

from dates import year_fraction


def d(
    K: float,
    df_d: float,
    df_f: float,
    S_t: float,
    sigma: float,
    tau: float,
) -> tuple[float, float]:
    a = log(S_t / K) + log(df_f / df_d) + 0.5 * sigma * sigma * tau
    b = sigma * sqrt(tau)
    d_1 = a / b
    d_2 = d_1 - b
    return (d_1, d_2)


class OptionType(IntEnum):
    CALL = 1
    PUT = -1


class VanillaOptionBlackSholes:
    def __init__(self, T: date, K: float, option_type: OptionType) -> None:
        self.T = T
        self.K = K
        self.type = option_type

    def price(
        self, df_d: float, df_f: float, S_t: float, sigma: float, t: date, base: int
    ) -> float:
        K = self.K
        tau = year_fraction(t, self.T, base)
        d_1, d_2 = d(
            K=K,
            df_d=df_d,
            df_f=df_f,
            S_t=S_t,
            sigma=sigma,
            tau=tau,
        )
        omega = self.type
        a = df_f * S_t * NormalDist().cdf(omega * d_1)
        b = df_d * K * NormalDist().cdf(omega * d_2)
        return omega * (a - b)

    def vanna_volga(
        self, df_d: float, df_f: float, S_t: float, sigma: float, t: date, base: int
    ) -> tuple[float, float]:
        K = self.K
        tau = year_fraction(t, self.T, base)
        d1, d2 = d(
            K=K,
            df_d=df_d,
            df_f=df_f,
            S_t=S_t,
            sigma=sigma,
            tau=tau,
        )
        vanna = -df_f * NormalDist().pdf(d1) * sqrt(tau) * d2 / sigma
        return (
            vanna,
            -S_t * vanna * d1,
        )


def strike_for_delta(
    delta: float,
    option_type: OptionType,
    df_d: float,
    df_f: float,
    S_t: float,
    sigma: float,
    t: date,
    T: date,
    base: int,
    forward: bool = False,
    premium: bool = False,
    tol: float = 1e-9,
    max_iter: int = 100,
) -> float:
    tau = year_fraction(t, T, base)
    F = S_t * df_f / df_d
    sigma2 = sigma * sigma
    a = 0.5 * sigma2 * tau
    b = sigma * sqrt(tau)
    if forward:
        d_1 = option_type * NormalDist().inv_cdf(option_type * delta)
    else:
        d_1 = option_type * NormalDist().inv_cdf(option_type * delta / df_f)
    K_0 = F * exp(a - b * d_1)
    if premium:
        for _ in range(max_iter):
            u = (
                option_type * delta * F / K_0
                if forward
                else option_type * delta * S_t / (K_0 * df_d)
            )
            d_2 = option_type * NormalDist().inv_cdf(u)
            K = F * exp(-a - b * d_2)
            err = abs(K_0 - K) / K_0
            K_0 = K
            if err < tol:
                return K_0
    else:
        return K_0
    msg = "max_iter reached without convergence"
    raise ValueError(msg)
