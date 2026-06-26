import pandas as pd
import numpy as np
from dataclasses import dataclass
from .dates import year_fraction

file = "market_data.xlsx"
vol = pd.read_excel(file, sheet_name="Volatilities")
rates = pd.read_excel(file, sheet_name="SwapPoints&Rates")

@dataclass
class Market:
    tenor: str
    start: pd.Timestamp
    expiry: pd.Timestamp
    date: pd.Timestamp
    maturity: pd.Timestamp
    FX_Spot: float
    FX_Forward: float
    pln_rate: float
    eur_rate: float
    atm: float
    rr25: float
    bf25: float
    rr10: float
    bf10: float
    delta_forward: bool
    delta_premium: bool
def load_market(file: str, tenor: str) -> Market:
    vol = pd.read_excel(file, sheet_name="Volatilities")
    rates = pd.read_excel(file, sheet_name="SwapPoints&Rates")

    vol_row = vol[vol["Tenor"] == tenor]
    rate_row = rates[rates["Tenor"] == tenor]

    if vol_row.empty:
        raise ValueError("Nie znaleziono tenoru")
    if rate_row.empty:
        raise ValueError("Nie znaleziono tenoru")

    vol_row = vol_row.iloc[0]
    rate_row = rate_row.iloc[0]

    delta_forward = vol_row["Delta type"]=="Fwd"
    
    delta_premium= vol_row["Is premium in"]=="True"
        
    spot = vol_row["FX_spot"]
    forward = spot + rate_row["Swap Points"] / 10000
    return Market(
        tenor=tenor,
        start=vol_row["Date"],
        expiry=vol_row["Expiry"],
        date=rate_row["Date"],
        maturity=rate_row["Maturity"],
        spot=spot,
        forward=forward,
        pln_rate=rate_row["PLN MM rate"],
        eur_rate=rate_row["EUR MM rate"],
        atm=vol_row["ATM"],
        rr25=vol_row["25RR"],
        bf25=vol_row["25BF"],
        rr10=vol_row["10RR"],
        bf10=vol_row["10BF"],
        delta_forward=delta_forward,
        delta_premium=delta_premium )
class MarketEngine:
    def __init__(self, market: Market):
        self.m = market
    def taus(self):
        tau_vol = year_fraction(self.m.start, self.m.expiry, 365)
        tau_pln = year_fraction(self.m.date, self.m.maturity, 365)
        tau_eur = year_fraction(self.m.date, self.m.maturity, 360)
        return tau_vol, tau_pln, tau_eur
    def rates_dfs(self, imply_pln: bool):

        tau_vol, tau_pln, tau_eur = self.taus()

        if imply_pln:
            r_eur = np.log(1 + self.m.eur_rate * tau_eur) / tau_eur
            r_pln = (np.log(self.m.forward / self.m.spot) + r_eur * tau_eur) / tau_pln
        else:
            r_pln = np.log(1 + self.m.pln_rate * tau_pln) / tau_pln
            r_eur = (np.log(self.m.forward / self.m.spot) + r_pln * tau_pln) / tau_eur

        r_d = r_pln * tau_pln / tau_vol
        r_f = r_eur * tau_eur / tau_vol

        df_d = np.exp(-r_d * tau_vol)
        df_f = np.exp(-r_f * tau_vol)

        return r_pln, r_eur, df_d, df_f
