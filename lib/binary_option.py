from datetime import date
from statistics import NormalDist

from .dates import year_fraction
from .vanilla_option import OptionType, d


class AoNBlackScholes:
    def __init__(self, T: date, K: float, option_type: OptionType) -> None:
        self.T = T
        self.K = K
        self.type = option_type

    def price(
        self, df_d: float, df_f: float, S_t: float, sigma: float, t: date, base: int
    ):
        K = self.K
        tau = year_fraction(t, self.T, base)
        d_1, _ = d(
            K=K,
            df_d=df_d,
            df_f=df_f,
            S_t=S_t,
            sigma=sigma,
            tau=tau,
        )
        omega = self.type
        aon = df_f * S_t * NormalDist().cdf(omega * d_1)
        return aon


class CoNBlackScholes:
    def __init__(self, T: date, K: float, option_type: OptionType) -> None:
        self.T = T
        self.K = K
        self.type = option_type

    def price(
        self, df_d: float, df_f: float, S_t: float, sigma: float, t: date, base: int
    ):
        K = self.K
        tau = year_fraction(t, self.T, base)
        _, d_2 = d(
            K=K,
            df_d=df_d,
            df_f=df_f,
            S_t=S_t,
            sigma=sigma,
            tau=tau,
        )
        omega = self.type
        con = df_d * K * NormalDist().cdf(omega * d_2)
        return con
