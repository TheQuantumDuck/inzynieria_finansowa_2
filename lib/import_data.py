import pandas as pd
import numpy as np
from .dates import year_fraction

file = "market_data.xlsx"
vol = pd.read_excel(file, sheet_name="Volatilities")
rates = pd.read_excel(file, sheet_name="SwapPoints&Rates")

def clean_columns(df):
    df.columns = (
    df.columns.astype(str)
        .str.strip()
        .str.replace(" ", "_")
        .str.replace("%", "pct")
    )
    return df
vol_names = clean_columns(vol_raw)
rates_names = clean_columns(rates_raw)

print("Dostępne Tenory")
print(vol['Tenor'].to_string(index=False))
choice = input("Wybierz tenor:")

def get_market_data(tenor, vol, rates):
    vol_row = vol[vol["Tenor"] == tenor]
    rate_row = rates[rates["Tenor"] == tenor]
    if vol_row.empty:
        raise ValueError("Nie znaleziono tenoru")
    if rate_row.empty:
        raise ValueError("Nie znaleziono tenoru")
        
    vol_row = vol_row.iloc[0]
    rate_row = rate_row.iloc[0]
    if vol_row["Delta type"]=="Fwd": delta_forward=True
    else: delta_forward=False
    if vol_row["Is premium in"]=="True": delta_premium=True
    else: delta_premium=False
    
    data = {
        "tenor": vol_row["Tenor"],
        "Start": vol_row["Date"],
        "End": vol_row["Expiry"],
        "Date": rate_row["Date"],
        "Maturity": rate_rov["Maturity"],
        "sigma_ATM": vol_row["ATM"],
        "sigma_25RR": vol_row["25RR"],
        "sigma_10RR": vol_row["10RR"],
        "sigma_25BF": vol_row["25BF"],
        "sigma_10BF": vol_row["10BF"],
        "delta_forward": delta_forward,
        "delta_premium": delta_premium,
        "FX_Spot": vol_row["FX_spot"],
        "FX_Forward":vol_row["FX_spot"]+rate_row["Swap Points"]/10000,
        "PLN_rate": rate_row["PLN MM rate"],
        "EUR_rate": rate_row["EUR MM rate"],
        "SwapPoints": rate_row["Swap Points"]
    } 
    return data
def get_rates(market, imply_PLN: bool):
    tau_vol=year_fraction(market["Start"], market["End"], 365)
    tau_PLN=year_fraction(market["Date"], market["Maturity"], 365)
    tau_EUR=year_fraction(market["Date"], market["Maturity"], 360)
    if imply_PLN==True: 
        r_EUR=np.log(1+market["EUR_rate"]*tau_EUR)/tau_EUR
        r_PLN=(np.log(market["FX_Forward"]/market["FX_Spot"])+r_EUR*tau_EUR)/tau_PLN
    else:
        r_PLN=np.log(1+market["PLN_rate"]*tau_PLN)/tau_PLN
        r_EUR=(np.log(market["FX_Forward"]/market["FX_Spot"])+r_PLN*tau_PLN)/tau_EUR
    r_d=r_PLN*tau_PLN/tau_vol
    r_f=r_EUR*tau_EUR/tau_vol  
    return(r_d,r_f)
