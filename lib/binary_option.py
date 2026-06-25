from datetime import date
from statistics import NormalDist

from .dates import year_fraction
from .vanilla_option import OptionType, VanillaOptionBlackSholes, d


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
        dK: float,
    ) -> float:
        T = self.T
        K = self.K
        if self.type == OptionType.CALL:
            K_b, K_s = K - dK, K + dK
        else:
            K_b, K_s = K + dK, K - dK
        option_buy = VanillaOptionBlackSholes(T=T, K=K_b, option_type=self.type)
        option_sell = VanillaOptionBlackSholes(T=T, K=K_s, option_type=self.type)
        buy_price = option_buy.vanna_volga_price(
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
        sell_price = option_sell.vanna_volga_price(
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
        return (buy_price - sell_price) / (2 * dK)


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
        dK: float,
    ) -> float:
        T = self.T
        K = self.K
        vanilla = VanillaOptionBlackSholes(T=T, K=K, option_type=self.type)
        con = CoNBlackScholes(T=T, K=K, option_type=self.type)
        vanilla_price = vanilla.vanna_volga_price(
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
        con_price = con.vanna_volga_price(
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
            dK=dK,
        )
        omega = self.type
        return omega * vanilla_price + K * con_price
