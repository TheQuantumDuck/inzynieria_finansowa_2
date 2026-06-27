from datetime import date
from enum import IntEnum
from math import log, sqrt
from statistics import NormalDist

from dates import year_fraction
from vanilla_option import vanna_volga_cost_coefficients


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
        self, T: date, B: float, bound_type: BoundType, payment_type: PaymentType
    ) -> None:
        self.T = T
        self.B = B
        self.bound_type = bound_type
        self.payment_type = payment_type

    def price(
        self, df_d: float, df_f: float, S_t: float, sigma: float, t: date, base: int
    ) -> float:
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

    # def vanna(
    #     self, df_d: float, df_f: float, S_t: float, sigma: float, t: date, base: int
    # ) -> float:
    #     tau = year_fraction(t, self.T, base)
    #     beta = self.payment_type
    #     eta = self.bound_type
    #     B = self.B
    #     if eta * S_t <= eta * B:
    #         msg = (
    #             "To calculate vanna for digital option it must be the case that eta * S > eta * B but "
    #             f"S_t = {S_t} "
    #             f"B = {B} "
    #             f"eta = {eta}"
    #         )
    #         raise ValueError(msg)
    #     theta_p, theta_m = theta(df_d=df_d, df_f=df_f, sigma=sigma, tau=tau)
    #     varthet = vartheta(df_d=df_d, df_f=df_f, sigma=sigma, tau=tau, beta=beta)
    #     # alpha
    #     sigma2 = sigma * sigma
    #     sig_inv = 1.0 / sigma
    #     a = theta_p * theta_m
    #     b = varthet + (theta_p + theta_m) / varthet
    #     c = -1.0 / sigma2
    #     alpha_p, alpha_m = c * (a + b), c * (a - b)
    #     B_to_S = B / S_t
    #     log_B_to_S = log(B_to_S)
    #     # partial derivatives
    #     sqrt_tau = sqrt(tau)
    #     a = log_B_to_S / (sigma2 * tau)
    #     b = (theta_m * theta_p * sqrt_tau * sig_inv) / varthet
    #     dd_by_ds_p, dd_by_ds_m = b + a, b - a
    #     d_p, d_m = d(
    #         B=B, df_d=df_d, df_f=df_f, S_t=S_t, sigma=sigma, tau=tau, beta=beta
    #     )
    #     # mu
    #     mu_p = (
    #         alpha_p
    #         * NormalDist().pdf(-eta * d_p)
    #         * (-sigma - (theta_m + varthet) * log_B_to_S)
    #     )
    #     mu_m = (
    #         alpha_m
    #         * NormalDist().pdf(eta * d_m)
    #         * (-sigma - (theta_m - varthet) * log_B_to_S)
    #     )
    #     # lambda
    #     lam_p = (
    #         -eta
    #         * (NormalDist().pdf(d_p) / sqrt_tau)
    #         * (d_m * dd_by_ds_p + alpha_p * log_B_to_S + sig_inv)
    #     )
    #     lam_m = (
    #         -eta
    #         * (NormalDist().pdf(d_m) / sqrt_tau)
    #         * (d_m * dd_by_ds_m - alpha_m * log_B_to_S - sig_inv)
    #     )
    #     # nu
    #     nu_p, nu_m = mu_p + lam_p, mu_m + lam_m
    #     exp_1 = (theta_m + varthet) * sig_inv
    #     exp_2 = (theta_m - varthet) * sig_inv
    #     return (
    #         (df_d**beta)
    #         * ((B_to_S**exp_1) * nu_p + (B_to_S**exp_2) * nu_m)
    #         / (sigma * S_t)
    #     )

    def vanna(
        self, df_d: float, df_f: float, S_t: float, sigma: float, t: date, base: int
    ) -> float:
        h_s = 6e-6 * max(abs(S_t), 1.0)
        h_v = 6e-6 * max(abs(sigma), 1.0)

        def p(S: float, v: float):
            return self.price(df_d=df_d, df_f=df_f, S_t=S, sigma=v, t=t, base=base)

        return (
            p(S_t + h_s, sigma + h_v)
            - p(S_t + h_s, sigma - h_v)
            - p(S_t - h_s, sigma + h_v)
            + p(S_t - h_s, sigma - h_v)
        ) / (4.0 * h_s * h_v)

    def volga(
        self, df_d: float, df_f: float, S_t: float, sigma: float, t: date, base: int
    ) -> float:
        h_v = 1e-4 * max(abs(sigma), 1.0)

        def p(v: float) -> float:
            return self.price(df_d=df_d, df_f=df_f, S_t=S_t, sigma=v, t=t, base=base)

        return (p(sigma + h_v) - 2.0 * p(sigma) + p(sigma - h_v)) / (h_v * h_v)

    def vanna_volga_price(
        self,
        df_d: float,
        df_f: float,
        p: float,
        S_t: float,
        sigma_atm: float,
        sigma_25C: float,
        sigma_25P: float,
        t: date,
        delta_forward: bool,
        delta_premium: bool,
        base: int,
    ) -> float:
        T = self.T
        c_1, c_2 = vanna_volga_cost_coefficients(
            df_d=df_d,
            df_f=df_f,
            S_t=S_t,
            sigma_atm=sigma_atm,
            sigma_25C=sigma_25C,
            sigma_25P=sigma_25P,
            t=t,
            T=T,
            delta_forward=delta_forward,
            delta_premium=delta_premium,
            base=base,
        )
        vanna = self.vanna(
            df_d=df_d, df_f=df_f, S_t=S_t, sigma=sigma_atm, t=t, base=base
        )
        volga = self.volga(
            df_d=df_d, df_f=df_f, S_t=S_t, sigma=sigma_atm, t=t, base=base
        )
        V_BS = self.price(
            df_d=df_d, df_f=df_f, S_t=S_t, sigma=sigma_atm, t=t, base=base
        )
        return V_BS + p * (c_1 * vanna + c_2 * volga)


class NoTouchBlackScholes:
    def __init__(
        self,
        T: date,
        K: float,
        bound_type: BoundType,
    ) -> None:
        self.T = T
        self.B = K
        self.bound_type = bound_type

    def price(
        self, df_d: float, df_f: float, S_t: float, sigma: float, t: date, base: int
    ) -> float:
        T = self.T
        V_OT = OneTouchBlackScholes(
            T=T,
            B=self.B,
            bound_type=self.bound_type,
            payment_type=PaymentType.AT_MATURITY,
        ).price(df_d=df_d, df_f=df_f, S_t=S_t, sigma=sigma, t=t, base=base)
        return df_d - V_OT

    def vanna_volga_price(
        self,
        df_d: float,
        df_f: float,
        p: float,
        S_t: float,
        sigma_atm: float,
        sigma_25C: float,
        sigma_25P: float,
        t: date,
        delta_forward: bool,
        delta_premium: bool,
        base: int,
    ) -> float:
        V_OT = OneTouchBlackScholes(
            T=self.T,
            B=self.B,
            bound_type=self.bound_type,
            payment_type=PaymentType.AT_MATURITY,
        ).vanna_volga_price(
            df_d=df_d,
            df_f=df_f,
            p=p,
            S_t=S_t,
            sigma_atm=sigma_atm,
            sigma_25C=sigma_25C,
            sigma_25P=sigma_25P,
            t=t,
            delta_forward=delta_forward,
            delta_premium=delta_premium,
            base=base,
        )
        return df_d - V_OT
