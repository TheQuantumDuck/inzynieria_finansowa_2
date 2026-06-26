from datetime import date
from enum import IntEnum
from math import log, sqrt
from statistics import NormalDist

from dates import year_fraction


def theta(df_d: float, df_f: float, sigma: float, tau: float) -> tuple[float, float]:
    r_d_minus_r_f = -(1 / tau) * log(df_d / df_f)
    a = r_d_minus_r_f / sigma
    b = 0.5 * sigma
    return a + b, a - b


class PaymentType(IntEnum):
    AT_TOUCH = 0
    AT_MATURITY = 1


class BoundType(IntEnum):
    LOWER_BOUND = 1
    UPPER_BOUND = -1


def vartheta(
    df_d: float, df_f: float, sigma: float, tau: float, beta: PaymentType
) -> float:
    _, theta_minus = theta(
        df_d=df_d,
        df_f=df_f,
        sigma=sigma,
        tau=tau,
    )
    if beta == PaymentType.AT_MATURITY:
        return abs(theta_minus)
    theta_minus2 = theta_minus * theta_minus
    r_d = -log(df_d) / tau
    return sqrt(theta_minus2 + 2 * r_d)


def d(
    B: float,
    df_d: float,
    df_f: float,
    S_t: float,
    sigma: float,
    tau: float,
    beta: PaymentType,
) -> tuple[float, float]:
    varthet = vartheta(df_d=df_d, df_f=df_f, sigma=sigma, tau=tau, beta=beta)
    a = log(S_t / B)
    b = sigma * varthet * tau
    c = sigma * sqrt(tau)
    return (a - b) / c, (-a - b) / c


class OneTouchBlackScholes:
    def __init__(
        self, T: date, K: float, bound_type: BoundType, payment_type: PaymentType
    ) -> None:
        self.T = T
        self.B = K
        self.bound_type = bound_type
        self.payment_type = payment_type

    def price(
        self, df_d: float, df_f: float, S_t: float, sigma: float, t: date, base: int
    ):
        tau = year_fraction(t, self.T, base)
        beta = self.payment_type
        B = self.B
        eta = self.bound_type
        B_to_S = B / S_t
        d_p, d_m = d(
            B=B, df_d=df_d, df_f=df_f, S_t=S_t, sigma=sigma, tau=tau, beta=beta
        )
        _, theta_m = theta(df_d=df_d, df_f=df_f, sigma=sigma, tau=tau)
        varthet = vartheta(df_d=df_d, df_f=df_f, sigma=sigma, tau=tau, beta=beta)
        exp_1 = (theta_m + varthet) / sigma
        exp_2 = (theta_m - varthet) / sigma
        return (df_d**beta) * (
            (B_to_S**exp_1) * NormalDist().cdf(-eta * d_p)
            + (B_to_S**exp_2) * NormalDist().cdf(eta * d_m)
        )
